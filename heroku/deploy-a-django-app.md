# Deploy a Django app to Heroku

This guide provides instructions on deploying a Django app to Heroku, DataMade's
preferred platform for hosting dynamic applications.

## Contents

- [Set up application code for Heroku](#set-up-application-code-for-heroku)
  - [Containerize your app](#containerize-your-app)
  - [Serve static files with WhiteNoise](#serve-static-files-with-whitenoise)
  - [Read settings and secret variables from the environment](#read-settings-and-secret-variables-from-the-environment)
  - [Configure Django logging](#configure-django-logging)
- [Provision Heroku resources](#provision-heroku-resources)
  - [Ensure that the Heroku CLI is installed](#ensure-that-the-heroku-cli-is-installed)
  - [Create Heroku config files](#create-heroku-config-files)
    - [`heroku.yml`](#herokuyml)
    - [`release.sh`](#releasesh)
    - [`app.json`](#appjson)
  - [Create apps and pipelines for your project](#create-apps-and-pipelines-for-your-project)
- [Set up Slack notifications](#set-up-slack-notifications)
- [Enable additional services](#enable-additional-services)
  - [Solr](#solr)
  - [PostGIS](#postgis)
- [Set up a custom domain](#set-up-a-custom-domain)
  - [Step 1: Configure a custom domain on Heroku](#step-1-configure-a-custom-domain-on-heroku)
  - [Step 2: Configure a custom domain on a DNS provider](#step-2-configure-a-custom-domain-on-a-dns-provider)
  - [Step 3: Enable SSL](#step-3-enable-ssl)
  - [General guidelines for custom domains](#general-guidelines-for-custom-domains)
- [Troubleshooting](#troubleshooting)

## Set up application code for Heroku

In order to deploy a Django application to Heroku, a few specific configurations
need to be enabled in your application code. We provide details on these
configurations below.

### Containerize your app

We use Heroku as a platform for deploying containerized apps, which means that
your app must be containerized in order to use Heroku properly. If your app
is not yet containerized, [follow our instructions for containerizing Django
apps](/docker/local-development.md) before moving on.

There are two commands you should make sure to add to your Dockerfile in order to
properly deploy with Heroku:

1. In the section of your Dockerfile where you install OS-level dependencies with `apt-get`,
   make sure to install `curl` so that Heroku can stream logs during releases (if you're
   inheriting from the official `python` images, `curl` will already be installed by default)
2. Toward the end of your Dockerfile, run `python manage.py collecstatic --noinput` so that
   static files will be baked into your container on deployment

For an example of a Django Dockerfile that is properly set up for Heroku, see
the [Minnesota Election Archive project](https://github.com/datamade/mn-election-archive/blob/master/Dockerfile).

### Serve static files with WhiteNoise

Apps deployed on Heroku don't typically use Nginx to serve content, so they need some
other way of serving static files. Since our apps tend to have relatively low traffic,
we prefer configuring [WhiteNoise](http://whitenoise.evans.io/)
to allow Django to serve static files in production.

Follow the [setup instructions for WhiteNoise in
Django](http://whitenoise.evans.io/en/stable/django.html) to ensure that your
Django apps can serve static files.

In order to be able to serve static files when `DEBUG` is `False`, you'll also want
to make sure that `RUN python manage.py collectstatic` is included as a step in your
Dockerfile. This will ensure that the static files are baked into the container.
Since we typically mount application code into the container during local development,
you'll also need to make sure that your static files are stored outside of the root
project folder so that the mounted files don't overwrite them. One easy way to do this
is to set `STATIC_ROOT = '/static'` in your `settings.py` file.

### Read settings and secret variables from the environment

Heroku doesn't allow us to decrypt content with GPG, so we can't use Blackbox
to decrypt application secrets. Instead, we can store these secrets as [config
vars](https://devcenter.heroku.com/articles/config-vars), which Heroku will thread
into our container environment.

The three most basic config vars that you'll want to set for every app include
the Django `DEBUG`, `SECRET_KEY`, and `ALLOWED_HOSTS` variables. Update `settings.py`
to read these variables from the environment:

```python
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
DEBUG = False if os.getenv('DJANGO_DEBUG', True) == 'False' else True
allowed_hosts = os.getenv('DJANGO_ALLOWED_HOSTS', [])
ALLOWED_HOSTS = allowed_hosts.split(',') if allowed_hosts else []
```

Make sure to update your app service in `docker-compose.yml` to thread any variables
that don't have defaults into your local environment:

```yml
services:
  app:
    environment:
      - DJANGO_SECRET_KEY=really-super-secret
```

For a full example of this pattern in a production app, see the [Docker Compose
file](https://github.com/datamade/mn-election-archive/blob/master/docker-compose.yml)
and [Django settings
file](https://github.com/datamade/mn-election-archive/blob/master/elections/settings.py)
in the [UofM Election Archive project](https://github.com/datamade/mn-election-archive).

### Configure Django logging

When Gunicorn is running our app on Heroku, we generally want it to log to stdout
and stderr instead of logging to files, so that we can let Heroku capture the logs
and see view them with the `heroku logs` CLI command (or in the web console).

By default, Django will not log errors to the console when `DEBUG` is `False`
([as documented here](https://docs.djangoproject.com/en/2.2/topics/logging/#django-s-default-logging-configuration)).
To make sure that errors get logged appropriately in Heroku, set the following
baseline logging settings in your `settings.py` file:

```python
import os

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # Preserve default loggers
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}
```

For more detail on Django's logging framework, [see the documentation](https://docs.djangoproject.com/en/2.2/topics/logging/).

## Provision Heroku resources

Once your application is properly configured for Heroku, the following instructions
will help you deploy your application to the platform.

### Ensure that the Heroku CLI is installed

The fastest way to get a project up and running on Heroku is to use the
[Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli). Before you start,
make sure you have the CLI installed locally. In addition, confirm that you have the
manifest plugin) installed:

```
heroku plugins | grep manifest
```

If you don't see any output, [follow the official instructions for installing the
plugin](https://devcenter.heroku.com/changelog-items/1441).

### Create Heroku config files

Define config files relative to the root of your repo.

#### `heroku.yml`

The `heroku.yml` manifest file tells Heroku how to build and network the services
and containers that comprise your application. This file should live in the root of your project repo.
For background and syntax, see [the
documentation](https://devcenter.heroku.com/articles/build-docker-images-heroku-yml).
Use the following baseline to get started:

```yml
# Define addons that you need for  your project, such as Postgres, Redis, or Solr.
setup:
  addons:
    - plan: heroku-postgresql
# Define your application's Docker containers.
build:
  docker:
    web: Dockerfile
# Define any scripts that you'd like to run every time the app deploys.
release:
  command:
    - ./scripts/release.sh
  image: web
# The command that runs your application. Replace 'app' with the name of your app.
run:
  web: gunicorn -t 180 --log-level debug app.wsgi:application
```

#### `release.sh`

In your app's `scripts` folder, define a script `release.sh` to run every time the app deploys.
Use the following baseline script and make sure to run `chmod u+x scripts/release.sh`
to make it executable:

```bash
#!/bin/bash
python manage.py collectstatic --noinput
python manage.py migrate --noinput
```

If your app uses a `dbload` script to load initial data into the database, you can use `release.sh`
to check if the initial data exists and run the data loading scripts if not. For example:

```bash
# Set ${TABLE} to the name of a table that you expect to have data in it.
if [ `psql ${DATABASE_URL} -tAX -c "SELECT COUNT(*) FROM ${TABLE}"` -eq "0" ]; then
    make all
fi
```

Note that logs for the release phase won't be viewable in the Heroku console unless `curl`
is installed in your application container. Make sure your Dockerfile installs
`curl` to see logs as `scripts/release.sh` runs.

#### `app.json`

In order to enable [review apps](https://devcenter.heroku.com/articles/github-integration-review-apps)
for your project, the repo must contain an `app.json` config file in the root directory.
For background and syntax, see [the documentation](https://devcenter.heroku.com/articles/app-json-schema).
Use the following baseline to get started:

```json
{
  "name": "your-app",
  "description": "Short description of your app.",
  "scripts": {},
  "env": {
    "DJANGO_SECRET_KEY": {
      "required": true
    },
    "DJANGO_ALLOWED_HOSTS": {
      "required": true
    }
  },
  "formation": {
    "web": {
      "quantity": 1,
      "size": "hobby"
    }
  },
  "addons": [
    "heroku-postgresql"
  ],
  "environments": {
    "review": {
      "addons": ["heroku-postgresql:hobby-basic"]
    }
  },
  "buildpacks": [],
  "stack": "container"
}
```

### Create apps and pipelines for your project

In order to deploy your project, you need to create Heroku apps for staging
and production, and tie them together in a [pipeline](https://devcenter.heroku.com/articles/pipelines).
To create these resources, start by defining the name of your app:

```bash
# This should be the same slug as your project's GitHub repo.
export APP_NAME=<your-app-name-here>
```

Then, run the following Heroku CLI commands to create a staging app and a pipeline:

```bash
heroku create ${APP_NAME}-staging -t datamade --manifest
heroku pipelines:create -t datamade ${APP_NAME} -a ${APP_NAME}-staging -s staging
heroku pipelines:connect ${APP_NAME} -r datamade/${APP_NAME}
heroku reviewapps:enable -a ${APP_NAME}-staging -p ${APP_NAME}
```

If you would like to set up a production app as well, run the following commands
to create one and add it to your pipeline:

```bash
heroku create ${APP_NAME} -t datamade --manifest
heroku pipelines:add ${APP_NAME} -a ${APP_NAME} -s production
```

Once you have the environments you need, enable [review
apps](https://devcenter.heroku.com/articles/github-integration-review-apps)
for your pipeline:

```bash
# If you only have a staging app, change the value of the -a flag to ${APP_NAME}-staging
# to set the staging app as the parent app for all review apps.
heroku reviewapps:enable -p ${APP_NAME} -a ${APP_NAME}
```

Next, configure environment variables for staging, production, and review apps. These can be set
using either the dashboard or the CLI. [Follow the Heroku
documentation](https://devcenter.heroku.com/articles/config-vars#managing-config-vars)
to set up your config vars. Note that you need to define config vars for each environment
in your application: for staging and production environments, you can define these
variables under `Settings > Config Vars` on the application page, but since review apps
don't have an application page until they're created, you can define config vars
that will be inherited by each review app by navigating to the pipeline home page
and visiting `Settings > Review Apps > Review app config vars` in the nav.

If you followed the setup instructions in "[Read settings and secret variables from the
environment](#read-settings-and-secret-variables-from-the-environment)" above,
you should need to set at least the following variables:

- `DJANGO_SECRET_KEY`: This needs to be a random string, unique to each environment.
  We often use the [XKCD password generator](https://preshing.com/20110811/xkcd-password-generator/)
  to generate random strings.
- `DJANGO_ALLOWED_HOSTS`: This variable should be a comma-separated list of hostnames
  that are valid for your application. For review apps and the staging environment,
  you can set this to `.herokuapp.com` to automatically safelist any subdomains
  of the `herokuapp.com` root domain.

Note that while `DATABASE_URL` is probably required by your application, you don't actually
need to set it yourself. The Heroku Postgres add-on will [automatically define this
variable](https://devcenter.heroku.com/articles/heroku-postgresql#designating-a-primary-database)
when it provisions a database for your application.

After your config vars are set up, configure the GitHub integration to set up [automatic
deploys](https://devcenter.heroku.com/articles/github-integration#automatic-deploys)
for both Heroku apps (staging and production). Ideally we would choose
"Wait for CI to pass before deploy" for each app, but in our experience so far it will
prevent Heroku from automatically creating new review apps for each new PR, so for now
we recommend leaving it off. We have an open ticket with Heroku support and will update
this recommendation in the future if the situation changes.

Heroku needs to deploy from specific branches in order to deploy to different environments
(e.g. staging vs. production). In order to properly enable automatic deployments, then,
you'll need to deploy to production from a branch instead of tagged commits (a practice
which we've used in the past for deploying to production). We recommend creating a long-lived
`deploy` branch off of `master` immediately after setting up your repo so that you can
use `master` to deploy to staging and `deploy` to deploy to production.

## Set up Slack notifications

Heroku can send build notifications to Slack via the Heroku ChatOps integration.
This integration should already be set up in our Slack channel, but if you need
to install it again, see the [official documentation](https://devcenter.heroku.com/articles/chatops).

To enable notifications for an app, run the following Slack command in the
corresponding channel:

```bash
/h route ${PIPELINE_NAME} to ${CHANNEL_NAME}
```

For example, to enable notifications for the `parserator` pipeline in the `#parserator`
channel, we would run `/h route parserator to #parserator`.

## Enable additional services

If your app requires additional services, like Solr or PostGIS, you'll need
to perform some extra steps to set them up for your pipeline.

### Solr

Solr can be configured as a separate service using the [Websolr
add-on for Heroku](https://devcenter.heroku.com/articles/websolr). We recommend
following the instructions for configuring [Websolr with
Haystack](https://devcenter.heroku.com/articles/websolr#haystack-for-django).
In addition to following these instructions, complete the following two steps:

1. Update your `heroku.yml` and `app.json` config files to add `websolr` to your
   add-ons configuration attributes, so Websolr will be enabled for review apps
2. Define `WEBSOLR_URL` as an environment variable for your `app`
   service in your `docker-compose.yml` file in order to point your app to your
   Solr service in local development

For help setting up Haystack for local development, see [our guide to
Haystack](https://github.com/datamade/how-to/blob/master/search/03-heavyweight.md#getting-started).
For an example of a working Solr installation in a Heroku app, see the [`2.5_deploy`
branch of LA Metro Councilmatic](https://github.com/datamade/la-metro-councilmatic/tree/2.5_deploy).

Note that the Websolr add-on [can be expensive](https://elements.heroku.com/addons/websolr#pricing),
with staging instances costing a minimum of $20/mo and the smallest production
instance costing $60/mo. Refer to our [guide to searching
data](https://github.com/datamade/how-to/blob/master/search/03-heavyweight.md#heavyweight)
to make sure you really need Solr before going forward with installing it on your project.

### PostGIS

If your app requires PostGIS, you'll need to [manually enable it in your
database](https://devcenter.heroku.com/articles/postgis). Once your database
has been provisioned, run the following command to connect to your database and
enable PostGIS:

```
heroku psql -a <YOUR_APP> -c "CREATE EXTENSION postgis"
```

To automate this process, you can include a step like this in `scripts/release.sh`
to make sure PostGIS is always enabled in your databases:

```bash
psql ${DATABASE_URL} -c "CREATE EXTENSION IF NOT EXISTS postgis"
```

## Set up a custom domain

All Heroku apps are automatically delegated a subdomain under the `heroku.com`
root domain, like `example.heroku.com`. This automatic Heroku subdomain
is usually fine for review apps and staging apps, but production apps almost
always require a dedicated custom domain like `example.com`.

When you're ready to deploy to production and publish your app publicly, you'll
need to set up a custom domain. In order to do this, you need to register the custom
domain in two places: in the Heroku dashboard, and in your (or your client's) DNS provider.
Then, you'll need to instruct Heroku to enable SSL for your domain.

For detailed documentation on setting up custom domains, see the [Heroku
docs](https://devcenter.heroku.com/articles/custom-domains).

### Step 1: Configure a custom domain on Heroku

The first step to setting up a custom domain is to instruct Heroku to use the
domain for your app. Navigate to `Settings > Domains` in your app dashboard, choose
`Add domain`, and enter the name of the custom domain you would like to use.

When you save the domain, Heroku should display the DNS target for your domain.
Copy this string and use it in the next step to delegate the domain with your
DNS provider.

### Step 2: Configure a custom domain on a DNS provider

_Note: If you're not comfortable with basic DNS terminology and you're finding this
section to be confusing, refer to the CloudFlare docs on [how DNS
works](https://www.cloudflare.com/learning/dns/what-is-dns/)._

Once you have a DNS target for Heroku, you need to instruct your DNS provider to
direct traffic for your custom domain to Heroku.

If you're setting up a custom **subdomain**, like `www.example.com` or `app.example.com`,
you'll need to create a `CNAME` record pointing to your DNS target with your DNS
provider. For more details, see the Heroku docs on [configuring DNS for
subdomains](https://devcenter.heroku.com/articles/custom-domains#configuring-dns-for-subdomains).

If you're setting up a custom **root domain**, like `example.com`, you'll need
to create the equivalent of an `ALIAS` record with your DNS provider. Not all
DNS providers offer the same type of `ALIAS` record, so to provision this record
you should visit the Heroku docs on [configuring DNS for root
domains](https://devcenter.heroku.com/articles/custom-domains#configuring-dns-for-root-domains)
and follow the instruction for your provider. At DataMade we typically use Namecheap,
which allows you to [create `ALIAS`
records](https://www.namecheap.com/support/knowledgebase/article.aspx/10128/2237/how-to-create-an-alias-record).

After creating the appropriate DNS record with your DNS provider, wait a few
minutes for DNS to propagate and confirm that you can load your app by visiting
your custom domain. Remember that Django will only serve domains that are listed
in its `ALLOWED_HOSTS` settings variable, so you may have to update your `DJANGO_ALLOWED_HOSTS`
config var on Heroku to accomodate your custom domain.

### Step 3: Enable SSL

Once your custom domain is properly resolving to your app, navigate to
`Settings > SSL Certificates` in your app dashboard, select `Configure SSL`,
and Choose `Automatic Certificate Management (ACM)`. Your app should now load
properly when you visit it with the `https://` protocol.

As a final step, we want to make sure that the app always redirects HTTP traffic
to HTTPS. Heroku [can't do this for us](https://help.heroku.com/J2R1S4T8/can-heroku-force-an-application-to-use-ssl-tls),
so we need to configure the app code to do it. Add the following settings to your
`settings.py` file:

```python
if DEBUG is False:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
```

When you deploy this change and try to load your app with the `http://` protocol,
it should now automatically redirect you to `https://` and display a valid certificate.

### General guidelines for custom domains

When setting up custom domains, follow these general guidelines:

- Where possible, let the client register the domain name so we don't have to manage it.
- Shorter domains are always better, but we usually defer to our clients' preferences
  when choosing a custom domain name.
- If the client has a pre-existing root domain, always advise deploying on a subdomain
  like `app.example.com` instead of a path like `example.com/app`. Clients often
  ask for paths off of root domains, but they are typically quite hard to deploy.
- If using a root domain, make sure to set up a `www` subdomain to redirect to the root.
- Don't allow `.herokuapp.com` in `DJANGO_ALLOWED_HOSTS` in production, since we want
  the custom domain to be canonical for search engine optimization.

## Troubleshooting

### I see `Application error` or a `Welcome to Heroku` page on my site

If your app isn't loading at all, check the dashboard to make sure that the most
recent build and release cycle passed. If the build and release both passed,
check the `Dyno formation` widget on the app `Overview` page to make sure that
dynos are enabled for your `web` process.

### Heroku CLI commands are failing without useful error messages

Sometimes a Heroku CLI command will fail without showing much output (e.g. `Build failed`).
In these cases, you can set the following debug flag to show the raw HTTP responses
from the Heroku API:

```bash
export HEROKU_DEBUG=1
```

### The release phase of my build is failing but the logs are empty

Heroku can't stream release logs unless `curl` is installed in the application
container. Double-check to make sure your Dockerfile installs `curl`.

If `curl` is installed and you still see no release logs, try viewing all of your app's logs by
running `heroku logs -a <YOUR_APP>`. Typically this stream represents the most
complete archive of logs for an app.

### I need to connect to an app database from the command line

The Heroku CLI provides a command, `heroku psql`, that you can use to connect
to your database in a `psql` shell. See the [docs for using this
command](https://devcenter.heroku.com/articles/connecting-to-heroku-postgres-databases-from-outside-of-heroku).

### I need to share a database between multiple apps

You can use the Heroku CLI to accomplish this task. See the Heroku docs on
[sharing databases between
applications](https://devcenter.heroku.com/articles/heroku-postgresql#sharing-heroku-postgres-between-applications).
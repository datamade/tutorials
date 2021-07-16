# Deploy a Django app to Heroku

This guide provides instructions on deploying a Django app to Heroku, DataMade's
preferred platform for hosting dynamic applications.

The easiest way to properly set up your application code for Heroku is
to use our [Django template](/docker/templates/) to create a fresh
Heroku-enabled Django app. The template includes additional nice features like ES6
support and GitHub Actions configuration, but it is only appropriate for brand new apps.
Once you've created your app, you can skip to learning how to [Provision Heroku
resources](#provision-heroku-resources).

If you'd like to convert an existing app to Heroku, or if the template is unfeasible
for some other reason, see [Set up application code for Heroku](#set-up-application-code-for-heroku).

## Contents


- [Provision Heroku resources](#provision-heroku-resources)
  - [Install the Heroku CLI with the manifest plugin](#install-the-heroku-cli-with-the-manifest-plugin)
  - [Create apps and pipelines for your project](#create-apps-and-pipelines-for-your-project)
  - [Set configuration variables for review apps and deployments](#set-configuration-variables-for-review-apps-and-deployments)
  - [Configure deployments from Git branches](#configure-deployments-from-git-branches)
- [Set up Slack notifications](#set-up-slack-notifications)
- [Enable additional services](#enable-additional-services)
  - [Solr](#solr)
  - [PostGIS](#postgis)
- [Set up a custom domain](#set-up-a-custom-domain)
  - [Step 1: Configure a custom domain on Heroku](#step-1-configure-a-custom-domain-on-heroku)
  - [Step 2: Configure a custom domain on a DNS provider](#step-2-configure-a-custom-domain-on-a-dns-provider)
  - [Step 3: Enable SSL](#step-3-enable-ssl)
  - [General guidelines for custom domains](#general-guidelines-for-custom-domains)
- [Set up application code for Heroku](#set-up-application-code-for-heroku)
  - [Containerize your app](#containerize-your-app)
  - [Clean up old configurations](#clean-up-old-configurations)
  - [Serve static files with WhiteNoise](#serve-static-files-with-whitenoise)
  - [Read settings and secret variables from the environment](#read-settings-and-secret-variables-from-the-environment)
  - [Configure Django logging](#configure-django-logging)
  - [Create Heroku config files](#create-heroku-config-files)
    - [`heroku.yml`](#herokuyml)
    - [`release.sh`](#releasesh)
    - [`app.json`](#appjson)
  - [Set up GitHub Actions for CI](#set-up-github-actions-for-ci)
- [Troubleshooting](#troubleshooting)

## Provision Heroku resources

**If you initialized your application with DataMade's [`new-django-app` Cookiecutter template](https://github.com/datamade/how-to/tree/master/docker/templates)**, your app is already configured to run on Heroku.
**If you are migrating an existing app**, or if you want to learn more about the configuration that comes with the template, see [Set up application code for Heroku](#set-up-application-code-for-heroku), below, before proceeding with this step.

The following instructions will help you deploy your properly configured application to the platform.

### Install the Heroku CLI with the manifest plugin

The fastest way to get a project up and running on Heroku is to use the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli). Before you start, make sure you have the CLI installed locally. Once you install the CLI, you'll need to [switch over to the CLI's beta version](https://devcenter.heroku.com/articles/build-docker-images-heroku-yml#creating-your-app-from-setup). This allows you to use the `manifest` CLI plugin, which you must install:

```
heroku update beta
heroku plugins:install @heroku-cli/plugin-manifest
```

Confirm that you have the manifest plugin installed:

```
heroku plugins | grep manifest
```

If you don't see any output, [follow the official instructions for installing the
plugin](https://devcenter.heroku.com/changelog-items/1441).

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
```

Your CLI output should look like this:
```bash
heroku create ${APP_NAME}-staging -t datamade --manifest 
Reading heroku.yml manifest... done
Creating ⬢ demo-app-staging... done, stack is container
Adding heroku-postgresql... done
https://demo-app-staging.herokuapp.com/ | https://git.heroku.com/demo-app-staging.git

heroku pipelines:add ${APP_NAME}-staging -a ${APP_NAME}-staging -s staging
Adding ⬢ demo-app-staging to datamade-app pipeline as staging... done
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
# Note that these need to be two separate commands due to an open Heroku bug,
# since --autodeploy and --autodestroy require a PATCH request
heroku reviewapps:enable -p ${APP_NAME}
heroku reviewapps:enable -p ${APP_NAME} --autodeploy --autodestroy
```

### Set configuration variables for review apps and deployments
Next, configure environment variables for staging and production apps. `DJANGO_SECRET_KEY`
should be a string generated using the [XKCD password generator](https://preshing.com/20110811/xkcd-password-generator/),
and `DJANGO_ALLOWED_HOSTS` should be a comma-separated string of valid hosts
for your app.

```bash
heroku config:set -a ${APP_NAME}-staging DJANGO_SECRET_KEY=<random-string-here>
heroku config:set -a ${APP_NAME}-staging DJANGO_ALLOWED_HOSTS=.herokuapp.com

# Run these commands if you have a production application
heroku config:set -a ${APP_NAME} DJANGO_SECRET_KEY=<random-string-here>
heroku config:set -a ${APP_NAME} DJANGO_ALLOWED_HOSTS=<your-list-of-allowed-hosts-here>
```

Note that review app config vars cannot yet be set using the CLI, but you can set them in
the Heroku dashboard by navigating to the pipeline home page and visiting
`Settings > Review Apps > Review app config vars` in the nav.

You can also set them in the `app.json` file, but only set non-sensitive values since that file is committed to version control. See [this code for an example](https://github.com/datamade/ca-wastewater-surveillance-system/blob/fecd93d7f91b892c5b63a921d954a941a723c383/app.json#L5), and the Heroku docs for [more information about the `app.json` schema](https://devcenter.heroku.com/articles/app-json-schema).

Also note that while `DATABASE_URL` is probably required by your application, you don't actually
need to set it yourself. The Heroku Postgres add-on will [automatically define this
variable](https://devcenter.heroku.com/articles/heroku-postgresql#designating-a-primary-database)
when it provisions a database for your application.

### Configure deployments from Git branches

Heroku can deploy commits to specific branches to different environments
(e.g. staging vs. production).

[Follow the Heroku documentation](https://devcenter.heroku.com/articles/github-integration#automatic-deploys)
to enable automatic deploys from `master` to your staging app. **Be sure to check
`Wait for CI to pass before deploy` to prevent broken code from being deployed!**

For production deployments, create a long-lived `deploy` branch off of `master` and
configure automatic deployments from `deploy` to production.

```bash
# create deploy branch (first deployment)
git checkout master
git pull origin master
git checkout -b deploy
git push origin deploy

# sync deploy branch with master and deploy to production (subsequent deployments)
git checkout master
git pull origin master
git push origin master:deploy
```

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
so we need to configure the app code to do it. If you didn't use the Django template
to create your app, add the following settings to your `settings.py` file:

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

## Set up application code for Heroku

In order to deploy a legacy Django application to Heroku, a few specific configurations
need to be enabled in your application code.

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

### Clean up old configurations

For new projects, you can skip this step. For existing projects that are being convered from our older deployment practices, you'll want to consolodate everything into `settings.py` and eventually delete your `settings_local.py` and supporting files. In switching to Heroku, the `settings_local.py` pattern is no longer necessary to store secret values as we'll be using environment variables instead. 

In addition, you will want to **delete** the following files, as we won't be using Travis, Blackbox or CodeDeploy:

* `.travis.yml` (we will be using GitHub Actions instead of Travis for CI)
* `appspec.yml`
* `APP_NAME/settings_local.example.py` (secret values are now stored as environment variables)
* `configs/nginx.xxx.conf.gpg` files
* `configs/supervisor.xxx.conf.gpg` files
* `configs/settings_local.xxx.py.gpg` files
* `configs/settings_local.travis.py` files
* `keyrings/live/pubring.kbx` (Blackbox is no longer needed as we're using environment variables)
* `scripts/after_install.sh.gpg` (no longer using AWS CodeDeploy)
* `scripts/before_install.sh.gpg`
* `scripts/app_start.sh.gpg`
* `scripts/app_stop.sh.gpg`

For an example of a conversion, [see this PR for the Erikson EDI project](https://github.com/datamade/erikson-edi/pull/162/) (private repo)

### Serve static files with WhiteNoise

Apps deployed on Heroku don't typically use Nginx to serve content, so they need some
other way of serving static files. Since our apps tend to have relatively low traffic,
we prefer configuring [WhiteNoise](http://whitenoise.evans.io/)
to allow Django to serve static files in production.

Follow the [setup instructions for WhiteNoise in
Django](http://whitenoise.evans.io/en/stable/django.html) to ensure that your
Django apps can serve static files. You will also need to include `whitenoise` in your `requirements.txt` as a dependency.

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

### Create Heroku config files

If you're converting an existing app to use Heroku, create the following config files
relative to the root of your repo. If you're setting up a Heroku deployment for
an app that you created with the Django template, you should have these config
files already, and you can safely skip to [Create apps and pipelines for your
project](#create-apps-and-pipelines-for-your-project).

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
set -euo pipefail

python manage.py collectstatic --noinput
python manage.py migrate --noinput
python manage.py createcachetable && python manage.py clear_cache
```

If your app uses a `dbload` script to load initial data into the database, you can use `release.sh`
to check if the initial data exists and run the data loading scripts if not. For example:

```bash
# Set ${TABLE} to the name of a table that you expect to have data in it.
if [ `psql ${DATABASE_URL} -tAX -c "SELECT COUNT(*) FROM ${TABLE}"` -eq "0" ]; then
    make all
fi
```

The `release.sh` file must be set to executable at the file system level. To do this, run `chmod +x scripts/release.sh` on your local machine and commit the change. Surprisingly, GitHub will recognize this change!

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
  "environments": {
    "review": {
      "addons": ["heroku-postgresql:hobby-basic"]
    }
  },
  "buildpacks": [],
  "stack": "container"
}
```

### Set up GitHub Actions for CI

For Heroku deployments, we use GitHub Actions for CI (continuous integration). Read the [how-to to set up GitHub Actions](https://github.com/datamade/how-to/blob/master/ci/github-actions.md).

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

### I get emails saying "[warning] Database disruption imminent, row limit exceeded"

If a review app requires loading in data with more than 10,000 rows, Heroku will
send an angry email to whoever "deployed" that review app saying that disruption
of the database is imminent because of exceeded row limits.

If the email is indeed referring to a review app, you can safely ignore it because "database disruption"
means that `INSERT` operations will be revoked in seven days and for most review
apps this is beyond the amount of time the app will be active anyway. If the email is
instead referring to a production app or a long-lived staging app, you should
[upgrade your Heroku Postgres plan](https://devcenter.heroku.com/articles/updating-heroku-postgres-databases)
for that instance to insure that database function continues.

In an ideal world it would be nice to configure apps that require >10,000 rows
of data to use a larger Heroku Postgres plan for review apps. Unfortunately, there
is not currently a way to set this type of configuration (and hence prevent these
kinds of emails being sent for review apps) because [Heroku defaults to the cheapest plan for
review app addons](https://help.heroku.com/SY28FR6H/why-aren-t-i-seeing-the-add-on-plan-specified-in-my-app-json-in-my-review-or-ci-app).

### Help! My staging pipeline doesn't have a database!
You might deploy a review app and everything works. Then you merge your code to master, which builds a new version to the staging pipeline. But for some reason, there is no database provisioned for staging.

Did you have the `manifest` CLI plugin installed when you first created the Heroku pipeline? If not, then it won't provision the Postgres add-on. [See this step](#install-the-heroku-cli-with-the-manifest-plugin).

Here's an example where the `manifest` plugin **was not installed** when creating an app:
```
heroku create ${APP_NAME}-staging -t datamade --manifest                                 
Creating ⬢ demo-app-staging... done
https://demo-app-staging.herokuapp.com/ | https://git.heroku.com/demo-app-staging.git
```

Here is an example where everything worked because the `manifest` plugin was installed:
```
heroku create ${APP_NAME}-staging -t datamade --manifest 
Reading heroku.yml manifest... done
Creating ⬢ demo-app-staging... done, stack is container
Adding heroku-postgresql... done
https://demo-app-staging.herokuapp.com/ | https://git.heroku.com/demo-app-staging.git

heroku pipelines:add ${APP_NAME}-staging -a ${APP_NAME}-staging -s staging
Adding ⬢ demo-app-staging to datamade-app pipeline as staging... done
```

The difference is in the CLI's output. In the working example, note the output `Reading heroku.yml manifest... done` and `Adding heroku-postgresql... done`.

If that is not the problem, then make sure your app's `heroku.yml` is configured correctly. When Heroku builds your app to a pipeline, it uses the `heroku.yml` file to provision the resources (like Postgres or Solr).

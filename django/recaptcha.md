# Set up Google reCAPTCHA in a Django app
Google's reCAPTCHA protects public-facing forms from the bots (like a sign up form). This guide will walk you through how to set up a production-ready reCAPTCHA in a Django/Docker/Heroku application. See [the reCAPTCHA documentation](https://developers.google.com/recaptcha/intro) for more details about reCAPTCHA itself.

There are two ways you can implement a reCAPTCHA in a Django app:
1. Use [the `django-recaptcha` plugin](https://pypi.org/project/django-recaptcha/). This is the recommended approach for use cases.
2. Implement the reCAPTCHA in your view and template.

This guide assumes that you have an existing form, or have created a new form prior to starting. You'll first implement a test reCAPTCHA. Once this is setup, it will be easy to reconfigure your application to use a real reCAPTCHA.

- [How it works](#how-it-works)
- [Set up the test reCAPTCHA](#set-up-the-test-recaptcha)
  - [Configure the keys](#configure-the-keys)
  - [Implement your code](#implement-your-code)
- [Test the implementation with a live reCATPCHA](#test-the-implementation-with-a-live-recaptcha)
- [Add a production reCAPTCHA](#add-a-production-recaptcha)
- [Resources](#resources)

## How it works
- A user fills out a form with the reCAPTCHA, then submits the form. Google provides some JavaScript to help with this.
- The view validates the form and the reCAPTCHA, separately.
  - The form fields are validated like any regular Django form.
  - To validate the reCAPTCHA, the view POSTs the user's reCAPTCHA response to Google's reCAPTCHA API.
  - Depending on Google's response, the reCAPTCHA is valid or invalid.

## Set up the test reCAPTCHA
Google provides a test reCAPTCHA that you can use for automated testing and local development. You'll need to setup the test reCAPTCHA within your application. The test reCAPTCHA should never be used in a production environment, because the validation always evaluates to true (aka not a bot).

### Configure the keys
1. Get the public key and secret key for Google's test reCAPTCHA. You can [get the keys from their site](https://developers.google.com/recaptcha/docs/faq#id-like-to-run-automated-tests-with-recaptcha.-what-should-i-do).

2. Add the public and private keys to your local environment. 
    - Create an `.env.example` file in your root directory. This will give you a file that can be commited to version control and shared with other developers, so they know what environment variables to set for their own local development. [Here is an example from one of our projects](https://github.com/datamade/parserator.datamade.us/blob/bda3201c3d7873916ed4075a2102b5805fad9a3a/.env.example#L9), with the keys for Google's test reCAPTCHA.
    - Once you have your `.env.example` file, copy it to a local `.env` file so that your application can use the environment variables.

3. Configure `docker-compose.yml` to use the environment file.
    - Reference the `.env` file in the project's root `docker-compose.yml` file. This will enable the app to run locally and use your local environment variables. [Here is an example](https://github.com/datamade/parserator.datamade.us/blob/bda3201c3d7873916ed4075a2102b5805fad9a3a/docker-compose.yml#L26).
    - If your automated tests interact with the reCAPTCHA, then add the environment variables to [`~/tests/docker-compose.yml`](https://github.com/datamade/parserator.datamade.us/blob/bda3201c3d7873916ed4075a2102b5805fad9a3a/tests/docker-compose.yml#L13).

Now you can use the public key and private key in your code. Whenever you deploy your app, you must change these keys to use a production reCAPTCHA (see [Add a production reCAPTCHA](#add-a-production-recaptcha)).

### Implement your code
  - An example where [we used the `django-recaptcha` plugin](https://github.com/datamade/la-metro-councilmatic/pull/737/files/02b6c9104eff556c15663e9c3d77bf24df35a519). This is the recommended implementation.
  - An example of how [we've implemented v2](https://github.com/datamade/parserator.datamade.us/blob/bda3201c3d7873916ed4075a2102b5805fad9a3a/parserator_web/views.py#L524).
  - An example of how [we've implemented v3](https://github.com/datamade/django-salsa-auth/commit/c8512d030b90762c7d703bfd1630f79d11e10a5e#diff-bfb393f3e832ecb2f6fb86ad35eefa88a87e0d773b3e4a80ce224d83997df815R137).

## Test the implementation with a live reCATPCHA
So far, you've been using Google's test reCAPTCHA, which always evaluates to true. If you want to test with a real, live reCAPTCHA, you can use one of the existing local development reCAPTCHAs.

1. Visit the admin dashboard: https://www.google.com/recaptcha/admin
2. Get the keys you need.
    - Use `local_development_v2` if you're using V2 of reCAPTCHA.
    - Use `local_development_v3` if you're using V3.
3. Change the public and private keys you set in the [Configure the keys](#configure-the-keys) section.

## Add a production reCAPTCHA
Get with your project lead to create a new, official reCAPTCHA for your app. This one should be used for staging and production environments. 

1. Visit the admin dashboard: https://www.google.com/recaptcha/admin
1. Create a new reCAPTCHA. Be sure to whitelist the proper domains.
1. Get the public and private keys for the new reCAPTCHA.
1. Set Heroku environment variables with those keys.
1. Deploy to Heroku with environment variables.
1. Test that it works.
1. Bye Bye Bots.


## Resources
- [The reCAPTCHA admin dashboard](https://www.google.com/recaptcha/admin)
- [Google's documentation about reCAPTCHA](https://developers.google.com/recaptcha/intro)
- [Google's reCAPTCHA for automated testing](https://developers.google.com/recaptcha/docs/faq#id-like-to-run-automated-tests-with-recaptcha.-what-should-i-do)
- [the `django-recaptcha` plugin](https://pypi.org/project/django-recaptcha/)
- DataMade implementations:
  - [Using the `django-recaptcha` plugin](https://github.com/datamade/la-metro-councilmatic/pull/737/files/02b6c9104eff556c15663e9c3d77bf24df35a519). This is the recommended implementation.
  - [v2 with custom code for the view and template](https://github.com/datamade/parserator.datamade.us/blob/bda3201c3d7873916ed4075a2102b5805fad9a3a/parserator_web/views.py#L524).
  - [v3 with custom code for the view and template](https://github.com/datamade/django-salsa-auth/commit/c8512d030b90762c7d703bfd1630f79d11e10a5e#diff-bfb393f3e832ecb2f6fb86ad35eefa88a87e0d773b3e4a80ce224d83997df815R137).

# Set up Google reCAPTCHA in a Django app
Google's reCAPTCHA protects public-facing forms from the bots (like a sign up form). This guide will walk you through how to set up a production-ready V2 reCAPTCHA in a Django/Docker/Heroku application. See [the reCAPTCHA documentation](https://developers.google.com/recaptcha/intro) for more details about reCAPTCHA itself.

Each application requires a unique reCAPTCHA. Anytime you want to add a reCAPTCHA to your app, you'll need to create a new one for production. In addition to your unique reCAPTCHA, Google provides a test reCAPTCHA that you can use for automated testing and local development. 

- [How it works](#how-it-works)
- [Set up the test reCAPTCHA](#set-up-the-test-recaptcha)
- [Create a reCAPTCHA for testing](#create-a-throwaway-recaptcha-for-testing)
- [Add a production reCAPTCHA](#add-a-production-recaptcha)

## How it works
- User fills out the form, including the reCAPTCHA, then submits the form. Google provides some JavaScript to help with this.
- The view validates the form and the reCAPTCHA, separately.
  - The form fields are validated like any regular Django form.
  - To validate the reCAPTCHA, the view POSTS the user's reCAPTCHA response to Google's reCAPTCHA API.
  - Depending on Google's response, the reCAPTCHA is valid or invalid.

## Set up the test reCAPTCHA
First, you'll need to setup the test reCAPTCHA within your application.

### 1. Get the reCAPTCHA keys
Get the public key and secret key for Google's test reCAPTCHA. You can [get the keys from their site](https://developers.google.com/recaptcha/docs/faq#id-like-to-run-automated-tests-with-recaptcha.-what-should-i-do).


### 2. Add the public and private keys to your local environment
Create an `.env.example` file in your root directory. This will give you a file that can be commited to version control and shared with other developers, so they know what environment variables to set for their own local development. [Here is an example from one of our projects](https://github.com/datamade/parserator.datamade.us/blob/bda3201c3d7873916ed4075a2102b5805fad9a3a/.env.example#L9), with the keys for Google's test reCAPTCHA.

Once you have your `.env.example` file, copy it to a local `.env` file so that you can keep secrets safe: 
```bash
cp .env.example .env
```

### 3. Configure docker-compose to use the environment file
- Reference the `.env` file in the project's root `docker-compose.yml` file. This will enable the app to run locally and use your local environment variables. [Here is an example](https://github.com/datamade/parserator.datamade.us/blob/bda3201c3d7873916ed4075a2102b5805fad9a3a/docker-compose.yml#L26).
- Add the environment variables to `~/tests/docker-compose.yml`, [like so](https://github.com/datamade/parserator.datamade.us/blob/bda3201c3d7873916ed4075a2102b5805fad9a3a/tests/docker-compose.yml#L13).

Now you can use the public key and private key in your code.

### 4. Use the reCAPTCHA in your code
There are a few ways of doing this, so [refer to Google](https://developers.google.com/recaptcha/intro) when considering how to implement this in your project. For this guide, we are implementing V2 of reCAPTCHA.

#### Configure the view with the public key
[Pass the public key into the template via the context](https://github.com/datamade/parserator.datamade.us/blob/bda3201c3d7873916ed4075a2102b5805fad9a3a/parserator_web/views.py#L519).

#### Add Google's magic JavaScript and public key to your template
Your application needs to have some code on the frontend. [See Google's documentation](https://developers.google.com/recaptcha/docs/display#auto_render) on how to add the reCAPTCHA to your code. We also have [an example of how this looks](https://github.com/datamade/parserator.datamade.us/blob/bda3201c3d7873916ed4075a2102b5805fad9a3a/parserator_web/templates/parserator_web/sign_up.html#L64) in an application. [This is where you'll use the public key](https://github.com/datamade/parserator.datamade.us/blob/bda3201c3d7873916ed4075a2102b5805fad9a3a/parserator_web/templates/parserator_web/sign_up.html#L53) you just added to your context.


#### Add a helper function to validate the reCAPTCHA with Google's API
Your backend needs to accept the reCAPTCHA response from the frontend, and then send a request to Google to validate the reCAPTCHA response. 
- Here's an example of how we've done this with V2: https://github.com/datamade/parserator.datamade.us/blob/bda3201c3d7873916ed4075a2102b5805fad9a3a/parserator_web/views.py#L524.
- Here's another example of this with V3: https://github.com/datamade/django-salsa-auth/commit/c8512d030b90762c7d703bfd1630f79d11e10a5e

### 5. Test it manually and automatically
If everything was setup correctly, then you should be able submit the form.

## Create a throwaway reCAPTCHA for testing
If you want to test a real reCAPTCHA, then you'll need to first create one. You can use this reCAPTCHA to test locally and with deployments.

### Create the reCAPTCHA
Go to the reCAPTCHA admin site and create a new reCAPTCHA: https://www.google.com/recaptcha/admin/create. It should be the v2 type. Add `localhost` as your domain.

### Reconfigure your environment variables
In your `.env` that you created earlier, change the public and private key. Use the keys from the reCAPTCHA you just created.

### Test it
This is where you might need to do some debugging. Good luck!


## Add a production reCAPTCHA
Get with a project lead to create a new, official reCAPTCHA for your app. [Follow the steps from the previous section](#create-the-recaptcha) to create this. This one should be used for staging and production environments. 

- Create a new reCAPTCHA.
- Get the keys from the new reCAPTCHA.
- Set environment variables on Heroku with those keys.
- Deploy to Heroku with environment variables.
- Test that it works
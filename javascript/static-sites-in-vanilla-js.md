# Static Sites in Vanilla JavaScript

Plain old HTML, CSS, and a JavaScript file or two offer a simple developer
experience during development and deployment. This document contains an
assessment of this stack, as well as guidance on when to use it, and some tips
for publishing your work.

## The case for vanilla ES6

### Does DataMade currently create many apps that could be "little sites"?

Yes, several DataMade projects, old and new, qualify as little sites, including:

- The budget visualization family, including [Look at Cook](
https://github.com/datamade/look-at-cook) and [NY Budget](
https://github.com/datamade/ny-budget)
- [IHS Displacement Risk Map](https://github.com/datamade/ihs-displacement-risk-in-chicago)
- [IHS Price Index](https://github.com/datamade/ihs-price-index)
- [NWSS Demo](https://github.com/datamade/nwss-data-standard/tree/main/docs)
- [Public Land Survey](https://github.com/fgregg/public-land-survey)

I anticipate that we can find even more opportunities to create little apps once
we officially add this development stack to our toolkit. 

While we don't create a huge volume of single-page apps, this stack is
particularly well suited to demos and proofs of concepts, especially in
instances where the proof of concept will eventually become part of a Django
app. In this case, we can avoid the overhead of writing a Gatsby app we'll
ultimately abandon by using vanilla JavaScript instead.

### What are the pros and cons of writing single page apps in vanilla JavaScript? How does it compare to Gatsby? 

#### Developer experience

Vanilla JavaScript offers many advantages over Gatsby. Chief among them, the
learning curve for vanilla JavaScript is much less steep. It does not require
any knowledge of React or GraphQL. 

Vanilla JavaScript also requires few or no build steps. In the event that your
vanilla JavaScript app does have a build step to bundle your code with its
dependencies and transpile it for browser compatibility, it is generally quicker
and more transparent than Gatsby builds, which can be slow and abstract away
important context, particularly while debugging.

Vanilla JavaScript can also be configured to match Gatsby's live reloading with
[watchify](https://www.npmjs.com/package/watchify).

N.b., [our `new-vanilla-js-app` cookiecutter](../docker/templates/new-vanilla-js-app)
is set up with a `develop` script that runs a local server and uses `watchify`
to rebundle and retranspile JavaScript as it changes, as well as a `build`
script to bundle and transpile code during deployment.

#### Deployment

Vanilla JavaScript can be deployed on GitHub pages, a feature none of our
other development stacks offers. If a staging site is needed, vanilla JavaScript
can be deployed on Netlify, the same as our Gatsby apps.

#### Browser compatibility

Gatsby [comes with broad browser support out of the box](
https://www.gatsbyjs.com/docs/how-to/custom-configuration/browser-support/),
while vanilla JavaScript apps must add a build step to transpile code with
Babel.

N.b. (redux), [our `new-vanilla-js-app` cookiecutter](../docker/templates/new-vanilla-js-app)
is set up with a `develop` script that runs a local server and uses `watchify`
to rebundle and retranspile JavaScript as it changes, as well as a `build`
script to bundle and transpile code during deployment.

#### Maintainability

Gatsby continues to grow in popularity, and we don't anticipate that it will
fall out of active support or development any time soon. With that said, its
pre-requisite skills do make maintainability slightly more challenging as we
cycle in new staff, who may or may not have those skills.

Conversely, a lower learning curve means any staff could probably pick up a
vanilla JavaScript app without issue.

## When to use Vanilla ES6

Does your site need:

- Only one or two pages?
- A minimally complicated map?
- Lightweight data, e.g., a single JSON or CSV file or low cost external requests

It could be well suited to the vanilla JavaScript stack! Read on for more
details.

On the other hand, does your site need:

- Multiple pages, particularly pages based on data?
- Heavyweight data, e.g., multiple data files, an external datastore (such as
Hasura), or heavy external requests?
- Complex maps, charts, or other visualizations?

Then it's probably better suited for Gatsby. [Head over to our Gatsby docs to
learn more](gatsby/).

## Prerequisites

For a maximally productive time, you'll want to familiarize yourself with
[our JavaScript stack](https://github.com/datamade/how-to/blob/hcg/lil-js/javascript/stack.md),
namely the `yarn` package manager and build tool, as well as ES6 itself.

## Patterns

### Development

If your app doesn't have any dependencies, or if you can ship them with your
code or source them from a CDN, simply create an `index.html` file and a
`main.js` file, and off you go.

You can serve your files in local development like:

```bash
python3 -m http.server
```

If you're using ES6 syntax, though, this approach will not be compatible with 
all browsers.

If you're targeting a broader user base, and/or if you prefer the ease of using
a CLI to manage packages, we recommend using `yarn` to install dependencies
and Browserify and Babelify to bundle third-party packages with your code and
compile them to ES5 for maximum compatibility. 

See [our `new-vanilla-js-app` cookiecutter](../docker/templates/new-vanilla-js-app)
for an example of this setup. It contains the following components:

1. A `package.json` file defining `develop` and `build` scripts that bundle and
transpile your JavaScript during development and deployment, respectively.
2. A `babel.config.json` file specifying target browsers.
3. Starter HTML, CSS, and JS files for your website.

To serve your site locally, simply:

```bash
yarn run develop
```

This command will detect changes to your main JavaScript file and automatically
rebundle and retranspile it as you work.

### Deployment

#### GitHub Pages

Vanilla JavaScript sites can be hosted seamlessly on GitHub Pages.

Working without build steps (e.g., using a CDN for dependencies)? Simply
navigate to your repository settings > Pages, then enable GitHub Pages.

If you need a build step, you can define a GitHub Action to bundle and transpile
your code. See [the NWSS project](
https://github.com/datamade/nwss-data-standard/blob/main/.github/workflows/gh-pages.yml)
for an example. Once you've defined the action, head to your repository settings >
Pages, then enable GitHub Pages from the branch your action pushes builds to
(`gh-pages`, by default).

#### Netlify

If you need staging and production instances of your site, you can follow [our
documentation for deploying static sites to Netlify](
https://github.com/datamade/how-to/tree/master/deployment/netlify).

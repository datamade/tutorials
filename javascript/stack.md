# The DataMade JavaScript Stack

A number of tools comprise our development stack for projects written in or
containing JavaScript.

## Static sites

### Vanilla JavaScript

1. [ES6](http://es6-features.org/) - A number of big improvements to core JavaScript syntax
2. [Yarn](https://yarnpkg.com/) - package manager
3. [Browserify](https://browserify.org/) - build tool to bundle dependencies with code
4. [Babelify](https://www.npmjs.com/package/babelify) - Browserify plug-in that transpiles ES6 to ES5 for browser compatibility using [Babel](https://babeljs.io/)
5. [Watchify](https://www.npmjs.com/package/watchify) - build tool to update bundled/transpiled code during development
6. [GitHub Pages](https://pages.github.com/) or [Netlify](https://www.netlify.com/) - deployment platforms

### Gatsby 

1. [Gatsby](https://www.gatsbyjs.org/) - static site generator
2. [React](https://reactjs.org/) - JavaScript framework for building user interfaces
3. [Yarn](https://yarnpkg.com/) - package manager
4. [ESLint](https://eslint.org/) - linter
5. [Netlify](https://www.netlify.com/) - deployment platform
6. [Docker](https://www.docker.com/products/docker-desktop) / [Docker Compose](https://docs.docker.com/compose/) - container engine

## Django/React Integration

1. [ES6](http://es6-features.org/) - A number of big improvements to core JavaScript syntax
2. [React](https://reactjs.org/) - JavaScript framework for building user interfaces
3. [Yarn](https://yarnpkg.com/) - package manager
4. [Browserify](https://browserify.org/) - build tool to bundle dependencies with code
5. [Babelify](https://www.npmjs.com/package/babelify) - Browserify plug-in that transpiles ES6 to ES5 for browser compatibility using [Babel](https://babeljs.io/)

## Some example setups

### Vanilla JavaScript

- Buildless: [IHS Displacement Risk Map](https://github.com/datamade/ihs-displacement-risk-in-chicago)
- Bundled code and dependencies: [NWSS Demo Site](https://github.com/datamade/nwss-data-standard)

### Gatsby

- Basic static app: [`static-app-template`](https://github.com/datamade/static-app-template/) (to be iterated upon)
- Static app with `recharts` charts: [`how-to-recharts`](https://github.com/datamade/how-to-recharts/)
- Static app with `react-leaflet` map: [`lisc-cnda-map`](https://github.com/datamade/lisc-cnda-map/)

## React in Django

Integrating React with Django? See [the docs on our approach](https://github.com/datamade/how-to/blob/master/django/django-react-integration.md).

## Managing packages and plugins

As in Python, there are a few competing package managers in JavaScript. The two most popular are [npm](https://www.npmjs.com/get-npm), which comes bundled with Node.js, and [Yarn](https://yarnpkg.com/). At DataMade, we like Yarn, in particular for its build speed.

See [this article](https://stackshare.io/stackups/npm-vs-yarn) for a more detailed comparison of the leading package managers.

See [the Yarn documentation](https://yarnpkg.com/getting-started/) for more detailed information of usage.

#### 🚨 A note on `yarn` and Docker entrypoints

If you are using a containerized development environment that defines `yarn` as its entrypoint, omit `yarn` from commands you execute with `docker-compose run`. Why? Docker prepends `run` commands with the entrypoint command.

If you are seeing errors like this when you try to run `yarn` commands with your application container -

```bash
yarn run v1.15.2
error Command "yarn" not found.
info Visit https://yarnpkg.com/en/docs/cli/run for documentation about this command.
```

- this is almost certainly the problem! Run your commands like this, instead:

```bash
# The application's entry point is "yarn" so we only need to pass the "add" command.
docker-compose run --rm app add ${PACKAGE}
```

### Defining your package

Similarly to `setup.py` in Python, JavaScript apps are defined in a central file called `package.json`. [See the Yarn documentation on composing your own `package.json` file](https://classic.yarnpkg.com/en/docs/package-json/).

Starting from scratch? Yarn provides a nice utility to help you create a `package.json` file interactively. Run `yarn init` from your command line, then complete to prompts.

### Installing dependencies

Similarly to `pip` in Python, Yarn provides a straightforward command to install a package in your
project.

```bash
yarn add ${PACKAGE}
```

Unlike `pip`, calling `yarn` add will also add your dependency to `package.json` and create a `yarn.lock` file containing the exact version of each package in your dependency tree.

Then, if the package you installed is a Gatsby plugin, add the package to
`gatsby-config.js`:

```javascript
module.exports = {
  plugins: [
    '${PACKAGE}',
  ],
}
```

If the plugin comes with a stylesheet, e.g., Leaflet, you can add it like this
to automatically pull in styles via CDN.

```javascript
module.exports = {
    plugins: [{
      resolve: 'gatsby-plugin-react-leaflet',
      options: {
        linkStyles: true // Enable/disable loading stylesheets via CDN
      }
    }],
}
````

### Running custom scripts

JavaScript package managers are also build tools. Usefully, they allow you to define custom scripts in your `package.json` files.

```json
module.exports = {
    "scripts": {
        "develop": "gatsby develop"
    }
}
```

If you run a command that Yarn doesn't recognize, it will check your `package.json` for a corresponding script, and execute it, if it finds one.

```bash
yarn develop
```

You can also use `yarn run` to run your custom scripts explicitly.

```bash
yarn run develop
```

See [the Yarn documentation](https://classic.yarnpkg.com/en/docs/cli/run/) for more information on custom scripts.

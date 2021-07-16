# {{cookiecutter.app_verbose_name}}

_{{cookiecutter.app_description}}_

## Developing

Development requires a local installation of [Yarn](https://yarnpkg.com/).

Run the app:

```
yarn run develop
```

The app will be available at http://localhost:8000. 

### Ensuring browser compatibility

The default `babel.config.json` file will transpile JavaScript in your `js/`
directory to syntax that's friendly to modern and legacy browsers but it will
not transpile third-party plug-ins by default.

Some plug-ins target Node versions above ES5, which means that they aren't
compatible for older browsers. Luckily, we can tell Babel to transpile these
dependencies to ensure our apps remain broadly compatible across browsers.

To identify problematic plug-ins, you can use [the `es6-sniffer` CLI](https://github.com/hancush/python-es6-sniffer).

```bash
# Build the es6-sniffer image from GitHub
docker build -t es6-sniffer https://github.com/hancush/python-es6-sniffer.git

# Sniff out potentially incompatible modules
docker run -v {{ cookiecutter.app_name }}_{{ cookiecutter.app_name }}-node-modules:/node_modules --rm es6-sniffer
```

Once you've found the culprits, add them to the `only` array in
`babel.config.json`. For example:

```json
{
    "only": [
        "./js", // Your JavaScript - default
        "./node_modules/problem_module_a",
        "./node_modules/problem_module_b"
    ],
    // The rest of your config
}
```

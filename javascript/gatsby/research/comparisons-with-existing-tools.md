# Comparing Gatsby with existing tools

How does Gatsby compare to other tools in the DataMade toolkit?

### Gatsby vs. Jekyll

Gatsby's most obvious competitor is [Jekyll](https://jekyllrb.com/), a static site generator built in Ruby. We've used Jekyll for a number of static sites in the past, including [the DataMade website](https://github.com/datamade/datamade.us), [dedupe.io](https://github.com/dedupeio/dedupe.io), and [CUAMP](https://github.com/datamade/CUAMP-live).

Gatsby and Jekyll can both be deployed on Netlify as purely static sites, which makes them attractive candidates for sites that require no dynamic backend functionality like faceted search, persistent data storage, user management, or admin interfaces.

In general, you should prefer Gatsby to Jekyll when:

- You have a team that has working knowledge of ES6, NPM, React, and GraphQL
- You would like to load and display data from data sources other than Markdown

#### Pros

- Gatsby is built on top of JavaScript, a language that we use much more regularly than Ruby.
- Gatsby supports data loading from a huge variety of data sources via its extensible data layer API. Jekyll can only read data from Markdown posts, or from specially-formatted YAML, JSON, or CSV files living in the `_data` folder.
- Gatsby uses React under the hood and exposes a fully-configured React development environment, meaning you can make use of JSX and the React plugin ecosystem. Jekyll requires you to use the [Liquid templating language](https://jekyllrb.com/docs/liquid/), which does not integrate as closely with JavaScript as JSX.
- Gatsby builds in a lot of performance optimizations, including code splitting, progressive rendering, and resized images for different devices. (For a deep dive on Gatsby's performance optimizations, see [Why is Gatsby so fast?](https://www.gatsbyjs.org/blog/2017-09-13-why-is-gatsby-so-fast/))
- Gatsby bakes in a modern JavaScript development environment by default, including hot reloading, source maps, and JavaScript package management.

#### Cons

- By nature of offering more flexible data management and a modern JavaScript environment, a Gatsby project is typically more complicated to set up than a Jekyll project.
- Gatsby requires working knowledge of ES6, NPM, React, GraphQL. While these tools are very powerful and fun to use once you understand them, they may be overwhelming at first for devs who are learning them all at once.
- Since it is built on top of React, Gatsby does not play well with JQuery. This has the disadvantage of making it incompatible with many of the JQuery libraries DataMade uses regularly, and it means you'll often need to use a React plugin to get older JavaScript libraries to work (e.g. [react-leaflet](https://react-leaflet.js.org/) in addition to vanilla [Leaflet](https://leafletjs.com/)).

### Gatbsy vs. Django

At first glance, Gatsby and Django may appear to be very different tools -- Gatsby is a static site generator, while Django is a full-featured MVC web framework -- but in practice, Gatsby can be a good choice for many simple apps that we would otherwise build in Django.

In particular, Gatsby's flexible data layer means that it can [generate pages programmatically from data](https://www.gatsbyjs.org/tutorial/part-seven/). This means that Gatsby can easily generate list and detail views based on a CSV or Postgres database. And since Gatsby can be deployed as a static site on Netlify, you can save a lot of time that you would otherwise spend provisioning staging and production environments, and serve up fast prebuilt assets to boot.

In general, you should prefer Gatsby to Django when:

- You have a team that has working knowledge of ES6, NPM, React, and GraphQL
- Your app doesn't require any dynamic backend behavior like faceted search, persistent data storage, user management, or admin interfaces
- Your primary motivation for considering Django over static HTML/CSS/JS is the ability to generate views based on data

#### Pros

- By treating JavaScript as a first-class citizen, Gatsby and React make the process of building frontend interactions much more intuitive (and much more testable) than Django does.
- Deploying on Netlify reduces the overhead of Continuous Deployment and server provisioning/management.
- In addition to Gatsby's [built-in performance optimizations](https://www.gatsbyjs.org/blog/2017-09-13-why-is-gatsby-so-fast/), the fact that you're deploying static assets instead of rendering responses on a server means that a Gatsby app by default will load pages much faster than a Django app.

#### Cons

- So far, we don't have a good way of doing faceted search in a Gatsby app. [David Eads has done it](https://www.propublica.org/nerds/the-ticket-trap-news-app-front-to-back-david-eads-propublica-illinois) but we still need to prove it out in our stack.
- Gatsby lacks a simple solution for user management and admin views. [We're tracking the progress of Netlify Identity](https://jeancochrane.com/blog/netlify-identity-dealbreakers), but it's not production-ready yet.
- Gatsby requires working knowledge of ES6, NPM, React, and GraphQL. As of May 2019, these technologies are less well-known on our team than Python and Django.

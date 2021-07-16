# GatsbyJS

This directory records best practices for working with [GatsbyJS](https://github.com/datamade/tutorials/projects/1), a static site generator built on top of React and GraphQL.

**Our cookiecutter for creating a new Gatsby app lives in the [containerization templates](https://github.com/datamade/how-to/tree/master/docker/templates) directory.**

## Contents

- README
    - [When to use Gatsby](#when-to-use-gatsby)
    - [How to use Gatsby](#how-to-use-gatsby)
    - [Resources for learning](#resources-for-learning)
- [Research](./research/)
    - [Comparisons with existing tools](./research/comparisons-with-existing-tools.md)
        - [Gatsby vs. Jekyll](./research/comparisons-with-existing-tools.md#gatsby-vs-jekyll)
        - [Gatsby vs. Django](./research/comparisons-with-existing-tools.md#gatsby-vs-django)
    - [Recommendation of adoption](./research/recommendation-of-adoption.md)
- [Stack](stack.md)
    - [Tools in our Gatsby development stack](stack.md)
    - [Some example setups](stack.md#some-example-setups)
    - [Managing packages and plugins](stack.md#managing-packages-and-plugins)
- [Best practices](best-practices.md)
    - [Styling and images](best-practices.md#styling-and-images)
    - [State management](best-practices.md#state-management)
    - [ETL and querying](best-practices.md#etl-and-querying)
    - [Pagination](best-practices.md#pagination)
    - [SEO](best-practices.md#seo)

## Standard toolkit

| Objective | Library | Internal documentation |
| :- | :- | :- |
| Data Visualization | [`recharts`](http://recharts.org/) | |
| Error Logging | [`@sentry/gatsby`](https://www.gatsbyjs.com/plugins/@sentry/gatsby/) | [Link](./../logging/sentry.md#logging-errors-in-gatsby-applications) |

## When to use Gatsby

Gatsby is an excellent choice for two types of projects:

1. Static sites (that is, sites that can be deployed with pure HTML/CSS/JavaScript)
2. Small dynamic sites with a limited range of simple server-side functions **not** including faceted search, user administration, or admin interfaces

For more details on the specific pros and cons of Gatsby, see the [comparisons with existing tools](./research/comparisons-with-existing-tools.md) produced during R&D.

## How to use Gatsby

To start a Gatsby project, [create a new repository from our Static App Template](https://github.com/datamade/static-app-template/generate). Once you're ready to publish the site, follow our guide to [deploy a static site](https://github.com/datamade/deploy-a-site/blob/master/Deploy-a-static-site.md).

For an example of a DataMade app deployed with Gatsby, see [LISC CNDA](https://github.com/datamade/lisc-cnda).

## Resources for learning

The following is a list of good resources for learning how to use Gatsby.

- [The Gatsby.js tutorial](https://www.gatsbyjs.org/tutorial/) - Gatsby's official tutorial. A full walkthrough of building a simple blog from scratch in Gatsby, including quick sidebars on the basics of React, JSX, and GraphQL.
- [The React docs](https://reactjs.org/docs/hello-world.html) - A step-by-step guide through the basics of React. Useful for getting your bearings in JSX, components, and React state management, which are important prerequisites for Gatsby.
- [The Fullstack Tutorial for GraphQL](https://www.howtographql.com/) - Gatsby's recommended tutorial for learning GraphQL. We recommend reading the "GraphQL fundamentals" section.
- [@jeancochrane's lunch&learn on Gatsby](https://gist.github.com/jeancochrane/705dda18da74fafe4b8182d15284114d) - A set of brief notes giving a quick overview of Gatsby's features.

See our documentation on [the Gatsby development stack](stack.md) for more on how we organize Gatsby applications and manage JavaScript dependencies at DataMade.

## Debugging your Gatsby code

- **Use [React Developer Tools](https://chrome.google.com/webstore/detail/react-developer-tools/fmkadmapgofadopljbjfkapdkoienihi) to follow the data**

    > React Developer Tools is a Chrome DevTools extension for the open-source React JavaScript library. It allows you to inspect the React component hierarchies in the Chrome Developer Tools.

    Using this browser extension, you can run your site locally and inspect components in the browser to see what's appearing where and what value each prop holds. To gain an advanced understanding of this extension, go through their [interactive tutorial](https://react-devtools-tutorial.now.sh/).

- **Make sure you've wrapped your head around the React and Gatsby lifecycles**

    React and Gatsby have a component and build lifecycles, respectively, very conceptually distinct from Django projects. If you're running into issues with how a component is rendered, re-rendered, or updated, it might be useful to brush up on the [React component lifecycle](https://reactjs.org/docs/state-and-lifecycle.html). If you're running into errors while building your project—either locally or on Netlify—and you're not sure why, it's helpful to step back and make sure you can identify which step in the process is causing problems, which will better help you understand if you need to change something in `gatsby-node.js`, `gatsby-browser.js`, or `gatsby-ssr.js`. We recommend this summary of the [Gatsby build lifecycle](https://www.narative.co/articles/understanding-the-gatsby-lifecycle) as well as the [official docs](https://www.gatsbyjs.com/docs/overview-of-the-gatsby-build-process).

- **Remember the distinctions between `gatsby develop` and `gatsby build`**

    Some of the peskiest bugs in Gatsby show up only in production. If your site is working locally but not once it's deployed, the culprit may be one of the differences between the `gatsby develop` and `gatsby build` commands. To understand the distinctions, read through [this documentation](https://www.gatsbyjs.com/docs/overview-of-the-gatsby-build-process). They've also helpfully broken down common missteps in HTML builds for us [here](https://www.gatsbyjs.com/docs/debugging-html-builds/).

    

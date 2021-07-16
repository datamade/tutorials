# Gatsby best practices

## Styling and images
Gatsby provides solutions for a few common styling needs.
* *Links*: Use [`<Link>`](https://www.gatsbyjs.com/docs/reference/built-in-components/gatsby-link/) instead of `<a>` for local links. This takes advantage of Gatsby's page pre-loading and makes changing between pages much quicker. 
* *Images*: In Wes Bos's Gatsby course, he recommends using [`gatsby-image`](https://www.gatsbyjs.com/plugins/gatsby-image/), however this package has been deprecated. Instead, use [`gatsby-plugin-image`](https://www.gatsbyjs.com/plugins/gatsby-plugin-image). This plugin makes it easier to include responsive images or even images available through your CMS.
* *Layout*: Gatsby's [`gatsby-plugin-layout`](https://www.gatsbyjs.com/plugins/gatsby-plugin-layout/) makes it easy to create a layout that [won't unmount from the page when the top-most component re-loads](https://www.gatsbyjs.com/docs/how-to/routing/layout-components/).

## State management
The best way to manage state in Gatsby is using hooks within functional components. 

Hooks allow us to 'hook into' the `state` object in React by creating and returning the new property on the `state` object and a function that will allow us to update this property. Hooks make components more concise and remove the need to refactor to and from class components, among other benefits. 

Here's the [React documentation on hooks](https://reactjs.org/docs/hooks-intro.html).

## ETL and querying
In order to load data into a Gatsby site, we make use of the really helpful `gatsby-config.js` file. It allows, among other things, to pull data from an ETL pipeline into GraphQL, add site metadata, and make use of plugins. For more on `gatsby-config.js`, see the [Gatsby documentation](https://www.gatsbyjs.com/docs/reference/config-files/gatsby-config/).

### Queries
There are two ways to write GraphQL queries in Gatsby. One way is by using a [page query](https://www.gatsbyjs.com/docs/how-to/querying-data/page-query/), in which the query must run on a top level page (as opposed to component). From there, we can pass data down as props to child components of the page. One of the biggest upsides to using page queries is that they can be dynamic. This means you can filter, limit, and sort the results from the query using variables. Here's a basic example of a [sorting page query](https://github.com/sunrisedatadept/green-jobs/blob/main/src/pages/compare.js).

The other way to query for data from GraphQL is using [`StaticQuery`](https://www.gatsbyjs.com/docs/how-to/querying-data/static-query/). Static queries cannot be dynamic, and no variables can be passed, but they can run on components as well as pages.

No matter which kind of query you decide on, [GraphiQL](https://www.gatsbyjs.com/docs/how-to/querying-data/running-queries-with-graphiql/) is a great tool for drafting your query, exploring filters, and getting an immediate view of the data you would have access to. It is available on your local app at `/___graphql`.

## Pagination 
When trying to create pages for pieces of information and will not be using a table package that may include pagination functionality, Wes Bos's ["Master Gatsby" course](https://wesbos.com/courses) takes you step by step in creating pagination. His method involves setting up [`gatsby-node.js`](https://www.gatsbyjs.com/docs/reference/config-files/gatsby-node/) and the [createPage action](https://www.gatsbyjs.com/docs/reference/config-files/actions/#createPage). 

## SEO
We use [React Helmet](https://github.com/nfl/react-helmet#readme) in order to customize the HTML head of individual Gatsby pages.

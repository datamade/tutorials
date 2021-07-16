# recharts

[`recharts`](http://recharts.org/) is a charting library for React components and our preferred method to create data visualizations in Gatsby projects. Install it in your containerized Gatsby project by running:

`docker-compose run --rm add recharts --save`

You can then import components that you want to use into individual modules. See [Getting Started](http://recharts.org/en-US/guide/getting-started) and the [Examples page](http://recharts.org/en-US/examples) for models of how this works.

In general, Recharts is a robust library but often underdocumented. We recommend starting from their examples page to build what you want, then consulting StackOverflow as you hit the limits of what the official documentation can offer.

## On data transformation
**We do _not_ recommend performing any data transformation with Recharts or in frontend Gatsby components.** This can slow down an application's performance as calculations run on page load, and also creates an unnecessary opportunity for error in a project's data pipeline. Instead, all data transformation for visualizations should be performed in separate scripts that generate finalized data that can then be passed directly to Recharts components. A couple example setups for this:

- For [The Circuit's charges visualizations](https://gitlab.com/court-transparency-project/charges-app), we ran a remote database using Amazon RDS. This database had an `analysis` schema with tables created with raw SQL commands run by a Makefile in a [separate data repo](https://gitlab.com/court-transparency-project/cleaning-charges). These tables were formatted to pass directly to Recharts via GraphQL queries with a [Hasura](https://hasura.io/) connection.
- For Gatsby projects with smaller data sets that can be kept under version control, we recommend following [DataMade's datamaking practices](https://github.com/datamade/data-making-guidelines) and transforming data with Python scripts via a Makefile. Recharts can then source directly from the `data/finalized` directory. Bea's [Covid-19 Neighborhoods](https://github.com/beamalsky/medical-examiner-data) website is an example of this approach.
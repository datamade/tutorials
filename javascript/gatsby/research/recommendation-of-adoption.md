# Recommendation of adoption: GatsbyJS

Based on our research, we recommend adopting Gatsby as our framework of choice for the following types of projects:

1. Static sites (that is, sites that can be deployed with pure HTML/CSS/JavaScript)
2. Small dynamic sites with a limited range of simple server-side functions **not** including faceted search, user administration, or admin interfaces

The following document records our recommended path forward for adopting Gatsby.

## Proof of concept and pilot

As a proof of concept, we tested Gatsby by refactoring the CPS SSCE project to make use of it. You can view that spike on the [`feature/jfc/test-drive-gatsbyjs` branch](https://github.com/datamade/cps-ssce-dashboard/tree/jfc/test-drive-gatsbyjs).

Following the proof of concept, Gatsby was piloted on the LISC CNDA project, both for the [awardee map](https://github.com/datamade/lisc-cnda-map) and the [application submission app](https://github.com/datamade/lisc-cnda). Those two repos provide good examples of real-world Gatsby projects.

## Prerequisite skills

The biggest obstacle to incorporating Gatsby into our standard stack is a lack of prerequisite skills among developers. Specifically, Gatsby requires that new developers be comfortable with:

- GraphQL
- ES6 (modern JavaScript)
- React

Lack of familiarity with GraphQL is not a pressing challenge, since Gatsby makes only very limited use of GraphQL. Based on our pilot project, we recommend allocating 2 hours for a developer to follow [The Fullstack Tutorial for GraphQL](https://www.howtographql.com/) when working on their first Gatsby project.

Lack of familiarity with ES6 and React is a more important challenge, since both tools are used extensively in Gatsby and neither tool integrates easily with our current stack. Based on our experience in the pilot project, it's particularly important that we invest time in learning ES6 separate from Gatsby projects, since ES6 is important for understanding the Gatsby and React documentation.

In sum, we make the following recommendations for developing prerequisite skills among our staff:

1. Adopt ES6 as our new standard for JavaScript, and invest R&D time in creating a templated build environment for using it with Django projects
2. Set aside ~2 hours per new dev for Gatsby projects for them to do the GraphQL tutorial
3. Do one (or both) of two things to encourage React learning:
    - Set aside ~4 hours per new dev for Gatsby projects for them to do the React and Gatsby tutorials
    - Try to lead some sort of company-wide Gatsby/React learning group, where we would all do the tutorial and come together to share challenges and lessons

## Maintenance outlook

From a maintenance perspective, there are two primary risks to recommending wide adoption of Gatsby:

1. The risk that Gatsby falls out of vogue, or stops being actively developed
2. The risk that our team will not have the expertise to maintain Gatsby in the future

We consider each of these risks in turn.

### 1. Will Gatsby stop being actively developed?

We believe it's unlikely that the Gatsby project will be abandoned within the next five years. It's hard to judge what the future will hold for new tools, especially in the JavaScript ecosystem, but Gatsby strikes us as a project that will be stable for the long-term future, given the [long list of well-funded users who have built their sites in Gatsby](https://www.gatsbyjs.org/showcase/) as well as the project's [80,000 dependent packages and 2,100 contributors on GitHub](https://github.com/gatsbyjs/gatsby).

In addition, React and GraphQL are very stable tools, particularly given the substantial support they receive from Facebook. Since Gatsby relies heavily on React and GraphQL, we can be sure that, even in a future where Gatsby becomes less well-supported, the foundation of React and GraphQL will continue to be a good investment for our team.

### 2. Will our team be able to support Gatsby in the long-term?

To us, this is a more concerning maintenance question than 1) above. Gatsby requires expertise in supporting tools that are not yet widely used at DataMade, particularly ES6 and React, and if for some reason we were to lose our employees with ES6/React expertise before we have the chance to build it up team-wide, it might be hard for the team to maintain existing projects.

Rather than discourage us from pushing forward with new tools, this maintenance risk indicates to us that we should invest in building capacity on our team in Gatsby's prerequisite tools as soon as possible. This determination is reflected the recommended next steps we outline in the [Prerequisite skills](#prerequisite-skills) section above.

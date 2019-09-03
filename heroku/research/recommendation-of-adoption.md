# Recommendation of adoption: Heroku

Over the course of the past two months, we've spent time evaluating different possibilities
for containerizing our applications in production. We evaluated:

- ECS (see [Hannah's notes](./hec-log.md))
- Heroku (see [Hannah's notes](./hec-log.md) and [Jean's notes](./jfc-log.md))
- Divio (see [Jean's notes](https://github.com/datamade/how-to/issues/23))

In addition, we proposed the possibility of building our own, more incremental
solution, using [Docker Machine and EC2](https://github.com/datamade/how-to/issues/32).
We did not evaluate this solution in detail, but it remains a possibility.

Ultimately, we recommend **moving forward with Heroku as our deployment platform for dynamic client apps**.
According to our research, Heroku does the best job of meeting as many of our
DevOps needs as possible, while being the most easy-to-use
solution that we considered. While using Heroku will be more expensive than AWS,
our current provider, we believe that we can safely forward this cost to our clients,
and that the benefit to developer productivity will offset the higher price.

We consider these needs in detail below, and explain the specifics of why we believe
Heroku to be the right fit for dynamic client apps at DataMade.

## Background: DevOps dreams

During a conversation in May 2019, the DevOps committee discussed and synthesized
our thoughts on [the ways our infrastructure is painful, and how we want to change
it](https://github.com/datamade/devops/issues/90#issuecomment-502196656). Our
focus areas of improvement included:

- [Containerization](#containerization)
- [Deployment scripts](#deployment-scripts)
- [DNS](#dns)
- [SSH](#ssh)
- [Logging](#logging)
- [Time to First Deploy](#time-to-first-deploy)
- [Permissioning](#permissioning)
- [Application cleanup](#application-cleanup)
- [Isolation](#isolation)

We consider each focus area in detail and explain how Heroku will address it.

### Containerization

**Problem**: Developer environments are containerized, but production environments are not.

Heroku provides first-class support for deploying containers in production with the
[`heroku.yml` config file](https://devcenter.heroku.com/articles/build-docker-images-heroku-yml). With
the proper configuration, Heroku will automatically build and push application
container images to its container registry, and trigger rebuilds of your application
using the latest version of the container image.

Other deployment providers do not offer the same level of container integration that Heroku does.
ECS requires you to maintain your own deployment pipeline for building and pushing
container images, as well as for restarting builds. (It also does not automatically
connect the containers to a load balancer, or automatically provision SSL certificates
for custom domains, as Heroku does.) Divio allegedly
supports containerized deployments, but the feature is so new that it is not
documented, and we were not able to get it up and running successfully.

### Deployment scripts

**Problem**: "Custom deployment scripts are hard to read, write, and maintain."

Heroku deployments are set up entirely through config files. In this way, the service abstracts
the process of pushing code to a remote host. Although some amount of infrastructure
setup (such as initializing the Heroku project and connecting it to GitHub) is
still necessary, all of the relevant operations are available in the [Heroku
CLI](https://devcenter.heroku.com/articles/heroku-cli), so while we will no longer
need to maintain deployment scripts for applications, we can instead script
the process of provisioning a new application.

As mentioned above, ECS still requires custom deployment scripts to build and
push container images. In addition, it requires extra AWS infrastructure, like
load balancers and Route53 hosted zones, in order to work, and this infrastructure
would either have to be set up by hand or (more likely) provisioned with yet
more deployment scripts. Divio purports to offer similar services as Heroku, but
they are undocumented and we were not able to get them to work.

### DNS

**Problem**: DNS is a central point of failure, and is configured separately from
our other infrastructure.

Heroku doesn't really address this problem, unfortunately. While we can use custom
domains with Heroku apps (and Heroku will automatically provision and manage SSL certificates)
we still need to register them with an external registrar.

ECS could mitigate this problem somewhat, since AWS offers [domain registration
services](https://aws.amazon.com/getting-started/tutorials/get-a-domain/) through
its Route53 service. This would at least mean that we could use the same DNS provider
as our infrastructure provider. Divio offers no solutions to this problem.

### SSH

**Problem**: "SSH access is required for provisioning an application", and also for viewing logs.

Heroku exposes SSH access to services through the Heroku CLI. With the Heroku CLI,
developers authenticate through the web app and then shell into running services
with the [`heroku ps:exec` command](https://devcenter.heroku.com/articles/exec).
Since `heroku ps:exec` uses SSH under the hood, the command can be used for tunneling
as well.

ECS has [no natively-supported solution for shelling into running
containers](https://github.com/aws/containers-roadmap/issues/187). However, since
ECS runs on EC2 instances, we could presumably continue to make use of [EC2 instance
connect](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-connect-methods.html)
to shell into EC2 instances, and access containers with bare Docker commands. Divio
[allegedly supports shelling into application
instances](http://support.divio.com/en/articles/735276-how-to-ssh-into-your-cloud-server)
but since we couldn't get a containerized application up and running on the platform
we weren't able to confirm this.

### Logging

**Problem**: "Logs are inconsistent, hard to find, and require SSH access to the server."

Heroku automatically streams all container output to its logging service.
Developers can access these logs in two ways: via the Heroku CLI or via the web app.
Using the CLI, developers can tail or stream logs with the `heroku logs` command.
These logs are filterable by team, application, and service name. Equivalent logs
can also be viewed on the admin dashboard for a project on the web app.

Heroku only stores the most recent 1,500 lines of any given log, and stores them
for a maximum of one week ([source](https://devcenter.heroku.com/articles/logging#log-history-limits)).
Additional logging can be configured via paid add-ons, but we expect that this
basic level of logging should meet the needs of the majority of our applications,
where we typically only use logs for active debugging.

ECS container logs can be [streamed to the AWS CloudWatch logging
service](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/using_awslogs.html).
These logs can then be viewed in the CloudWatch console, or piped into AWS Athena for
analysis. Note that while potentially more powerful than Heroku logs, ECS logs are more
cumbersome to configure up front, since they require an integration with an additional
AWS service.

Similar to Heroku, Divio exposes the [last 1,000 lines of container output
in their web app](http://support.divio.com/en/articles/735542-how-to-access-logs-for-your-cloud-sites).

### Time to first deploy (TTFD)

**Problem**: "Deployment takes too long."

Configuring a deployment to Heroku is very easy, requiring at most two config
files and a couple of CLI commands to set up a deployment pipeline. It took Hannah
three hours start-to-finish to read all of the relevant documentation and
set up a parallel instance of Dedupe.io on Heroku.

Setting up a deployment with ECS is substantially more difficult, as it requires
provisioning infrastructure for a number of additional Amazon services, including
ECR container repositories, an EC2 instance, an ELB Application Load Balancer,
Route53 hosted zones and records, and an ACM SSL certificate, to name a few. AWS
Fargate only minimally simplifies this process, since the only services it provisions
automatically are the underlying EC2 instances.

Configuring deployments with Divio is supposed to be similarly easy as Heroku,
but we weren't able to get a deployment up and running properly to confirm this.

### Permissioning

**Problem**: "User access is granted on a per-application basis, but it's also revoked on a per-application basis."

Permissions for all of the operations that Heroku supports for managing and inspecting
applications, including loggs, SSH, and deployment, are provisioned at the level of
Heroku accounts. DataMade developers can be granted access by adding their Heroku account to a
Heroku team; once removed from the Heroku team, developers would no longer be
able to view or manage applications in the web app or via the CLI.

ECS offers a similar permissioning scheme, although access to all resources is
configured via an IAM role. Divio offers similar permissioning to Heroku.

### Application cleanup

**Problem**: "Applications are hard to clean up."

Since Heroku apps are fully containerized and the underlying infrastructure
is abstracted away from the developer, cleaning them up is as simple as scaling
the number of web application dynos down to 0 (to turn off the application) or deleting
the project (to delete all infrastructure related to the application).

Cleaning up ECS apps is slightly more difficult, although still an improvement on
our current deployment pipeline. ECS apps can be easily stopped by scaling down
the number of active application containers to 0, but in order to fully remove
the application, the developer needs to clean up all of the application's
supporting infrastructure, including EC2 instances, load balancers, etc.

Divio applications can be deleted in a similar way as Heroku applications.

### Isolation

**Problem**: "Shared services introduce undesirable dependencies between colocated applications."

Since all three of the services we evaluated support containerized deployments,
they all necessarily solve the problem of app isolation.

## Other considerations

There are a few additional considerations that are important in evaluating any infrastructure
provider. While we didn't bring these up during our DevOps Dreams conversation,
we consider them below out of due diligence.

### Pricing

Heroku represents a significant increase in price from EC2. Our current deployment
practice recommends setting up two `t3.small` EC2 instances for an application,
one for staging and one for production, which comes out to roughtly $30
per month. (Sometimes we deploy staging apps on a shared staging server, which
roughly halves the monthly cost of hosting, but this practice is probably not stable in
the long run and contributes to environment isolation problems on the staging server.)

To deploy a typical client application on Heroku, we expect that we'll want at least
one Standard 1x dyno to run the web application ($25/mo) and one Standard Heroku
Postgres instance for the database ($50/mo). If the application requires asynchronous
processing, we may additionally need a second Standard 1x dyno to run a worker process
and a Premium Heroku Redis instance for a queue ($15/mo). This makes the estimated monthly
cost of a production application somewhere in the range of $75-$115/mo.

Staging and preview applications on Heroku can make use of free tier add-ons for their
databases and queues, but they will need to use Hobby dynos ($7/mo) for web and worker services.
Building and releasing new container images also uses Hobby dyno resources. However, since Heroku
prorates these dynos to the second, and since we can easily turn off staging applications when
the app isn't under heavy development, we expect the total cost of these environments to be about
$15/mo in the worst case, which is negligible compared to the cost of production environments.

An additional consideration is that the pricing for AWS has historically been very
stable, often decreasing over time. As a newer service, the pricing for Heroku is
less reliable. Switching to Heroku increases the risk that Heroku will raise its
prices unexpectedly.

### Maintenance outlook

There are two pertinent maintenance questions when switching infrastructure providers:

1. How long can we expect the provider to remain stable and cost-effective?
2. How hard will it be to maintain existing applications on our old infrastructure provider
   while we switch to a new one?

We consider these questions in turn.

#### 1. How long can we expect the provider to remain stable and cost-effective?

Heroku has been under active development since 2007 and has been owned by Salesforce.com
since 2010. This makes it about the same age as AWS. From a stability perspective,
we would be surprised if the company folded in the next five years.

Cost-effectiveness is a bigger risk with Heroku than with AWS. Historically, the pricing
for Heroku has changed much more drastically than the pricing for AWS. However,
since we can forward most of this cost to our clients, and since the cost of hosting
is small compared to the cost of developing an application, we think this tradeoff
is worth it.

#### 2. How hard will it be to maintain existing applications on our old infrastructure provider while we switch to a new one?

DataMade has been deploying applications on AWS for over five years. Because of
this long history, we expect to maintain some number of legacy AWS applications
for the foreseeable future.

At this point, our knowledge of AWS is stable. We mostly use comparatively
old services, including EC2 (launched 2006) and CodeDeploy (launched 2014). Neither
of these services changes much year-to-year compared to newer services like
Lambda and ECS. In addition, [our documentation](https://github.com/datamade/deploy-a-site/)
for the way we use these services is extensive.

As we start to build new applications in Heroku, we expect to flesh out new
Heroku-specific documentation while maintaining our old documentation for the purposes of operating
existing apps. The maintenance overhead for our existing client applications is
minimal and we expect this to continue in the future for our AWS-deployed apps.

### Secrets management

How do we thread secrets into running applications without keeping them under
version control?

## Transition plan

How will we transition to Heroku? What are our next steps?
# Spike: Running locally without AWS access

Have tried a few things to run without requiring AWS access.

Kind of half-succeeded but it does require someone with AWS to download the lambda layers required.  It also requires
Docker Compose, AWS SAM (Serverless Application Model) CLI and Localstack's SAM Local CLI.

The rough workflow would be:

1. Install requirements within src directory
2. Run docker compose to get localstack running
3. Build Lambda with SAM and cache lambda layers to lambda-layers directory
4. Invoke Lambda with SAM Local pointing to the lambda-layers cache directory

As one can see, this is not really workable and requires setup and knowledge of a lot of different tools.  When the
Lambda runtime is upgraded in future, it will also require an engineer with AWS access to cache the lambda-layer and
commit to this directory.

In the end it will probably just be better to use pytest to make sure no silly mistakes have been made in the Canary
source code.  The pytest setup will need to stub the AWS Synthetics dependencies or perhaps provide a bridge
to an alternative implementation that can run locally.


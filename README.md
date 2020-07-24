# AWS Account Metadata HTML Generator

This serverless function will look at an existing AWS organization and generate an HTML file with clickable roleswitch URLs. 

## Requirements

* [Serverless framework](https://serverless.com)
* [Docker](https://www.docker.com) (Optional, needed if you want to Dockerize the dependency deployment with Serverless)
* IAM privileges in the Organizations account - Serverless will create additional roles needed to execute Lambda and granting read privileges to the S3 bucket

## Deployment

Copy the file `env.yml.example` and make your own named `env.yml`. Modify accordingly to fit your needs. Note the tree structure of the file; this is so that you can use the `--stage` flag in Serverless framework to deploy to different accounts. Stage defaults to `dev`

```bash
sls deploy --stage dev|account1|account2
```

## Running
Execute either directly from Lambda console or by using CLI. 

```bash
sls invoke -f main --stage [stagename]
```
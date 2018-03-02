# Cognoma core-service

This repository, under the umbrella of Project Cognoma
(https://github.com/cognoma), holds the source code, under open source
license, of a runnable django rest API, a component in the overall system
specified in Project Cognoma.

## Getting started

Make sure to fork [this repository on
 +GitHub](https://github.com/cognoma/core-service "cognoma/core-service on
 +GitHub") first.

### Prerequisites

- Docker - tested with 1.12.1
- Docker Compose - tested with 1.8.0

## Starting up the service

```sh
docker-compose up
```

Sometimes the postgres image takes a while to load on first run and the Django server starts up first. If this happens just ctrl+C and rerun `docker-compose up`

The code in the repository is also mounted as a volume in the core-service container. This means you can edit code on your host machine, using your favorite editor, and the django server will automatically restart to reflect the code changes.

The server should start up at http://localhost:8080/, see the [API docs](https://github.com/cognoma/core-service/blob/master/doc/api.md).

## Swagger UI
Accessing the root API endpoint (ex: http://localhost:8080/) will bring up the [Swagger UI](https://github.com/marcgibbons/django-rest-swagger) for viewing the API.

**Note:** swagger will only display endpoints that you are authorized to
view. In order to authenticate, go to the top right corner and click
`Authorize`. Where it says `api_key`, type in `Bearer
<your_random_slug_here>` and hit enter to authenticate for the rest of the session.

## Running tests locally

Make sure the service is up first using `docker-compose up` then run:

```sh
docker-compose exec core python manage.py test
```

## Loading cancer static data

To load data, again with service up run:

```sh
docker-compose exec core bash
python manage.py acquiredata
python manage.py loaddata
```

To verify, run `curl http://localhost:8000/diseases/` to get a list of all diseases.

Or, run `curl http://localhost:8000/samples?limit=10` to view data for 10 samples.

## Deployment

### Prerequisites

This project is deployed within the Greene Lab AWS account. To be able
to deploy this project you will need to:
1. Be invited to the account.
2. Receive an AWS access key and secret key.

### Logging Into ECR

This project leverages
[AWS Ec2 Container Service (ECS)](https://aws.amazon.com/ecs/details).
ECS provides a private container registry called the
[Ec2 Container Repository (ECR)](https://aws.amazon.com/ecr/).
To be able to push Docker images to this repository you will first need to
get a login with:
```sh
aws ecr get-login --region us-east-1
```
and then run the output of that command. It will look something like:
```sh
docker login -u AWS -p <A_GIANT_HASH> -e none https://589864003899.dkr.ecr.us-east-1.amazonaws.com
```

### Building, Tagging, and Pushing the Container

This project uses two containers: one for Nginx and one for the core-service.
You will probably be deploying only the core-service unless you have modified
`config/prod/nginx.conf`.

#### Core Service Container

Run these commands:
```
docker build --tag cognoma-core-service .
docker tag cognoma-core-service:latest 589864003899.dkr.ecr.us-east-1.amazonaws.com/cognoma-core-service:latest
docker push 589864003899.dkr.ecr.us-east-1.amazonaws.com/cognoma-core-service:latest
```

#### Nginx Container

Run these commands:
```
docker build --tag cognoma-nginx --file config/prod/Dockerfile_nginx .
docker tag cognoma-nginx:latest 589864003899.dkr.ecr.us-east-1.amazonaws.com/cognoma-nginx:latest
docker push 589864003899.dkr.ecr.us-east-1.amazonaws.com/cognoma-nginx:latest
```

### Restarting the ECS Task

Navigate to
[Cognoma's ECS Tasks Page](https://console.aws.amazon.com/ecs/home?region=us-east-1#/clusters/cognoma/tasks)
and select the tasks corresponding to the container you are deploying.
The tasks will have a **Task Definition** like either `cognoma-core-service:X`
or `cognoma-nginx:X` which can be used to determine which are the correct
tasks. Once you have selected the correct tasks click the **Stop** button.
This will cause the tasks to be stopped and ECS will restart them with the
new version of the container you have pushed. Therefore you're now done.

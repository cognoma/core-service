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
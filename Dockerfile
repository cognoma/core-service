FROM python:3.5.1

MAINTAINER "Project Cognoma"

# System packages
RUN apt-key update && apt-get update
# Supervisor for running application in production
RUN apt-get install supervisor -y
# Clean up package manager
RUN apt-get autoremove -y
RUN rm -rvf /var/cache/apt


# Environment variables
ENV PYTHONUNBUFFERED 1


# Directories
RUN mkdir /code
WORKDIR /code


# Python environment
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt


# Mount application code
ADD . /code/

# Default entrypoint
ENTRYPOINT "/code/scripts/run_prod.sh"

#!/usr/bin/env bash
eval $(aws ecr get-login --region $AWS_DEFAULT_REGION)
docker push $AWS_ECR_ENDPOINT.dkr.ecr.us-east-1.amazonaws.com/cognoma-core-service:$CIRCLE_SHA1
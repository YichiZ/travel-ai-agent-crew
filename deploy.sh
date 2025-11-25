#!/bin/bash
export AWS_REGION=us-east-1
export AWS_ACCOUNT_ID=<YOUR_AWS_ACCOUNT_ID>
export REGISTRY_NAME=travel-ai-agent-crew-api
export TAG=1

echo "Logging in to ECR"
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

echo "Create repository if it doesn't exist"
aws ecr create-repository --repository-name $REGISTRY_NAME --region $AWS_REGION

echo "Building image"
docker build --no-cache --platform=linux/amd64 -t $REGISTRY_NAME:$TAG .

echo "Tagging image"
docker tag $REGISTRY_NAME:$TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REGISTRY_NAME:$TAG

echo "Pushing image to ECR"
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REGISTRY_NAME:$TAG

# Run the container locally
# docker run -p 8080:8080 travel-ai-agent-crew-api:1
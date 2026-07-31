#!/bin/bash

set -x
BUILD_DIR=${PWD}
DOCKER_BUILDKIT=1 docker build -f Dockerfile_lambda --target artifact --output type=local,dest=. .
zip -gr ${BUILD_DIR}/lambda-deployment-package.zip . -i "crash_reverser_lambda.py" "query.txt" --exclude ".venv/*" "*/__pycache__/*"

#!/bin/bash

set -e

if [ $# -eq 0 ]
  then
    echo "Please provide a build number and optional repository to push to"
    exit
fi

if [ -z "$1" ]
  then
    echo "No build number supplied"
else
  export BUILD_NO=$1
fi

export HOST="$2"

if [ -z "$2" ]
  then
    export HOST="docker.io/edamsoft/turo"
fi

export VERSION=${BUILD_NO}-$(git rev-parse --short HEAD)
export IMAGE_TAG="${HOST}:${VERSION}"
docker build -t ${IMAGE_TAG} .
echo "Built image ${IMAGE_TAG}"
docker push "${IMAGE_TAG}"
echo "Pushed image"
echo "${IMAGE_TAG}"

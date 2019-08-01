#!/bin/zsh


docker build -f dockerfiles/masterDockerfile -t pmaster .
docker build -f dockerfiles/serverDockerfile -t pserver .
docker build -f dockerfiles/clientDockerfile -t pclient .
#!/bin/bash
set -x

echo "Installing docker client"

wget -q  https://get.docker.com/builds/Linux/x86_64/docker-17.03.0-ce.tgz
tar xzf docker-17.03.0-ce.tgz docker/docker
mv docker/docker /usr/bin/docker
rm -rf docker-17.03.0-ce.tgz docker/

#wget -q get-docker.com -O get-docker.sh
#sh get-docker.sh

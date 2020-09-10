#!/bin/bash
set -x

echo "Installing docker client"

wget -q https://download.docker.com/linux/static/stable/x86_64/docker-19.03.12.tgz 
tar xzf docker-19.03.12.tgz docker/docker
mv docker/docker /usr/bin/docker
rm -rf docker-19.03.12.tgz docker/

#wget -q get-docker.com -O get-docker.sh
#sh get-docker.sh

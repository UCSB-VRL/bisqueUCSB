#!/bin/sh
echo "HOSTNAME"
hostname

echo "ENV"
printenv

echo "command"
echo "./dist/MyData $@"

exec ./dist/MyData $@


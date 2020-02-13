#!/bin/sh
echo "HOSTNAME"
hostname

echo "ENV"
printenv

echo "command"
echo "./dist/MetaData $@"

exec ./dist/MetaData $@


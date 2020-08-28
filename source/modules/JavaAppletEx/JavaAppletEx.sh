#!/bin/sh
echo "HOSTNAME"
hostname

echo "ENV"
printenv

echo "command"
echo "./dist/JavaAppletEx $@"

exec ./dist/JavaAppletEx $@


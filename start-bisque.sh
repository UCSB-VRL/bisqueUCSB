#!/bin/bash
cd /source
bq-admin server start
sleep 10
tail -f bisque_8080.log

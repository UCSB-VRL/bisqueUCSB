#!/bin/bash

function  usage() {
  echo "usage: $0 [-uname:pass] DBaddr"
  echo "  $0  http://localhost:8080/ds/datasets"
  exit
}

if [ $# -lt 1 ] ; then 
  usage
fi
USER="admin:testme"
while getopts "u:" options
do 
  case $options in
  u) USER="$OPTARG" ;;
  -) shift; break ;;
  ?) usage; exit 2 ;;
  esac
done
shift $(($OPTIND - 1))

RESOURCE=$1
curl -k -u $USER -X DELETE -H 'Content-type: text/xml'  $RESOURCE


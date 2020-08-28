#!/bin/bash

function  usage() {
  echo "usage: $0 [-uname:pass] filename dbaddr"
  echo "  $0 dataset.xml http://localhost:8080/ds/datasets"
  exit
}
if [ $# -lt 2 ] ; then 
  usage
fi
#USER="admin:testme"
while getopts "u:" options
do 
  case $options in
  u) EXTRA="-u $OPTARG" ;;
  -) shift; break ;;
  ?) usage; exit 2 ;;
  esac
done
shift $(($OPTIND - 1))

FILE=$1
RESOURCE=$2

R=$(cat $FILE)
echo "Sending $R -> $RESOURCE"
echo "curl -k $EXTRA -X POST -H 'Content-type: text/xml' -d @- $RESOURCE < $FILE
"
curl -k $EXTRA -X PUT -H 'Content-type: text/xml' -d @- $RESOURCE < $FILE


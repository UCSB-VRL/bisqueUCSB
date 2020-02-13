#!/bin/bash
VERBOSE=0

function  usage() {
  echo "usage: $0 [-uname:pass] filename dbaddr"
  echo "  $0 dataset.xml http://localhost:8080/ds/datasets"
  exit
}
function verbose () {
    if [ $VERBOSE -eq 1 ]; then
      echo $*
   fi
}

if [ $# -lt 2 ] ; then 
  usage
fi
USER="admin:testme"
while getopts "vu:M:E:" options
do 
  case $options in
  u) EXTRA="$EXTRA -u $OPTARG" ;;
  -) shift; break ;;
#  ?) usage; exit 2 ;;
  v) VERBOSE=1;;
  M) EXTRA="$EXTRA -H \"Authorization: Mex $OPTARG\"";;
  E) EXTRA="$EXTRA -H 'If-Match: $OPTARG'";;
  esac
done
shift $(($OPTIND - 1))

FILE=$1
RESOURCE=$2

R=$(cat $FILE)
verbose "Sending $R -> $RESOURCE"
verbose "curl -k $EXTRA -X POST $MEX -H 'Content-type: text/xml' -d @- $RESOURCE < $FILE
"
curl -k $EXTRA -X POST -H 'Content-type: text/xml' -d @- $RESOURCE < $FILE


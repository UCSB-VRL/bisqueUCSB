#!/bin/bash

if [ "$1" == "bootstrap" ] ; then
    #/builder/build-bisque.sh
    /builder/run-bisque.sh $@

else
    exec /bin/bash
fi

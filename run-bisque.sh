#!/bin/bash
set -x
CMD=$1; shift
INDEX=${PY_INDEX:=https://biodev.ece.ucsb.edu/py/bisque/d8/+simple}
CONFIG=./config/site.cfg
export  PIP_INDEX_URL=$INDEX
reports=$(pwd)/reports/
BUILD=/builder
BQHOME=${BQHOME:=/source/}
VENV=${VENV:=/usr/lib/bisque}

if [ ! -d ${reports} ]; then
    mkdir -p ${reports}
fi



echo "In " $(pwd) "BISQUE in" $BQHOME "Reports in" $reports
cd $BQHOME


# To be used during container builds
if [ "$CMD" = "build" ] ; then
    let returncode=0
    echo "BUILDING"
    if [ ! -d ${VENV} ] ; then
        virtualenv ${VENV}
    fi
    source ${VENV}/bin/activate

    ls -l ${BUILD}/build-scripts.d
    for f in ${BUILD}/build-scripts.d/*.sh; do
        echo "Executing $f"
        if [ -f $f ] && $f ; then
            mv $f $f.finished
        else
            echo "FAILED $f"
            let returncode=2
        fi
    done
    if [ $returncode -ne 0 ] ; then
        echo "BUILD Failed"
    fi
    exit $returncode
fi

source ${VENV}/bin/activate

if [ "$CMD" = "bootstrap" ] ; then
    echo "BOOTSTRAPPING"
    #/usr/share/python/bisque/bin/pip install -U pip==8.0.3 setuptools
    #/usr/share/python/bisque/bin/pip install -r extras.txt
    umask 0002
    ls -l
    if [ -d ${BUILD}/boot-scripts.d ]; then
        ls -l ${BUILD}/boot-scripts.d
        for f in ${BUILD}/boot-scripts.d/B*.sh; do
            echo "Executing **BOOT $f **"
            [ -f "$f" ] && bash  "$f"
        done
    fi
    CMD=$1; shift
fi

if [ "$CMD" = "pylint" ] ; then
    echo "Pylint testing"
#    if [ ! -f  ${BQHOME}config/site.cfg ] ; then
    if [ ! -f  config/site.cfg ] ; then
        echo "Please run bootstrap first i.e. bootstrap pylint"
        exit 1
    fi
    export PYLINTHOME=.
    ${BIN}pip install -i $INDEX pylint bisque_pylint_plugin
    #paver -f /usr/share/bisque/pavement.py pylint  $@
    ARGS=""
    while [[ "$1" == --* ]] ; do
        ARGS="$ARGS $1" ; shift
    done
    ${BIN}paver -f pavement.py pylint --output-format=parseable --disable=R,C,W,I $ARGS >${reports}pylint.log
    CODE=$?
    CMD=$1; shift
fi

if [ "$CMD" = "unit-tests" ] ; then
    echo "Unit  testing $@"
#    if [ ! -f  ${BQHOME}config/site.cfg ] ; then
    if [ ! -f  config/site.cfg ] ; then
        echo "Please run bootstrap first i.e. bootstrap unit-tests"
        exit 1
    fi
    ARGS=""
    while [[ $1 == --* ]] ; do
        ARGS="$ARGS $1" ; shift
    done

    ${BIN}pip install pytest
    ${BIN}pip install -e ./pytest-bisque
    python -m pytest  -m unit --junitxml=${reports}pytest-unit.xml $ARGS

    CODE=$?
    CMD=$1; shift
fi

if [ "$CMD" = "function-tests" ] ; then
    echo "Functional  testing $@"
    if [ ! -f  ./config/site.cfg ] ; then
        echo "Please run bootstrap first i.e. bootstrap functional-tests"
        exit 1
    fi
    ARGS=""
    while [[ $1 == --* ]] ; do
        ARGS="$ARGS $1" ; shift
    done

    ${BIN}pip install pytest
    ${BIN}pip install ./pytest-bisque
    pytest -m functional --junitxml=${reports}pytest-functional.xml $ARGS

    CODE=$?
    CMD=$1; shift
fi

if [ "$CMD" = "start" ] ; then
    #sleep 10  # wait for db to be ready
#    if [ ! -f  ${BQHOME}config/site.cfg ] ; then
    if [ ! -f  config/site.cfg ] ; then
        echo "Please run bootstrap first i.e. bootstrap start"
        exit 1
    fi
    if [ -d ${BUILD}/start-scripts.d ]; then
        ls -l ${BUILD}/start-scripts.d
        for f in ${BUILD}/start-scripts.d/R*.sh; do
            echo "Executing ** START $f **"
            [ -f "$f" ] && bash  "$f"
        done
    fi
    #exec /builder/start-bisque.sh
fi

if [ "$CMD" = "bash" ] ; then
    exec /bin/bash
fi

if [ "$CMD" = "" ] ; then
    #    exit $CODE    # Exit with this code on error from pytest or pylint
    exit 0
fi

echo "executing $CMD $@"
exec "$CMD" $@

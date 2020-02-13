#!/bin/bash -e

BOOST_DIR=/usr/include/boost
YASMIC_DIR=./

CCFILES="components.cc max_flow.cc orderings.cc searches.cc shortest_path.cc
spanning_trees.cc statistics.cc"
OFILES=`echo ${CCFILES} | sed -e 's/\.cc/\.o/g'`

CFLAGS="-O2 -fPIC -c -I${BOOST_DIR} -I${YASMIC_DIR}"

function echocmd {
	echo $@
	$@
}

for file in ${CCFILES}; do
	echocmd g++ $CFLAGS $file
done

echocmd ar rc libmbgl-linux-64.a ${OFILES} 
	
echocmd rm ${OFILES}	

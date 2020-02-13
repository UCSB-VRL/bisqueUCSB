CC=g++
MPC=mpiCC
mpiP_DIR=/cluster/home/berutten/mpiP-3.1.1
CVFLAGS=`pkg-config --cflags opencv` `pkg-config --libs opencv`
FLAGS=-Wall -g #-O2

RWalk : main.o imageIO.o cells.o RandWalk.o
	$(CC) $(CVFLAGS) $(FLAGS) main.o imageIO.o cells.o RandWalk.o -o RWalk

main.o : main.cpp imageIO.h cells.h RandWalk.h common.h
	$(CC) $(CVFLAGS) $(FLAGS) -c main.cpp 

imageIO.o : imageIO.cpp imageIO.h common.h Args.h
	$(CC) $(CVFLAGS) $(FLAGS) -c imageIO.cpp 

cells.o : cells.cpp cells.h common.h Args.h
	$(CC) $(FLAGS) -c cells.cpp 

RandWalk.o : RandWalk.cpp RandWalk.h cells.h common.h Args.h
	$(CC) $(FLAGS) -c RandWalk.cpp 

clean : 
	rm -f *#
	rm -f *~
	rm -f *.o 
	rm -f *.gch	
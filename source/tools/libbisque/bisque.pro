######################################################################
# Manually generated !!!
# libbisque 1.0 Project file
# run: 
#   qmake bisque.pro - in order to generate Makefile for your platform
#   make - to compile the library
#
#
# Copyright (c) 2005-2013, Center for Bio-Image Informatics, UCSB
#
# To generate Makefile on any platform:
#   qmake bisque.pro
#
# To generate VisualStudio project file:
#   qmake -t vcapp -spec win32-msvc2005 bisque.pro
#   qmake -t vcapp -spec win32-msvc.net bisque.pro
#   qmake -t vcapp -spec win32-msvc bisque.pro
#   qmake -spec win32-icc bisque.pro # to use pure Intel Compiler
#
# To generate xcode project file:
#   qmake -spec macx-xcode bisque.pro 
#
# To generate Makefile on MacOSX with binary install:
#   qmake -spec macx-g++ bisque.pro
#
######################################################################


#---------------------------------------------------------------------
# configuration: editable
#---------------------------------------------------------------------

TEMPLATE = lib
VERSION = 0.1.0

CONFIG += staticlib
CONFIG += release
CONFIG += warn_off

BQ_SRC  = ./src

#---------------------------------------------------------------------
# libbisque
#---------------------------------------------------------------------

INCLUDEPATH += $$BQ_SRC

HEADERS += $$BQ_SRC/bisqueAccess.h $$BQ_SRC/bisqueWebAccess.h 
SOURCES += $$BQ_SRC/bisqueAccess.cpp $$BQ_SRC/bisqueWebAccess.cpp 
FORMS += $$BQ_SRC/bisqueAccess.ui $$BQ_SRC/bisqueWebAccess.ui

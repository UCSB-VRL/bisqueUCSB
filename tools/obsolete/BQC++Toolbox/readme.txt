
C++ BisquikToolbox for Trolltech Qt

Copyright (c) 2008, Bio-Image Informatic Center, UCSB

To generate Makefile on any platform:
   qmake bisquik.pro

To generate VisualStudio project file:
   qmake -t vcapp -spec win32-msvc2005 bisquik.pro
   qmake -t vcapp -spec win32-msvc.net bisquik.pro
   qmake -t vcapp -spec win32-msvc bisquik.pro

To use Intel Compiler:
   qmake -spec win32-icc bisquik.pro

To generate xcode project file:
   qmake -spec macx-xcode bisquik.pro

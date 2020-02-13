Feature Extractors for the Bisque Feature Server
================================================


Here we have binary code for feature extraction in its original language, 
commonly c/c++, along with python wrappers (ctypes) ready for use by the
Bisque feature server. The "extractors" can be placed directly into Bisque
path "bisque/bqserver/bq/features/controllers/extractors" and rebuilt.

The "extractors/build" directory contains overarching makefiles and visual
studio files grouping all available extractors along with required third party 
libbraries. 

Each extractor should contain a source directory "src" with all necessary 
source files, a Makefile and a Visual Studio project files. Also a compiled 
library directory "lib" where the built files will be generated. 



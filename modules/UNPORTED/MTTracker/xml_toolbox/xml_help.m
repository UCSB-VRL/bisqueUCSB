% ----------------------------
%  XML TOOLBOX FOR MATLAB 3.2
% ----------------------------
%
% FUNCTIONS:
%  xml_format       converts a Matlab variable into XML string
%  xml_formatany    converts a Matlab variable into XML string with attributes
%  xml_parse        parses & converts XML string into Matlab structure
%  xml_parseany     parses & converts XML string into Matlab structure with attributes
%  xml_save         saves a Matlab variable/structure in XML format in a file
%  xml_load         loads the .xml file written with xml_save back into a variable
%  xml_help         this file, displays info about available xml_* commands
%  demo_xml         demonstrates step-by-step use of the XML Toolbox commands
%  tests/xml_tests  tests the xml toolbox by writing/reading a number of xml test files
%  strsplit         utility function which splits a string at specified characters
%  unblank          utility function which removes leading and trailing spaces
%
% MANUAL:
%  doc/xml_toolbox.pdf   (present only in standalone version)
%
% RELATED:
%  xmlread, xmlwrite, xslt (shipped with Matlab from version 6.5)
%
% Further information can be obtained by using the help command on a specific
% function, e.g. help xml_format, or by starting demo_xml, or by visiting
% http://www.geodise.org
 
% Copyright (c) 2002-2005, The Geodise Project, University of Southampton
% Author: Dr Marc Molinari <m.molinari@soton.ac.uk>
% $Revision: 1.11 $ $Date: 2005/08/26 09:41:37 $
 

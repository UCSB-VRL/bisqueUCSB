 
%XML_TOOLBOX_VERSION  Returns the current version of the XML Toolbox for Matlab
%
% SYNTAX        Version = xml_toolbox_version
%               Version = xml_toolbox_version( ['numeric'|'full'] )
%
% INPUT
%   [option]    'numeric' returns numerical TB version
%               'full' returns a full string with xml and Matlab version numbers
%               e.g. xmltb-3.1.3_matlab-6.5
%
% OUTPUT
%   Version     text string with version of the current XML Toolbox of the form
%               MAJOR.MINOR.POINT (e.g. '3.2.0')
%               If 'numeric' is specified as option, the version will be returned
%               as numerical value MAJOR.MINOR .
%               If 'full' is specified as option, a full version string will be
%               returned e.g. "xmltb-3.2.0_matlab-6.5.0.18000a-(R13)"
%
% SEE ALSO
%   xml_help
 
%  Copyright (c) 2005 Geodise Project, University of Southampton
%  XML Toolbox for Matlab, http://www.geodise.org
%  Dr Marc Molinari <m.molinari@soton.ac.uk>
%  $Revision: 1.3 $ $Date: 2007/03/22 15:40:09 $
 

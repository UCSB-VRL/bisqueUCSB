###############################################################################
##  Bisquik                                                                  ##
##  Center for Bio-Image Informatics                                         ##
##  University of California at Santa Barbara                                ##
## ------------------------------------------------------------------------- ##
##                                                                           ##
##     Copyright (c) 2007 by the Regents of the University of California     ##
##                            All rights reserved                            ##
##                                                                           ##
## Redistribution and use in source and binary forms, with or without        ##
## modification, are permitted provided that the following conditions are    ##
## met:                                                                      ##
##                                                                           ##
##     1. Redistributions of source code must retain the above copyright     ##
##        notice, this list of conditions, and the following disclaimer.     ##
##                                                                           ##
##     2. Redistributions in binary form must reproduce the above copyright  ##
##        notice, this list of conditions, and the following disclaimer in   ##
##        the documentation and/or other materials provided with the         ##
##        distribution.                                                      ##
##                                                                           ##
##     3. All advertising materials mentioning features or use of this       ##
##        software must display the following acknowledgement: This product  ##
##        includes software developed by the Center for Bio-Image Informatics##
##        University of California at Santa Barbara, and its contributors.   ##
##                                                                           ##
##     4. Neither the name of the University nor the names of its            ##
##        contributors may be used to endorse or promote products derived    ##
##        from this software without specific prior written permission.      ##
##                                                                           ##
## THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS "AS IS" AND ANY ##
## EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED ##
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE, ARE   ##
## DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE FOR  ##
## ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL    ##
## DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS   ##
## OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)     ##
## HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,       ##
## STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN  ##
## ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE           ##
## POSSIBILITY OF SUCH DAMAGE.                                               ##
##                                                                           ##
###############################################################################
"""
SYNOPSIS
========


DESCRIPTION
===========

"""
class BQException(Exception):
    "Base Bisquik Exception"

class IllegalOperation(BQException):
    pass

class ConfigurationError (BQException):
    '''Problem was found with the configuration'''
    pass

class EngineError(BQException):
    '''The Module Engine exception'''
    def __init__(self, msg='', stdout=None, stderr=None, exc = None):
        super(EngineError, self).__init__(msg)

        self.stdout = stdout
        self.stderr = stderr
        self.exc    = exc

    def __str__(self):
        msg = [super(EngineError, self).__str__ ()]
        if self.stdout:
            msg.append('stdout = %s' % self.stdout)
        if self.stderr:
            msg.append('stderr = %s' % self.stderr)
        if self.exc:
            msg.append('exception = %s' % self.exc)
        return '\n'.join(msg)


class BadValue(BQException):
    '''The Module Engine exception'''
    def __init__(self, msg, obj=None):
        super(BadValue, self).__init__(msg)
        self.obj = obj
    def __str__ (self):
        return "BadValue("+str(type(self.obj)) + ")"


class DuplicateFile(BQException):
    "A duplicate file or resource detected"

class RequestError(BQException):
    '''Used for any request that cannot be satisfied
    For example: HTTP requests to services
    '''

class ServiceError(BQException):
    '''Any error during in a service'''

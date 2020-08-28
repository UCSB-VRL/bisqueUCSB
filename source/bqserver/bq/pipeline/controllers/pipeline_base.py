###############################################################################
##  BisQue                                                                   ##
##  Center for Bio-Image Informatics                                         ##
##  University of California at Santa Barbara                                ##
## ------------------------------------------------------------------------- ##
##                                                                           ##
##     Copyright (c) 2015 by the Regents of the University of California     ##
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
Pipeline base for importers

"""

# default imports
import logging

log = logging.getLogger("bq.pipeline.base")


__all__ = [ 'PipelineBase' ]

#---------------------------------------------------------------------------------------
# Pipeline base
#
# field "data" will store the pipeline as follows:
#
# {
#   "__Header__" :
#    {
#      <attr_name> : <attr_value>,
#      ...
#      <attr_name> : <attr_value>
#    },
#   <step_id> :
#    {
#      "__Label__" : <label for step>,
#      "__Meta__"  : <attr_value>,
#      <attr_name> : <attr_value>,
#      ...
#      <attr_name> : <attr_value>
#    },
#   <step_id> : ...,
#   ...
#   <step_id> : ...
# }
#
# "<attr_value>" can be single value or dictionary (nested)
#---------------------------------------------------------------------------------------

class PipelineBase(object):

    name = ''
    version = '1.0'
    ext = ''
    mime_type = 'text/plain'

    def isloaded(self):
        return self.data is not None

    # functions to be defined in the individual drivers

    def __init__(self, uniq, resource, path, **kw):
        self.path = path
        self.resource = resource
        self.uniq = uniq
        self.url = kw['url'] if 'url' in kw else None
        self.data = None

#*******************************************************************************
# Author: Dima Fedorov <dima@dimin.net>
# Copyright Center for Bio-Image Informatics, UCSB
#*******************************************************************************

#from lxml import etree

from bq.blob_service.controllers.blob_plugins import ResourcePlugin

class TextPlugin (ResourcePlugin):
    '''Text file resource''' 
    name = "TextPlugin"  
    version = '1.0'
    ext = 'txt'
    resource_type = 'text'
    mime_type = 'text/plain'
    
    def __init__(self):
        pass

class AsciiTextPlugin (TextPlugin):
    '''Text file resource''' 
    ext = 'ascii'
    mime_type = 'text/plain'

class Ascii2TextPlugin (TextPlugin):
    '''Text file resource''' 
    ext = 'asc'
    mime_type = 'text/plain'

class Utf8TextPlugin (TextPlugin):
    '''Unicode Text file resource''' 
    ext = 'utf8'
    mime_type = 'text/plain; charset=utf-8'

class UnicodeTextPlugin (TextPlugin):
    '''Unicode Text file resource''' 
    ext = 'utxt'
    mime_type = 'text/plain'

class ChineseTextPlugin (TextPlugin):
    '''Chinese Text File resource''' 
    ext = 'zw'
    mime_type = 'text/plain'

class HanziTextPlugin (TextPlugin):
    '''Hanzi Text File resource''' 
    ext = 'hz'
    mime_type = 'text/plain'

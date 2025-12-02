from io import BytesIO
from lxml import etree
import os
import logging
log = logging.getLogger(__name__)

class AbstractArchiver():

    def getContentType(self):
        return 'application/octet-stream'

    def getFileExtension(self):
        return '.xml'
    
    def beginFile(self, file):
        if 'content' in file and file.get('content') is not None:
            content = file.get('content')
            if isinstance(content, str):
                content = content.encode('utf-8')
            self.reader = BytesIO(content)
            self.reader.seek(0, 2)
            self.fileSize = self.reader.tell()
            self.reader.seek(0)
        
        #elif 'xml' in file and file.get('path') is None:
        #    xml_content = etree.tostring(file.get('xml'), encoding='utf-8')
        #    self.reader = BytesIO(xml_content)
        #    self.reader.seek(0, 2)
        #    self.fileSize = self.reader.tell()
        #    self.reader.seek(0)

        else:
            self.reader = open(file.get('path'), 'rb')
            self.reader.seek(0, 2)
            self.fileSize = self.reader.tell()
            self.reader.seek(0)

        return
    
    def readBlock(self, block_size):
        return self.reader.read(block_size)
    
    def EOF(self):
        return self.reader.tell() == self.fileSize
    
    def endFile(self):
        self.reader.close()
        return
    
    def readEnding(self):
        return b''
    
    def close(self):
        return
    
    def destinationPath(self, file):
        log.info(f"--- destination path is {file.get('outpath')}")
        return file.get('outpath')

class ArchiverFactory():
    
    from bq.export_service.controllers.archiver.tar_archiver import TarArchiver
    from bq.export_service.controllers.archiver.zip_archiver import ZipArchiver
    from bq.export_service.controllers.archiver.gzip_archiver import GZipArchiver
    from bq.export_service.controllers.archiver.bz2_archiver import BZip2Archiver

    supportedArchivers = {
        'tar'  :   TarArchiver,
        'zip'  :   ZipArchiver,
        'gzip' :   GZipArchiver,
        'bz2'  :   BZip2Archiver,
    }  
    
    @staticmethod
    def getClass(compressionType):
        archiver = ArchiverFactory.supportedArchivers.get(compressionType)
        archiver = AbstractArchiver if archiver is None else archiver  

        return archiver()
# !!! Old codes, kept for reference, not used in the current implementation !!!
# from io import StringIO
# from lxml import etree
# import os

# class AbstractArchiver():

#     def getContentType(self):
#         return 'text/plain'

#     def getFileExtension(self):
#         return '.xml'
    
#     def beginFile(self, file):
#         if 'content' in file and file.get('content') is not None:
#             self.reader = StringIO(file.get('content'))
#             self.reader.seek(0, 2)
#             self.fileSize = self.reader.tell()
#             self.reader.seek(0)
        
#         #elif 'xml' in file and file.get('path') is None:
#         #    self.reader = StringIO(etree.tostring(file.get('xml')))
#         #    self.reader.seek(0, 2)
#         #    self.fileSize = self.reader.tell()
#         #    self.reader.seek(0)

#         else:
#             self.reader = open(file.get('path'), 'rb')

#         return
    
#     def readBlock(self, block_size):
#         return self.reader.read(block_size)
    
#     def EOF(self):
#         return self.reader.tell()==self.fileSize
    
#     def endFile(self):
#         self.reader.close()
#         return
    
#     def readEnding(self):
#         return ''
    
#     def close(self):
#         return
    
#     def destinationPath(self, file):
#         return file.get('outpath')

# class ArchiverFactory():
    
#     from bq.export_service.controllers.archiver.tar_archiver import TarArchiver
#     from bq.export_service.controllers.archiver.zip_archiver import ZipArchiver
#     from bq.export_service.controllers.archiver.gzip_archiver import GZipArchiver
#     from bq.export_service.controllers.archiver.bz2_archiver import BZip2Archiver

#     supportedArchivers = {
#         'tar'  :   TarArchiver,
#         'zip'  :   ZipArchiver,
#         'gzip' :   GZipArchiver,
#         'bz2'  :   BZip2Archiver,
#     }  
    
#     @staticmethod
#     def getClass(compressionType):
#         archiver = ArchiverFactory.supportedArchivers.get(compressionType)
#         archiver = AbstractArchiver if archiver is None else archiver  

#         return archiver()

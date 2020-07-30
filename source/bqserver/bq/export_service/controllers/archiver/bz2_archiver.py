from bq.export_service.controllers.archiver.tar_archiver import TarArchiver
import bz2
from cStringIO import StringIO

class BZip2Archiver(TarArchiver):
    
    def __init__(self):
        TarArchiver.__init__(self)
        self.bbuffer = StringIO()
        self.bzipper = bz2.BZ2Compressor(9)

    def readBlock(self, block_size):
        block = self.bzipper.compress(TarArchiver.readBlock(self, block_size))
        return block

    def readEnding(self):
        block = self.bzipper.compress(TarArchiver.readEnding(self))
        block += self.bzipper.flush()
        return block

    def getContentType(self):
        return 'application/x-bzip2'

    def getFileExtension(self):
        return '.tar.bz2'
        

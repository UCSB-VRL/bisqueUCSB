from bq.export_service.controllers.archiver.tar_archiver import TarArchiver
from cStringIO import StringIO
from zlib import Z_FULL_FLUSH
import gzip

class GZipArchiver(TarArchiver):
    
    def __init__(self):
        TarArchiver.__init__(self)
        self.gbuffer = StringIO()
        self.gzipper = gzip.GzipFile(None, 'wb', 9, self.gbuffer) 

    def readBlock(self, block_size):
        self.gzipper.write(TarArchiver.readBlock(self, block_size))
        self.gzipper.flush(Z_FULL_FLUSH)
        block = self.gbuffer.getvalue()
        self.gbuffer.truncate(0)
        return block

    def readEnding(self):
        self.gzipper.write(TarArchiver.readEnding(self))
        self.gzipper.flush()
        self.gzipper.close()

        block = self.gbuffer.getvalue()
        self.gbuffer.truncate(0)
        self.gbuffer.close()

        return block

    def getContentType(self):
        return 'application/x-gzip'

    def getFileExtension(self):
        return '.tar.gz'
        

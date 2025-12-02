from bq.export_service.controllers.archiver.tar_archiver import TarArchiver
import bz2
# from io import StringIO
# !!! modern Python versions use BytesIO for binary data, not StringIO
from io import BytesIO

class BZip2Archiver(TarArchiver):
    
    def __init__(self):
        # TarArchiver.__init__(self)
        # self.bbuffer = StringIO()
        # self.bzipper = bz2.BZ2Compressor(9)
        # !!! TarArchiver already initializes the buffer, so we can just call super().__init__()
        super().__init__()
        self.bbuffer = BytesIO()
        self.bzipper = bz2.BZ2Compressor(9)

    def readBlock(self, block_size):
        # block = self.bzipper.compress(TarArchiver.readBlock(self, block_size))
        # !!! modern alternative
        block = self.bzipper.compress(super().readBlock(block_size))
        return block

    def readEnding(self):
        # block = self.bzipper.compress(TarArchiver.readEnding(self))
        # !!! modern alternative
        block = self.bzipper.compress(super().readEnding())
        block += self.bzipper.flush()
        return block

    def getContentType(self):
        return 'application/x-bzip2'

    def getFileExtension(self):
        return '.tar.bz2'

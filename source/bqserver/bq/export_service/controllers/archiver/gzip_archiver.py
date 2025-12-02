from bq.export_service.controllers.archiver.tar_archiver import TarArchiver
# from io import StringIO
# from zlib import Z_FULL_FLUSH
# !!!modern Python versions use BytesIO for binary data, not StringIO
from io import BytesIO
import gzip

class GZipArchiver(TarArchiver):
    
    # def __init__(self):
    #     TarArchiver.__init__(self)
    #     self.gbuffer = StringIO()
    #     self.gzipper = gzip.GzipFile(None, 'wb', 9, self.gbuffer) 

    # def readBlock(self, block_size):
    #     self.gzipper.write(TarArchiver.readBlock(self, block_size))
    #     self.gzipper.flush(Z_FULL_FLUSH)
    #     block = self.gbuffer.getvalue()
    #     self.gbuffer.truncate(0)
    #     return block

    # def readEnding(self):
    #     self.gzipper.write(TarArchiver.readEnding(self))
    #     self.gzipper.flush()
    #     self.gzipper.close()

    #     block = self.gbuffer.getvalue()
    #     self.gbuffer.close()
    #     return block
    
    # !!! modern implementations of the above methods use BytesIO instead of StringIO
    def __init__(self):
        super().__init__()
        self.gbuffer = BytesIO()
        self.gzipper = gzip.GzipFile(fileobj=self.gbuffer, mode='wb', compresslevel=9)

    def readBlock(self, block_size):
        data = super().readBlock(block_size)
        if isinstance(data, str):
            data = data.encode('utf-8')
        self.gzipper.write(data)
        self.gzipper.flush()
        block = self.gbuffer.getvalue()
        self.gbuffer.seek(0)
        self.gbuffer.truncate(0)
        return block

    def readEnding(self):
        data = super().readEnding()
        if isinstance(data, str):
            data = data.encode('utf-8')
        self.gzipper.write(data)
        self.gzipper.close()

        block = self.gbuffer.getvalue()
        self.gbuffer.close()
        return block

    def getContentType(self):
        # return 'application/x-gzip'
        # !!! modern content type for gzip files
        return 'application/gzip'

    def getFileExtension(self):
        return '.tar.gz'

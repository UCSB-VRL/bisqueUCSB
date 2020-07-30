import tarfile
import copy
from bq.export_service.controllers.archiver.archiver_factory import AbstractArchiver
from cStringIO import StringIO


class TarArchiver(tarfile.TarFile, AbstractArchiver):
    
    def __init__(self):
        self.buffer = StringIO()
        tarfile.TarFile.__init__(self, None, mode='w', fileobj=self.buffer)
    
    def beginFile(self, file):
        AbstractArchiver.beginFile(self, file)

        self.reader.seek(0, 2)
        self.tarInfo = tarfile.TarInfo(self.destinationPath(file));
        self.tarInfo.size = self.reader.tell()
        self.reader.seek(0)
        self.addTarInfo(self.tarInfo)
        self.finished = False
        return
    
    def readBlock(self, block_size):
        self.fileobj.write(self.reader.read(block_size))
        block = self.buffer.getvalue()
        self.buffer.truncate(0)
        return block
    
    def EOF(self):
        if self.reader.tell()>=self.tarInfo.size:
            if self.finished:
                return True
            self.finishWrite()
        return False
    
    def getContentType(self):
        return 'application/x-tar'

    def getFileExtension(self):
        return '.tar'

    def addTarInfo(self, tarinfo):
        self._check("aw")

        tarinfo = copy.copy(tarinfo)
        buf = tarinfo.tobuf(self.format, self.encoding, self.errors)
        self.fileobj.write(buf)
        self.offset += len(buf)
        
        self.members.append(tarinfo)
    
    def finishWrite(self):
        blocks, remainder = divmod(self.tarInfo.size, tarfile.BLOCKSIZE)
        if remainder > 0:
            self.fileobj.write(tarfile.NUL * (tarfile.BLOCKSIZE - remainder))
            blocks += 1
        self.offset += blocks * tarfile.BLOCKSIZE
        
        self.finished = True

    def readEnding(self):
        self.close()
        block = self.buffer.getvalue()
        self.buffer.truncate(0)
        return block

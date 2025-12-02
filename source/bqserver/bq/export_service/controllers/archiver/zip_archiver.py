import zipfile
import time
import os
from io import BytesIO
from bq.export_service.controllers.archiver.archiver_factory import AbstractArchiver


class ZipArchiver(AbstractArchiver):
    def __init__(self):
        self.buffer = BytesIO()
        self.zip = zipfile.ZipFile(self.buffer, mode='w', compression=zipfile.ZIP_DEFLATED, allowZip64=True)
        self._finalized = False
        self._file_buffer = None
        self._file_name = None
        self._position = 0

    def beginFile(self, file):
        AbstractArchiver.beginFile(self, file)
        self._file_buffer = BytesIO()
        self._file_name = self.destinationPath(file)

    def readBlock(self, block_size):
        chunk = self.reader.read(block_size)
        self._file_buffer.write(chunk)
        return b''  # Nothing to yield yet

    def EOF(self):
        return self.reader.tell() >= self.fileSize

    def endFile(self):
        self._file_buffer.seek(0)
        self.zip.writestr(self._file_name, self._file_buffer.read())
        self._file_buffer.close()
        self._file_buffer = None

    def readEnding(self):
        if not self._finalized:
            self.zip.close()
            self._finalized = True
        self.buffer.seek(self._position)
        data = self.buffer.read()
        self._position = self.buffer.tell()
        return data

    def getContentType(self):
        return 'application/zip'

    def getFileExtension(self):
        return '.zip'

    def close(self):
        if not self._finalized:
            self.zip.close()
            self._finalized = True

# !!! Old implementation, kept for reference, not used in the current implementation !!!
# import zipfile
# import zlib
# import time, struct
# import os
# from io import StringIO
# from bq.export_service.controllers.archiver.archiver_factory import AbstractArchiver


# class ZipArchiver(zipfile.ZipFile, AbstractArchiver):


#     def __init__(self):
#         self.buffer = StringIO()
#         self.position = 0
#         zipfile.ZipFile.__init__(self, self.buffer, mode='w', allowZip64=True)

#     def beginFile(self, file):
#         AbstractArchiver.beginFile(self, file)

#         if file.get('path') is None:
#             ftime = time.localtime();
#         else:
#             ftime = time.localtime(os.path.getctime(file.get('path')))

#         self.zipInfo = zipfile.ZipInfo(self.destinationPath(file), ftime[:6]);
#         self.reader.seek(0, 2)
#         self.zipInfo.file_size = self.zipInfo.compress_size = self.reader.tell()

#         self.reader.seek(0)
#         self.zipInfo.flag_bits = 0x00
#         self.zipInfo.header_offset = self.position
#         self.zipInfo.CRC = self.CRC32()

#         self._writecheck(self.zipInfo)
#         self._didModify = True

#         self.fp.write(self.zipInfo.FileHeader())

#         self.filelist.append(self.zipInfo)
#         self.NameToInfo[self.zipInfo.filename] = self.zipInfo

#         return

#     def readBlock(self, block_size):
#         self.fp.write(self.reader.read(block_size))
#         block = self.buffer.getvalue()
#         self.buffer.truncate(0)
#         self.position += len(block)

#         return block

#     def readEnding(self):
#         self.buffer.seek(self.position)
#         self.close()
#         newPos = self.buffer.tell()
#         self.buffer.seek(self.position)
#         block = self.buffer.read(newPos-self.position+1)
#         self.buffer.truncate(0)
#         return block

#     def EOF(self):
#         if self.reader.tell()>=self.zipInfo.file_size:
#             return True
#         return False

#     def CRC32(self):
#         block = 1; CRC = 0
#         self.reader.seek(0)
#         while block:
#             block = self.reader.read(65536)
#             CRC = zlib.crc32(block, CRC) & 0xffffffff
#         self.reader.seek(0)

#         return CRC

#     def getContentType(self):
#         return 'application/zip'

#     def getFileExtension(self):
#         return '.zip'

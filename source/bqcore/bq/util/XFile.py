# XFile
#
# Copyright (c) 2004 by Jody Burns <opensource@deimerich.com>
#
# This file is part of XFile.
#
# XFile is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# XFile is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
##############################################################################
import errno
from os import name

# Define what will be imported when a 'from XFile import *' statement
# is executed.
__all__ = ["LOCK_NB", "LOCK_EX", "LOCK_SH", "XFile", "Dump", "Slurp", "LockError"]
__version__ = "0.1.0.2"

if name not in ["nt", "posix"]:
    raise OSError, "the XFile object does not support the '%s' operating system." % name

if name == "nt":
    # Define locking constants.
    LOCK_NB = 1
    LOCK_EX = 2
    LOCK_SH = 0

    # Import necessary functions.
    try:
        from win32file import LockFileEx, UnlockFileEx, _get_osfhandle, error
        from pywintypes import OVERLAPPED
    except ImportError:
        from sys import stderr
        stderr.write("XFile for Windows requires the PyWin32 package to be installed\n")
        stderr.write("but it could not be imported.  Please install it and try again.")
        raise

elif name == "posix":
    # Define locking constants and import necessary functions.
    from fcntl import LOCK_EX, LOCK_SH, LOCK_NB, LOCK_UN, lockf

def SplitNumber(Number):
    # SplitNumber -- Split number into high and low bits for
    # passing to Windows API functions.

    # Check that the number is an integer and is not too large.
    if type(Number) not in [int, long]:
        raise ValueError, "expected int or long for number, got %s" % type(Number).__name__
    if Number > 2 ** 64 - 1:
        raise ValueError, "number cannot be larger than 2 ** 64 - 1"

    # If the number is less than 2 ** 32 it doesn't need to
    # be split.
    if Number < 2 ** 32:
        num_High = 0
        num_Low = Number
    else:
        num_Low = Number % 2 ** 32
        num_High = (Number - num_Low) / (2 ** 32)

    # If the numbers are greater than 2 ** 31 - 1, they have to be inverted.
    if num_High > 2 ** 31 - 1:
        num_High = -(num_High ^ (2 ** 32 - 1)) - 1
    if num_Low > 2 ** 31 - 1:
        num_Low = -(num_Low ^ (2 ** 32 - 1)) - 1

    return int(num_High), int(num_Low)

class LockError(IOError):
    # Our custom lock error class, descended from
    # IOError so it will be caught by 'except IOError'.
    pass

class XFile(file):

    def __init__(self, str_Filename, str_Mode="r", num_BufferSize=-1):
        # Set our locker/unlocker members to their OS-specific functions.
        if name == "nt":
            self.__LockFile = self.__LockNT
            self.__UnlockFile = self.__UnlockNT
        elif name == "posix":
            self.__LockFile = self.__LockPOSIX
            self.__UnlockFile = self.__UnlockPOSIX

        # Set the internal lock flag.
        self.__bool_Locked = False

        # Initialize the rest of ourself.
        file.__init__(self, str_Filename, str_Mode, num_BufferSize)

    def __LockNT(self, num_LockFlags, num_Start, num_End):
        # Lock the file on the NT platform.  Locking files
        # on NT isn't as simple as using flock() so we have
        # to use a more complex method to lock files.

        # Firstly, we must get the actual filehandle that
        # the OS uses.
        if hasattr(self, "num_OSHandle") == False:
            self.__num_OSHandle = _get_osfhandle(self.fileno())

        # Before we go about splitting the numbers up, we have
        # to set defaults.  Given 0 for both the start and the end,
        # we assume that the user wants to lock the whole file,
        # because locking no part of the file would be pointless.
        if num_Start == num_End == 0:
            num_End = 2 ** 64 - 1

        # Now, we have to split the byte range end into high
        # and low bits because that's how LockFileEx takes it.
        num_BytesToLock = num_End - num_Start
        num_BytesToLockHigh, num_BytesToLockLow = SplitNumber(num_BytesToLock)

        # We also have to split up the offset of the file and then
        # put it in a PyOVERLAPPED structure.  Why Microsoft chose
        # to use an OVERLAPPED structure for file locking I don't know;
        # e-mail me if you find out why.
        num_OffsetHigh, num_OffsetLow = SplitNumber(num_Start)
        self.__OverlappedObject = OVERLAPPED()
        self.__OverlappedObject.OffsetHigh = num_OffsetHigh
        self.__OverlappedObject.Offset = num_OffsetLow

        # Now that we have all of these things we can try to lock the file.
        try:
            LockFileEx(self.__num_OSHandle, num_LockFlags, num_BytesToLockLow, num_BytesToLockHigh, self.__OverlappedObject)
        except error, e:
            self.__LastException = e
            raise LockError, e.args

        # Place the start and end values as members in ourself so
        # the unlock() function can use the later.
        self.__num_Start = num_Start
        self.__num_End = num_End

    def __UnlockNT(self, num_Start, num_End):
        # Unlocking is about as complex as locking for NT.
        num_BytesToUnlock = num_End - num_Start
        num_BytesToUnlockHigh, num_BytesToUnlockLow = SplitNumber(num_BytesToUnlock)

        # We already have the overlapped object so we don't need to make it again.
        try:
            UnlockFileEx(self.__num_OSHandle, num_BytesToUnlockLow, num_BytesToUnlockHigh, self.__OverlappedObject)
        except error, e:
            self.__LastException = e
            raise LockError, e.args

    def __LockPOSIX(self, num_LockFlags, num_Start, num_End):
        try:
            lockf(self.fileno(), num_LockFlags, num_End, num_Start, 0)
        except IOError, Error:
            # The lock was unsuccessful, so return False.
            if Error.errno == errno.EACCES or Error.errno == errno.EAGAIN:
                self.__LastException = Error
                raise LockError, Error.args

        # Place the start and end values as members in ourself so
        # the unlock() function can use the later.
        self.__num_Start = num_Start
        self.__num_End = num_End

    def __UnlockPOSIX(self, num_Start, num_End):
        try:
            lockf(self.fileno(), LOCK_UN, num_End, num_Start, 0)
        except IOError, Error:
            # If the unlock was unsuccessful, raise LockError.
            self.__LastException = Error
            raise LockError, Error.args

    def __GetLockStatusInternal(self):
        return self.__bool_Locked

    def lock(self, num_LockFlags, num_Start=0, num_End=0):

        """Locks the file.  num_LockFlags is a XOR'ed combination of the flags you want for this lock operation; num_Start is the start of the range of bytes you want to lock, and num_End is the end."""

        # Check that the file is lockable; ie, not closed or already locked.
        if self.is_locked() == True:
            raise LockError, "cannot lock file; file is already locked"
        if self.closed == True:
            raise LockError, "cannot lock file; file is closed"

        # Check that the flags are an integer.
        if type(num_LockFlags) not in [int, long]:
            raise LockError, "expected int or long for lock flags, got %s" % type(num_LockFlags).__name__

        # Check that we're not doing LOCK_EX when in read mode on POSIX.
        if name == "POSIX" and num_LockFlags | LOCK_EX == num_LockFlags and "r" in self.mode and "+" not in self.mode: # pylint: disable=unsupported-membership-test
            raise LockError, "LOCK_EX cannot be used in read mode on POSIX; use LOCK_SH instead"

        # Check that num_Start and num_End are integers.
        if type(num_Start) not in [int, long]:
            raise LockError, "expected int or long for lock range start, got %s" % type(num_Start).__name__
        if type(num_End) not in [int, long]:
            raise LockError, "expected int or long for lock range end, got %s" % type(num_End).__name__

        # Check that the ranges are positive.
        if num_Start < 0:
            raise LockError, "lock range start must be a positive integer"
        if num_End < 0:
            raise LockError, "lock range end must be a positive integer"

        # Check that the start and end are not the same.  The reason we ignore
        # a 0 for both values is that 0 is the default.
        if num_Start == num_End and num_Start != 0 and num_End != 0:
            raise LockError, "lock range start and lock range end must be different"

        # Lock the file.
        self.__LockFile(num_LockFlags, num_Start, num_End)

        # If we've gotten this far without raising an exception,
        # set the locked flag to True.
        self.__bool_Locked = True

    def unlock(self):

        """Unlocks the file."""

        # Check that the file is unlockable; ie, not closed or already unlocked.
        if self.is_locked() == False:
            raise LockError, "cannot unlock file; file is already unlocked"
        if self.closed == True:
            raise LockError, "cannot unlock file; file is closed"

        # Unlock the file.
        self.__UnlockFile(self.__num_Start, self.__num_End)

        # If we've gotten this far without an error,
        # set the locked flag to False.
        self.__bool_Locked = False

    def is_locked(self):
        """Returns True if the file has been locked by the lock() method for this file and False if it has not."""
        return self.__GetLockStatusInternal()


def Slurp(str_Filename, bool_Binary=False):
    # Given a filename, safely read the contents of that
    # file and return them.

    # Check parameter types.
    if type(str_Filename) not in [str, buffer, unicode]:
        raise TypeError, "Filename must be str, buffer or unicode; got %s" % type(str_Filename).__name__

    if type(bool_Binary) != bool:
        raise TypeError, "Binary indicator must be bool; got %s" % type(bool_Binary).__name__

    File = XFile(str_Filename, "r" + ("b" * bool_Binary))
    File.lock(LOCK_SH)
    str_Contents = File.read()
    File.unlock()
    File.close()

    return str_Contents

def Dump(str_Filename, str_Data, bool_Binary=False):
    # Given a filename, safely write the contents
    # of the string given to the file.

    # Check parameter types.
    if type(str_Filename) not in [str, buffer, unicode]:
        raise TypeError, "Filename must be str, buffer or unicode; got %s" % type(str_Filename).__name__

    if type(str_Data) not in [str, buffer, unicode]:
        raise TypeError, "Data must be str, buffer or unicode; got %s" % type(str_Data).__name__

    if type(bool_Binary) != bool:
        raise TypeError, "Binary indicator must be bool; got %s" % type(bool_Binary).__name__

    File = XFile(str_Filename, "w" + ("b" * bool_Binary))
    File.lock(LOCK_EX)
    File.write(str_Data)
    File.unlock()
    File.close()

def Append(str_Filename, str_Data, bool_Binary=False):
    # Given a filename, safely append the contents
    # of the string given to the file.

    # Check parameter types.
    if type(str_Filename) not in [str, buffer, unicode]:
        raise TypeError, "Filename must be str, buffer or unicode; got %s" % type(str_Filename).__name__

    if type(str_Data) not in [str, buffer, unicode]:
        raise TypeError, "Data must be str, buffer or unicode; got %s" % type(str_Data).__name__

    if type(bool_Binary) != bool:
        raise TypeError, "Binary indicator must be bool; got %s" % type(bool_Binary).__name__

    File = XFile(str_Filename, "a" + ("b" * bool_Binary))
    File.lock(LOCK_EX)
    File.write(str_Data)
    File.unlock()
    File.close()

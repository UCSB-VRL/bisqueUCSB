# misc.py
# Author: Dmitry Fedorov
# Center for BioImage Informatics, University California, Santa Barbara


"""miscellaneous functions for Image Service and COmmand Line Converters"""

__module__ = "misc"
__author__ = "Dmitry Fedorov"
__version__ = "0.1"
__revision__ = "$Rev$"
__date__ = "$Date$"
__copyright__ = "Center for BioImage Informatics, University California, Santa Barbara"

import logging
import os
import re
import tempfile
from itertools import groupby
from subprocess import PIPE, Popen

from bq.util.mkdir import _mkdir

log = logging.getLogger("bq.util.io_misc")


################################################################################
# Misc
################################################################################


# def blocked_alpha_num_sort(s):
#     return [int(''.join(g)) if k else ''.join(g) for k, g in groupby(str(s), str.isdigit)]
# !!! To handle cases where elements of sorted array may have integers and some doesn't have digit at all
def blocked_alpha_num_sort(s):
    s = str(s)
    return [str(int("".join(g))) if k else "".join(g) for k, g in groupby(s, str.isdigit)]


def between(left, right, s):
    _, _, a = s.partition(left)
    a, _, _ = a.partition(right)
    return a


def xpathtextnode(doc, path, default="", namespaces=None):
    r = doc.xpath(path, namespaces=namespaces)
    if len(r) < 1:
        return default
    else:
        return r[0].text


def safeint(s, default=0):
    try:
        v = int(s)
    except (ValueError, TypeError) as e:
        v = default
    return v


def safefloat(s, default=0.0):
    try:
        v = float(s)
    except ValueError:
        v = default
    return v


def safetypeparse(v):
    try:
        v = int(v)
    except ValueError:
        try:
            v = float(v)
        except ValueError:
            pass
    except TypeError:  # in case of Nonetype
        pass
    return v


def safeencode(s):
    if isinstance(s, str) is not True:
        return str(s)
    try:
        s.encode("ascii")
    except UnicodeEncodeError:
        s = s.encode("utf8")
    return s


def toascii(s):
    if isinstance(s, str) is not True:
        s = "%s" % s
    return s.encode("ascii", "replace")


# def tounicode(s):
#     if isinstance(s, str) is True:
#         return s
#     if isinstance(s, str) is not True:
#         return '%s'%s
#     try:
#         return s.decode('utf8')


#     except (UnicodeEncodeError, UnicodeDecodeError):
#         try:
#             return s.decode('latin1')
#         except (UnicodeDecodeError, UnicodeEncodeError):
#             return str(s.encode('ascii', 'replace'))
# !!! modified tounicode to handle bytes and str types
# !!! in python 3, since str is unicode and bytes is bytes
def tounicode(s):
    # log.info(f"----- tounicode before: {s} type: {type(s)}")
    out_str = ""
    if isinstance(s, str):
        out_str = s
    if isinstance(s, bytes):
        try:
            out_str = s.decode("utf-8")
        except UnicodeDecodeError:
            try:
                out_str = s.decode("latin1")
            except UnicodeDecodeError:
                out_str = s.decode("ascii", errors="replace")
    if isinstance(s, list):
        out_str = " ".join([tounicode(x) for x in s])
    out_str = f"{out_str}"
    # if string is still like "b'...' then decode it
    regex = re.compile(r"(^b'(.+)'$)|(^b\"(.+)\"$)")
    if regex.match(out_str):
        out_str = out_str[2:-1]
    # log.info(f"----- tounicode after: {out_str} type: {type(out_str)}")
    return out_str


def run_command(command, cwd=None, shell=False):
    """returns a string of a successfully executed command, otherwise None"""
    try:
        p = Popen(command, stdout=PIPE, stderr=PIPE, cwd=cwd, shell=shell)
        o, e = p.communicate()
        if p.returncode != 0:
            log.info("BAD non-0 return code for %s", command)
            return None

        # Handle Python 3 bytes to string conversion
        result = o or e
        if isinstance(result, bytes):
            result = result.decode("utf-8", errors="ignore")

        return result
    except OSError:
        log.warning("Command not found [%s]", command[0])
    except Exception:
        log.exception("Exception during execution [%s]", command)
    return None


def isascii(s):
    if isinstance(s, str) is True:
        return True
    try:
        s.encode("ascii")
    except UnicodeEncodeError:
        return False
    return True


def remove_safe(f):
    try:
        os.remove(f)
    except Exception as e:
        print(f"Cannot remove file {f}: {e}")
        log.warning(f"Cannot remove file {f}: {e}")


def dolink(source, link_name):
    log.debug("Hard link %s -> %s", source, link_name)
    return os.link(source, link_name)


def start_nounicode_win(ifnm, command):
    return command, None


def end_nounicode_win(tmp):
    pass

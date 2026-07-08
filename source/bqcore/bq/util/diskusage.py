#!/usr/bin/env python

"""
Return disk usage statistics about the given path as a (total, used, free)
namedtuple.  Values are expressed in bytes.
"""
# Author: Giampaolo Rodola' <g.rodola [AT] gmail [DOT] com>
# License: MIT
# http://code.activestate.com/recipes/577972-disk-usage/

import collections
import os

_ntuple_diskusage = collections.namedtuple("usage", "total used free")


def disk_usage(path):
    st = os.statvfs(path)
    free = st.f_bavail * st.f_frsize
    total = st.f_blocks * st.f_frsize
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    return _ntuple_diskusage(total, used, free)


disk_usage.__doc__ = __doc__

if __name__ == "__main__":
    print(disk_usage(os.getcwd()))

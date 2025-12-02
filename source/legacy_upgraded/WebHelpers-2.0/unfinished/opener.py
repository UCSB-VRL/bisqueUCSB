"""A unified front end for opening plain or compressed files.

This is in 'unfinished' because a smarter opener could also decode Unicode,
and check the file's magic number rather depending on the filename
extension.  Are these worth implementing?  Would they be more worthwhile
under Python 3, which might provide a Unicode-aware opener for bz2 and gz?
"""

def smart_open(filename, mode):
    """Unified front end for opening plain files and compressed files."""
    if   filename.endswith(".bz2"):
        import bz2
        opener = bz2.BZ2File
    elif filename.endswith(".gz"):
        import gzip
        opener = gzip.open
    else:
        opener = open
    return opener(filename, mode)
    

"""Functions being considered for webhelpers.containers.

These functions are useful but they're hard to explain and their 
implementation is more cryptic than we'd like.
"""

from webhelpers.containers import distribute

def columnize_as_rows(lis, columns, horizontal=False, fill=None):
    """Like 'zip' but fill any missing elements."""
    data = distribute(lis, columns, horizontal, fill)
    rowcount = len(data)
    length = max(len(x) for x in data)
    for c, lis in enumerate(data):
        n = length - len(lis)
        if n > 0:
            extension = [fill] * n
            lis.extend(extension)
    return zip(*data)

def izip_fill(*iterables, **kw):
    """Like itertools.izip but use a default value for the missing elements
       in short lists rather than stopping at the end of the shortest list.

       ``*iterables`` are the iterables to zip.
       ``default`` is the default value (default ``None``, must be a keyword
       arg.
    """
    iterables = map(iter, iterables)
    default = kw.pop('default', None)
    if kw:
        raise TypeError("unrecognized keyword arguments")
    columns = len(iterables)
    columns_range = range(columns)
    while True:
        found_data = False
        row = [None] * columns
        for i in columns_range:
            try:
                row[i] = iterables[i].next()
                found_data = True
            except StopIteration:
                row[i] = default
        if not found_data:
            break
        yield tuple(row)

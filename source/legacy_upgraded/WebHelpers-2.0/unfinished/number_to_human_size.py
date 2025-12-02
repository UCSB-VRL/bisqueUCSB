"""number_to_human_size() helper from WebHelpers 0.6.4

If you need the existing function, copy this file to your application.
We are working on a more comprehensive alternative, see
http://bitbucket.org/bbangert/webhelpers/issue/2/reinstate-number_to_human_size
"""

def number_to_human_size(size, precision=1):
    """
    Return a formatted-for-humans file size.

    ``precision``
        The level of precision, defaults to 1
    
    Examples::
    
        >>> number_to_human_size(123)
        '123 Bytes'
        >>> number_to_human_size(1234)
        '1.2 KB'
        >>> number_to_human_size(12345)
        '12.1 KB'
        >>> number_to_human_size(1234567)
        '1.2 MB'
        >>> number_to_human_size(1234567890)
        '1.1 GB'
        >>> number_to_human_size(1234567890123)
        '1.1 TB'
        >>> number_to_human_size(1234567, 2)
        '1.18 MB'
        
    """
    if size == 1:
        return "1 Byte"
    elif size < 1024:
        return "%d Bytes" % size
    elif size < (1024**2):
        return ("%%.%if KB" % precision) % (size / 1024.00)
    elif size < (1024**3):
        return ("%%.%if MB" % precision) % (size / 1024.00**2)
    elif size < (1024**4):
        return ("%%.%if GB" % precision) % (size / 1024.00**3)
    elif size < (1024**5):
        return ("%%.%if TB" % precision) % (size / 1024.00**4)
    else:
        return ""

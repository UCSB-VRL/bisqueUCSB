"""Contributed by Shazow.

These functions convert an int to/from any base, using any alphabet.
Hexadecimal, binary, and base64 are three well-known alphabets, but you can 
also create your own.  Shazow's examples::

    >> number_to_string(12345678, '01')
    '101111000110000101001110'
    >> number_to_string(12345678, 'ab')
    'babbbbaaabbaaaababaabbba'
    >>> number_to_string(12345678, string.letters + string.digits)
    'ZXP0
    >> string_to_number('101111000110000101001110', '01')
    12345678
    >> string_to_number('babbbbaaabbaaaababaabbba', 'ab')
    12345678
    >> string_to_number('ZXP0', string.letters + string.digits)
    12345678
    >> number_to_string(12345, ['zero ', 'one ', 'two ', 'three ', 'four ', 'five ', 'six ', 'seven ', 'eight ', 'nine '])
    'one two three four five '

YouTube does this to compress numeric video IDs a shorter ID string than
decimal.  This module remains in the unfinished directory because we're not
sure how useful it is.  ``base64.urlsafe_b64encode`` and decode in the Python
standard library cover the most common use case, even if those functions have
awful names.  (Standard base 64 is not filesystem safe because it uses "/".
(URL-safe base 64 is also safe for POSIX filenames.  Standard base 64 is 
*not* filesystem safe because it uses the "/" character.)

Experimental use compressing URL strings to a filesystem-safe alphabet also
yielded medicre results.  I (Mike Orr) tried taking the hex MD5 digest of a
long URL (always 32 hex characters), converting that to long, and then to
base 64 URLsafe.  This created a string longer than the hex number!  Trying
various hashlib functions and alphabets produced strings down to 20 chars.
This savings is not worth the complexity over well-tested-and-understood hex
MD5 unless the collection of numbers is very large.  Binary MD5 is even
shorter: 16 bytes, although they must be stored in a binary-safe manner.
"""

def baseN_encode(n, alphabet):
    """
    Given an non-negative int, convert it to a string composed of the given
    alphabet mapping
    """
    result = ''
    alphabet = list(alphabet)
    base = len(alphabet)
    current = int(n)
    while 1:
        result = alphabet[current % base] + result
        current = current // base
        if not current: break
    return result

def baseN_decode(s, alphabet):
    """
    Given a string, convert it to an int composed of the given alphabet mapping
    """
    s = list(s)
    alphabet = list(alphabet)
    base = len(alphabet)
    inverse_alphabet = dict(zip(alphabet, xrange(0, base)))
    n = 0
    exp = 0
    for i in reversed(s):
        n += inverse_alphabet[i] * (base ** exp)
        exp += 1
    return n


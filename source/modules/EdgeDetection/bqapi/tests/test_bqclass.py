import pytest

from lxml import etree
from bqapi.bqclass import BQFactory

pytestmark = pytest.mark.unit


X="""
<resource>
<image uri="/is/1">
<tag name="filename" value="boo"/>
<tag name="xxx" value="yyy"/>
</image>
</resource>
"""



def test_conversion():
    'test simple xml conversions'
    print "ORIGINAL"
    print X

    factory = BQFactory(None)

    r = factory.from_string(X)
    print "PARSED"

    x = factory.to_string (r)

    print "XML"
    print r
    assert x == X.translate(None, '\r\n')

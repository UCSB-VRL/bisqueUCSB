from webhelpers.util import *

def test_html_escape():
    assert html_escape('foo') == 'foo'
    assert html_escape('<this"that>') == '&lt;this&quot;that&gt;'
    assert html_escape(u'\u1000') == '&#4096;'
    class X:
        def __unicode__(self):
            return u'<\u1000>'
    assert html_escape(X()) == '&lt;&#4096;&gt;'
    assert html_escape(1) == '1'
    assert html_escape(None) == ''

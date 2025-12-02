from nose.tools import eq_

from webhelpers.html import literal, lit_sub, escape, HTML

def test_double_escape():
    quoted = escape(u'This string is "quoted"')
    eq_(quoted, u'This string is &#34;quoted&#34;')
    dbl_quoted = escape(quoted)
    eq_(quoted, dbl_quoted)

def test_literal():
    lit = literal(u'This string <>')
    other = literal(u'<other>')
    eq_(u'This string <><other>', lit + other)
    assert type(lit + other) is literal
    
    eq_(u'&#34;<other>', '"' + other)
    eq_(u'<other>&#34;', other + '"')
    
    mod = literal('<%s>ello')
    eq_(u'<&lt;H&gt;>ello', mod % '<H>')
    assert type(mod % '<H>') is literal
    eq_(HTML('<a>'), '&lt;a&gt;')
    assert type(HTML('<a>')) is literal

def test_literal_dict():
    lit = literal(u'This string <>')
    unq = 'This has <crap>'
    sub = literal('%s and %s')
    eq_(u'This string <> and This has &lt;crap&gt;', sub % (lit, unq))
    
    sub = literal('%(lit)s and %(lit)r')
    eq_(u"This string <> and literal(u&#39;This string &lt;&gt;&#39;)", sub % dict(lit=lit))
    sub = literal('%(unq)r and %(unq)s')
    eq_(u"&#39;This has &lt;crap&gt;&#39; and This has &lt;crap&gt;", sub % dict(unq=unq))

def test_literal_mul():
    lit = literal(u'<>')
    eq_(u'<><><>', lit * 3)
    assert isinstance(lit*3, literal)

def test_literal_join():
    lit = literal(u'<>')
    assert isinstance(lit.join(['f', 'a']), literal)
    eq_(u'f<>a', lit.join(('f', 'a')))

def test_literal_int():
    lit = literal(u'<%i>')
    eq_(u'<5>', lit % 5)

def test_html():
    a = HTML.a(href='http://mostlysafe\" <tag', c="Bad <script> tag")
    eq_(a, u'<a href="http://mostlysafe&#34; &lt;tag">Bad &lt;script&gt; tag</a>')
    
    img = HTML.img(src='http://some/image.jpg')
    eq_(img, u'<img src="http://some/image.jpg" />')
    
    br = HTML.br()
    eq_(u'<br />', br)

def test_lit_re():
    lit = literal('This is a <string>')
    unlit = 'This is also a <string>'
    
    result = lit_sub(r'<str', literal('<b'), lit)
    eq_(u'This is a <bing>', escape(result))
    
    result = lit_sub(r'a <str', 'a <b> <b', unlit)
    eq_(u'This is also a &lt;b&gt; &lt;bing&gt;', escape(result))

def test_unclosed_tag():
    result = HTML.form(_closed=False)
    print result
    eq_(u'<form>', result)
    
    result = HTML.form(_closed=False, action="hello")
    eq_(u'<form action="hello">', result)

def test_newline_arg():
    eq_(HTML.a(),         literal(u'<a></a>'))
    eq_(HTML.a(_nl=True), literal(u'<a>\n</a>\n'))
    eq_(HTML.a(_closed=False),           literal(u'<a>'))
    eq_(HTML.a(_closed=False, _nl=True), literal(u'<a>\n'))
    eq_(HTML.a("A", "B", href="/"),      literal(u'<a href="/">AB</a>'))
    eq_(HTML.a("A", "B", href="/", _nl=True), literal(u'<a href="/">\nA\nB\n</a>\n'))

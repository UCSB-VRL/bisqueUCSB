# -*- coding: utf-8 -*-
from nose.tools import eq_

from webhelpers.html import HTML, literal
from webhelpers.html.converters import *
from webhelpers.html.converters import _get_markdown_module

def test_textilize():
    eq_('<h1>This is a test of textile</h1>\n\n<p>Paragraph</p>\n\n<p>Another paragraph</p>\n\n<ul>\n<li>Bullets</li>\n</ul>',
        textilize("h1. This is a test of textile\n\nParagraph\n\nAnother paragraph\n\n* Bullets"))

def test_markdown():
    _markdown = _get_markdown_module()
    markdown_text = """
Introduction
------------

Markdown is a text-to-HTML conversion tool for web writers.

Acknowledgements <a id="acknowledgements" />
----------------

[Michel Fortin][] has ported to Markdown to PHP.
    """
    if _markdown.version_info >= (2, 0):
        expected =  literal(u'<h2>Introduction</h2>\n<p>Markdown is a text-to-HTML conversion tool for web writers.</p>\n<h2>Acknowledgements <a id="acknowledgements" /></h2>\n<p>[Michel Fortin][] has ported to Markdown to PHP.</p>')
    else:
        expected =  literal(u'<h2>Introduction</h2>\n<p>Markdown is a text-to-HTML conversion tool for web writers.\n</p>\n\n<h2>Acknowledgements <a id="acknowledgements" /></h2>\n<p>[Michel Fortin][] has ported to Markdown to PHP.\n</p>')
    eq_(markdown(markdown_text, markdown=_markdown), expected)

def test_markdown_embedded_html():
    _markdown = _get_markdown_module()
    markdown_text = 'This text includes <script>Javascript</script> & stuff.'
    if _markdown.version_info >= (2, 0):
        expected = literal(u'<p>This text includes &lt;script&gt;Javascript&lt;/script&gt; &amp; stuff.</p>')
    else:
        expected = literal(u'<p>This text includes &lt;script&gt;Javascript&lt;/script&gt; &amp; stuff.\n</p>')
    eq_(markdown(markdown_text, safe_mode="escape", markdown=_markdown), expected)


def test_nl2br():
    eq_(u'A B<br />\nC D<br />\n<br />\nE F', nl2br("A B\nC D\r\n\r\nE F"))

def test_nl2br2():
    eq_(u'&lt;strike&gt;W&lt;/strike&gt;<br />\nThe W', nl2br("<strike>W</strike>\nThe W"))

def test_nl2br3():
    eq_(u'<strike>W</strike><br />\nThe W', nl2br(literal("<strike>W</strike>\nThe W")))

def test_format_paragraphs1():
    eq_(u"<p>crazy\n cross\n platform linebreaks</p>", format_paragraphs("crazy\r\n cross\r platform linebreaks"))

def test_format_paragraphs2():
    eq_(u"<p>crazy<br />\n cross<br />\n platform linebreaks</p>", format_paragraphs("crazy\r\n cross\r platform linebreaks", True))

def test_format_paragraphs3():
    eq_(u"<p>A paragraph</p>\n\n<p>and another one!</p>", format_paragraphs("A paragraph\n\nand another one!"))

def test_format_paragraphs4():
    eq_(u"<p>A paragraph<br />\n With a newline</p>", format_paragraphs("A paragraph\n With a newline", True))

def test_format_paragraphs5():
    eq_(u"<p>A paragraph\n With a newline</p>", format_paragraphs("A paragraph\n With a newline", False))

def test_format_paragraphs6():
    eq_(u"<p>A paragraph\n With a newline</p>", format_paragraphs("A paragraph\n With a newline"))

def test_format_paragraphs7():
    eq_(u"", format_paragraphs(None))

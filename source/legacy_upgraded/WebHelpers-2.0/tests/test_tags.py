# -*- coding: utf-8 -*-

from nose.tools import eq_

from webhelpers.html import HTML, literal
from webhelpers.html.tags import *

from util import raises

class TestFormTagHelper(object):
    def test_check_box(self):
        eq_(
            checkbox("admin"),
            u'<input id="admin" name="admin" type="checkbox" value="1" />',
        )

    def test_form(self):
        eq_(
            form(url="http://www.example.com"),
            u'<form action="http://www.example.com" method="post">'
        )
        eq_(
            form(url="http://www.example.com", method='GET'),
            u'<form action="http://www.example.com" method="GET">'
        )
        eq_(
            form('/test/edit/1'),
            u'<form action="/test/edit/1" method="post">'
        )

    def test_form_multipart(self):
        eq_(
            form(url='http://www.example.com', multipart=True),
            u'<form action="http://www.example.com" enctype="multipart/form-data" method="post">'
        )
        
    def test_hidden_field(self):
        eq_(
            hidden("id", 3),
            u'<input id="id" name="id" type="hidden" value="3" />'
        )

    def test_hidden_field_alt(self):
        eq_(
            hidden("id", '3'),
            u'<input id="id" name="id" type="hidden" value="3" />'
        )

    def test_password_field(self):
        eq_(
            password("password"), 
            u'<input id="password" name="password" type="password" />'
        )

    def test_radio_button(self):
        eq_(
            radio("people", "justin"),
            u'<input id="people_justin" name="people" type="radio" value="justin" />'
        )
        
        eq_(
            radio("num_people", 5),
            u'<input id="num_people_5" name="num_people" type="radio" value="5" />'
        )

        eq_(
            radio("num_people", 5),
            u'<input id="num_people_5" name="num_people" type="radio" value="5" />'
        )
        
        eq_(
            radio("gender", "m") + radio("gender", "f"),
            u'<input id="gender_m" name="gender" type="radio" value="m" /><input id="gender_f" name="gender" type="radio" value="f" />'
        )
        
        eq_(
            radio("opinion", "-1") + radio("opinion", "1"),
            u'<input id="opinion_-1" name="opinion" type="radio" value="-1" /><input id="opinion_1" name="opinion" type="radio" value="1" />'
        )

        eq_(
            radio("num_people", 5, checked=True),
            u'<input checked="checked" id="num_people_5" name="num_people" type="radio" value="5" />'
        )

    def test_submit(self):
        eq_(
            u'<input id="commit" name="commit" type="submit" value="Save changes" />',
            submit("commit", "Save changes")
        )

    def test_text_area(self):
        eq_(
            textarea("aa", ""),
            u'<textarea id="aa" name="aa"></textarea>'
        )
        eq_(
            textarea("aa", None),
            u'<textarea id="aa" name="aa"></textarea>'
        )
        eq_(
            textarea("aa", "Hello!"),
            u'<textarea id="aa" name="aa">Hello!</textarea>'
        )

    def test_text_area_size_string(self):
        eq_(
            textarea("body", "hello world", cols=20, rows=40),
            u'<textarea cols="20" id="body" name="body" rows="40">hello world</textarea>'
        )

    def test_text_field(self):
        eq_(
            text("title", ""),
            u'<input id="title" name="title" type="text" value="" />'
        )
        eq_(
            text("title", None),
            u'<input id="title" name="title" type="text" />'
        )
        eq_(
            text("title", "Hello!"),
            u'<input id="title" name="title" type="text" value="Hello!" />'
        )

    def test_text_field_class_string(self):
        eq_(
            text( "title", "Hello!", class_= "admin"),
            u'<input class="admin" id="title" name="title" type="text" value="Hello!" />'
        )

    def test_boolean_options(self):
        eq_(     
            checkbox("admin", 1, True, disabled = True, readonly="yes"),
            u'<input checked="checked" disabled="disabled" id="admin" name="admin" readonly="readonly" type="checkbox" value="1" />'
        )
        eq_(
            checkbox("admin", 1, True, disabled = False, readonly = None),
            u'<input checked="checked" id="admin" name="admin" type="checkbox" value="1" />'
        )

    def test_multiple_id_bug(self):
        # Don't set multiple id attributes for 'id_' argument.
        eq_(
            text("spam", "pizza", id="eggs"),
            u'<input id="eggs" name="spam" type="text" value="pizza" />')
        eq_(
            text("spam", "pizza", id_="eggs"), 
            u'<input id="eggs" name="spam" type="text" value="pizza" />')
        eq_(
            select("spam", [1,2], [2], id="eggs"),
            u'<select id="eggs" name="spam">\n<option selected="selected" value="2">2</option>\n</select>')
        eq_(
            select("spam", [1,2], [2], id_="eggs"),
            u'<select id="eggs" name="spam">\n<option selected="selected" value="2">2</option>\n</select>')

    def test_id_and_id_(self):
        raises(TypeError, text, "spam", "pizza", id="fubar", id_="eggs")
        

    
class TestLinkHelper(object):
    def test_link_tag_with_query(self):
        eq_(u"<a href=\"http://www.example.com?q1=v1&amp;q2=v2\">Hello</a>", 
               link_to("Hello", "http://www.example.com?q1=v1&q2=v2"))
    
    def test_link_tag_with_query_and_no_name(self):
        eq_(u"<a href=\"http://www.example.com?q1=v1&amp;q2=v2\">http://www.example.com?q1=v1&amp;q2=v2</a>", 
               link_to(None, HTML.literal("http://www.example.com?q1=v1&amp;q2=v2")))
    
    def test_link_tag_with_custom_onclick(self):
        eq_(u"<a href=\"http://www.example.com\" onclick=\"alert(&#39;yay!&#39;)\">Hello</a>", 
               link_to("Hello", "http://www.example.com", onclick="alert('yay!')"))
    

class TestAssetTagHelper(object):
    def test_auto_discovery_link_tag(self):
        eq_(literal(u'<link href="http://feed.com/feed.xml" rel="alternate" title="RSS" type="application/rss+xml" />'),
                         auto_discovery_link('http://feed.com/feed.xml'))
        eq_('<link href="http://feed.com/feed.xml" rel="alternate" title="ATOM" type="application/atom+xml" />',
                         auto_discovery_link('http://feed.com/feed.xml', feed_type='atom'))
        eq_('<link href="app.rss" rel="alternate" title="atom feed" type="application/atom+xml" />',
                         auto_discovery_link('app.rss', feed_type='atom', title='atom feed'))
        eq_('<link href="app.rss" rel="alternate" title="My RSS" type="application/rss+xml" />',
                         auto_discovery_link('app.rss', title='My RSS'))
        eq_('<link href="/app.rss" rel="alternate" title="" type="text/html" />',
                         auto_discovery_link('/app.rss', feed_type='text/html'))
        eq_('<link href="/app.html" rel="alternate" title="My RSS" type="text/html" />',
                         auto_discovery_link('/app.html', title='My RSS', feed_type='text/html'))
        
    def test_image(self):
        eq_('<img alt="Xml" src="/images/xml.png" />',
                         image('/images/xml.png', "Xml"))
        eq_('<img alt="Xml" src="/images/xml.png" />',
                         image('/images/xml.png', alt="Xml"))
        eq_('<img alt="" src="/images/xml.png" />',
                         image('/images/xml.png', ""))
        eq_('<img alt="" src="/images/xml.png" />',
                         image('/images/xml.png', None))
        eq_('<img alt="rss syndication" src="/images/rss.png" />',
                         image('/images/rss.png', 'rss syndication'))
        eq_('<img alt="Gold" height="70" src="gold.png" width="45" />',
                         image('gold.png', "Gold", height=70, width=45))
        eq_('<img alt="Edit Entry" height="10" src="/images/icon.png" width="16" />',
                         image("/images/icon.png", height=10, width=16, alt="Edit Entry"))
        eq_('<img alt="Icon" height="16" src="/icons/icon.gif" width="16" />',
                         image("/icons/icon.gif", "Icon", height=16, width=16))
        eq_('<img alt="Icon" src="/icons/icon.gif" width="16" />',
                         image("/icons/icon.gif", "Icon", width=16))

    def test_javascript_include_tag(self):
        eq_("""<script src="/javascripts/prototype.js" type="text/javascript"></script>\n<script src="/other-javascripts/util.js" type="text/javascript"></script>""",
                         javascript_link('/javascripts/prototype.js', '/other-javascripts/util.js'))
        eq_("""<script defer="defer" src="/js/pngfix.js" type="text/javascript"></script>""",
                         javascript_link('/js/pngfix.js', defer=True))

    def test_stylesheet_link_tag(self):
        eq_(literal(u'<link href="/dir/file.css" media="all" rel="stylesheet" type="text/css" />'),
                         stylesheet_link('/dir/file.css', media='all'))
        eq_('<link href="style.css" media="all" rel="stylesheet" type="text/css" />',
                         stylesheet_link('style.css', media='all'))
        eq_('<link href="/random.styles" media="screen" rel="stylesheet" type="text/css" />\n<link href="/css/stylish.css" media="screen" rel="stylesheet" type="text/css" />',
                         stylesheet_link('/random.styles', '/css/stylish.css'))

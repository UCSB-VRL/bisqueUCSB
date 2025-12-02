import datetime

from nose.tools import eq_

import webhelpers.feedgenerator as fg

def test_simple_feed():
    pubdate = datetime.datetime(2009, 12, 18, 23, 45, 12)
    feed = fg.Rss201rev2Feed(
        title=u"Poynter E-Media Tidbits",
        link=u"http://www.poynter.org/column.asp?id=31",
        description=u"A group weblog by the sharpest minds in online media/journalism/publishing.",
        language=u"en",
    )
    feed.add_item(
        title="Hello", 
        link=u"http://www.holovaty.com/test/",
        description="Testing.",  
        pubdate=pubdate)
    result = feed.writeString("utf-8")
    control = """<?xml version="1.0" encoding="utf-8"?>\n<rss version="2.0"><channel><title>Poynter E-Media Tidbits</title><link>http://www.poynter.org/column.asp?id=31</link><description>A group weblog by the sharpest minds in online media/journalism/publishing.</description><language>en</language><lastBuildDate>Fri, 18 Dec 2009 23:45:12 -0000</lastBuildDate><item><title>Hello</title><link>http://www.holovaty.com/test/</link><description>Testing.</description><pubDate>Fri, 18 Dec 2009 23:45:12 -0000</pubDate></item></channel></rss>"""
    eq_(result, control)


def test_escaping():
    pubdate = datetime.datetime(2009, 12, 18, 23, 45, 12)
    feed = fg.Rss201rev2Feed(
        title=u"Poynter E-Media Tidbits",
        link=u"http://www.poynter.org/column.asp?id=31",
        description=u"A group weblog by the <em>sharpest</em> minds in online media & journalism.",
        language=u"en",
    )
    feed.add_item(
        title="Hello", 
        link=u"http://www.holovaty.com/test/",
        description="Testing.",  
        pubdate=pubdate)
    result = feed.writeString("utf-8")
    control = """<?xml version="1.0" encoding="utf-8"?>\n<rss version="2.0"><channel><title>Poynter E-Media Tidbits</title><link>http://www.poynter.org/column.asp?id=31</link><description>A group weblog by the &lt;em&gt;sharpest&lt;/em&gt; minds in online media &amp; journalism.</description><language>en</language><lastBuildDate>Fri, 18 Dec 2009 23:45:12 -0000</lastBuildDate><item><title>Hello</title><link>http://www.holovaty.com/test/</link><description>Testing.</description><pubDate>Fri, 18 Dec 2009 23:45:12 -0000</pubDate></item></channel></rss>"""
    eq_(result, control)

def test_geo_point_feed():
    pubdate = datetime.datetime(2009, 12, 18, 23, 45, 12)
    feed = fg.GeoAtom1Feed(
        title=u"Poynter E-Media Tidbits",
        link=u"http://www.poynter.org/column.asp?id=31",
        description=u"A group weblog by the sharpest minds in online media/journalism/publishing.",
        language=u"en",
    )
    feed.add_item(
        title="Hello", 
        link=u"http://www.holovaty.com/test/",
        description="Testing.",  
        pubdate=pubdate,
        geometry=(-120.5, 50.5))
    result = feed.writeString("utf-8")
    f = open("/tmp/feed", "w")
    f.write(result)
    f.close()
    control = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:georss="http://www.georss.org/georss" xml:lang="en"><title>Poynter E-Media Tidbits</title><link href="http://www.poynter.org/column.asp?id=31" rel="alternate"></link><id>http://www.poynter.org/column.asp?id=31</id><updated>2009-12-18T23:45:12Z</updated><entry><title>Hello</title><link href="http://www.holovaty.com/test/" rel="alternate"></link><updated>2009-12-18T23:45:12Z</updated><published>2009-12-18T23:45:12Z</published><id>tag:www.holovaty.com,2009-12-18:/test/</id><summary type="html">Testing.</summary><georss:point>-120.500000 50.500000</georss:point></entry></feed>"""
    eq_(result, control)

def test_geo_point_feed_longitude_first():
    pubdate = datetime.datetime(2009, 12, 18, 23, 45, 12)
    feed = fg.GeoAtom1Feed(
        title=u"Poynter E-Media Tidbits",
        link=u"http://www.poynter.org/column.asp?id=31",
        description=u"A group weblog by the sharpest minds in online media/journalism/publishing.",
        language=u"en",
    )
    feed.is_input_latitude_first = False
    feed.add_item(
        title="Hello", 
        link=u"http://www.holovaty.com/test/",
        description="Testing.",  
        pubdate=pubdate,
        geometry=(50.5, -120.5))
    result = feed.writeString("utf-8")
    f = open("/tmp/feed", "w")
    f.write(result)
    f.close()
    control = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:georss="http://www.georss.org/georss" xml:lang="en"><title>Poynter E-Media Tidbits</title><link href="http://www.poynter.org/column.asp?id=31" rel="alternate"></link><id>http://www.poynter.org/column.asp?id=31</id><updated>2009-12-18T23:45:12Z</updated><entry><title>Hello</title><link href="http://www.holovaty.com/test/" rel="alternate"></link><updated>2009-12-18T23:45:12Z</updated><published>2009-12-18T23:45:12Z</published><id>tag:www.holovaty.com,2009-12-18:/test/</id><summary type="html">Testing.</summary><georss:point>-120.500000 50.500000</georss:point></entry></feed>"""
    eq_(result, control)

# -*- coding: utf-8 -*-
from util import WebHelpersTestCase
import unittest

from webhelpers.html import HTML
from webhelpers.html.tags import *

class Holder(object):
    def __init__(self, settings):
        for k,v in settings.iteritems():
            setattr(self, k, v)
            
class TestModelTagsHelperWithObject(WebHelpersTestCase):
    def setUp(self):
        super(TestModelTagsHelperWithObject, self).setUp()
        obj = Holder({'name':'Jim', 'phone':'123-456-7890', 'fulltime':True, 'fired':False, 'password':'bacon', 'longtext':"lorem ipsum lorem ipsum\n"*10, 'favcolor':'blue', 'lang':'en'})
        self.m = ModelTags(obj)
        
    def test_check_box(self):
        self.assertEqual(
            self.m.checkbox("fulltime"),
            u'<input checked="checked" id="fulltime" name="fulltime" type="checkbox" value="1" />',
        )

    def test_hidden_field(self):
        self.assertEqual(
            self.m.hidden("name"),
            u'<input id="name" name="name" type="hidden" value="Jim" />'
        )

    def test_password_field(self):
        self.assertEqual(
            self.m.password('name'), 
            u'<input id="name" name="name" type="password" value="Jim" />'
        )
    def test_file_field(self):
        self.assertEqual(
            self.m.file('name'), 
            u'<input id="name" name="name" type="file" value="Jim" />'
        )

    def test_radio_button(self):
        self.assertEqual(
            self.m.radio("favcolor", "blue"),
            u'<input checked="checked" id="favcolor_blue" name="favcolor" type="radio" value="blue" />'
        )
        
        self.assertEqual(
            self.m.radio("favcolor", "red"),
            u'<input id="favcolor_red" name="favcolor" type="radio" value="red" />'
        )


    def test_text_area(self):
        self.assertEqual(
            self.m.textarea("longtext"),
            u'<textarea id="longtext" name="longtext">lorem ipsum lorem ipsum\nlorem ipsum lorem ipsum\nlorem ipsum lorem ipsum\nlorem ipsum lorem ipsum\nlorem ipsum lorem ipsum\nlorem ipsum lorem ipsum\nlorem ipsum lorem ipsum\nlorem ipsum lorem ipsum\nlorem ipsum lorem ipsum\nlorem ipsum lorem ipsum\n</textarea>'
        )

    def test_text_field(self):
        self.assertEqual(
            self.m.text("name"),
            u'<input id="name" name="name" type="text" value="Jim" />'
        )
    def test_select(self):
        self.assertEqual(
            self.m.select("lang", [("en", "English"), ("de", "German"), ("jp", "Japanese")]),
            u'<select id="lang" name="lang">\n<option selected="selected" value="en">English</option>\n<option value="de">German</option>\n<option value="jp">Japanese</option>\n</select>'
        )

class TestModelTagsHelperWithDict(TestModelTagsHelperWithObject):
    def setUp(self):
        super(TestModelTagsHelperWithObject, self).setUp()
        obj = {'name':'Jim', 'phone':'123-456-7890', 'fulltime':True, 'fired':False, 'password':'bacon', 'longtext':"lorem ipsum lorem ipsum\n"*10, 'favcolor':'blue', 'lang':'en'}
        self.m = ModelTags(obj, use_keys=True)

    def test_check_box(self):
        self.assertEqual(
            self.m.checkbox("fulltime"),
            u'<input checked="checked" id="fulltime" name="fulltime" type="checkbox" value="1" />',
        )

    def test_hidden_field(self):
        self.assertEqual(
            self.m.hidden("name"),
            u'<input id="name" name="name" type="hidden" value="Jim" />'
        )

    def test_password_field(self):
        self.assertEqual(
            self.m.password('name'), 
            u'<input id="name" name="name" type="password" value="Jim" />'
        )
    def test_file_field(self):
        self.assertEqual(
            self.m.file('name'), 
            u'<input id="name" name="name" type="file" value="Jim" />'
        )

    def test_radio_button(self):
        self.assertEqual(
            self.m.radio("favcolor", "blue"),
            u'<input checked="checked" id="favcolor_blue" name="favcolor" type="radio" value="blue" />'
        )

        self.assertEqual(
            self.m.radio("favcolor", "red"),
            u'<input id="favcolor_red" name="favcolor" type="radio" value="red" />'
        )


    def test_text_area(self):
        self.assertEqual(
            self.m.textarea("longtext"),
            u'<textarea id="longtext" name="longtext">lorem ipsum lorem ipsum\nlorem ipsum lorem ipsum\nlorem ipsum lorem ipsum\nlorem ipsum lorem ipsum\nlorem ipsum lorem ipsum\nlorem ipsum lorem ipsum\nlorem ipsum lorem ipsum\nlorem ipsum lorem ipsum\nlorem ipsum lorem ipsum\nlorem ipsum lorem ipsum\n</textarea>'
        )

    def test_text_field(self):
        self.assertEqual(
            self.m.text("name"),
            u'<input id="name" name="name" type="text" value="Jim" />'
        )
    def test_select(self):
        self.assertEqual(
            self.m.select("lang", [("en", "English"), ("de", "German"), ("jp", "Japanese")]),
            u'<select id="lang" name="lang">\n<option selected="selected" value="en">English</option>\n<option value="de">German</option>\n<option value="jp">Japanese</option>\n</select>'
        )

class TestModelTagsHelperWithIdGeneration(TestModelTagsHelperWithObject):
    def setUp(self):
        super(TestModelTagsHelperWithObject, self).setUp()
        obj = Holder({'name':'Jim', 'phone':'123-456-7890', 'fulltime':True, 'fired':False, 'password':'bacon', 'longtext':"lorem ipsum lorem ipsum\n"*10, 'favcolor':'blue', 'lang':'en'})
        self.m = ModelTags(obj, id_format='person:%s')

    def test_check_box(self):
        self.assertEqual(
            self.m.checkbox("fulltime"),
            u'<input checked="checked" id="person:fulltime" name="fulltime" type="checkbox" value="1" />',
        )

    def test_hidden_field(self):
        self.assertEqual(
            self.m.hidden("name"),
            u'<input id="person:name" name="name" type="hidden" value="Jim" />'
        )

    def test_password_field(self):
        self.assertEqual(
            self.m.password('name'), 
            u'<input id="person:name" name="name" type="password" value="Jim" />'
        )
    def test_file_field(self):
        self.assertEqual(
            self.m.file('name'), 
            u'<input id="person:name" name="name" type="file" value="Jim" />'
        )

    def test_radio_button(self):
        self.assertEqual(
            self.m.radio("favcolor", "blue"),
            u'<input checked="checked" id="person:favcolor_blue" name="favcolor" type="radio" value="blue" />'
        )

        self.assertEqual(
            self.m.radio("favcolor", "red"),
            u'<input id="person:favcolor_red" name="favcolor" type="radio" value="red" />'
        )


    def test_text_area(self):
        self.assertEqual(
            self.m.textarea("longtext"),
            u'<textarea id="person:longtext" name="longtext">lorem ipsum lorem ipsum\nlorem ipsum lorem ipsum\nlorem ipsum lorem ipsum\nlorem ipsum lorem ipsum\nlorem ipsum lorem ipsum\nlorem ipsum lorem ipsum\nlorem ipsum lorem ipsum\nlorem ipsum lorem ipsum\nlorem ipsum lorem ipsum\nlorem ipsum lorem ipsum\n</textarea>'
        )

    def test_text_field(self):
        self.assertEqual(
            self.m.text("name"),
            u'<input id="person:name" name="name" type="text" value="Jim" />'
        )
    def test_select(self):
        self.assertEqual(
            self.m.select("lang", [("en", "English"), ("de", "German"), ("jp", "Japanese")]),
            u'<select id="person:lang" name="lang">\n<option selected="selected" value="en">English</option>\n<option value="de">German</option>\n<option value="jp">Japanese</option>\n</select>'
        )

class TestModelTagsHelperWithoutObject(WebHelpersTestCase):
    def setUp(self):
        super(TestModelTagsHelperWithoutObject, self).setUp()
        obj = ''
        self.m = ModelTags(obj)
        
    def test_check_box(self):
        self.assertEqual(
            self.m.checkbox("fulltime"),
            u'<input id="fulltime" name="fulltime" type="checkbox" value="1" />',
        )

    def test_hidden_field(self):
        self.assertEqual(
            self.m.hidden("name"),
            u'<input id="name" name="name" type="hidden" value="" />'
        )

    def test_password_field(self):
        self.assertEqual(
            self.m.password('name'), 
            u'<input id="name" name="name" type="password" value="" />'
        )
    def test_file_field(self):
        self.assertEqual(
            self.m.file('name'), 
            u'<input id="name" name="name" type="file" value="" />'
        )

    def test_radio_button(self):
        self.assertEqual(
            self.m.radio("favcolor", "blue"),
            u'<input id="favcolor_blue" name="favcolor" type="radio" value="blue" />'
        )
        
        self.assertEqual(
            self.m.radio("favcolor", "red"),
            u'<input id="favcolor_red" name="favcolor" type="radio" value="red" />'
        )


    def test_text_area(self):
        self.assertEqual(
            self.m.textarea("longtext"),
            u'<textarea id="longtext" name="longtext"></textarea>'
        )

    def test_text_field(self):
        self.assertEqual(
            self.m.text("name"),
            u'<input id="name" name="name" type="text" value="" />'
        )
    def test_select(self):
        self.assertEqual(
            self.m.select("lang", [("en", "English"), ("de", "German"), ("jp", "Japanese")]),
            u'<select id="lang" name="lang">\n<option value="en">English</option>\n<option value="de">German</option>\n<option value="jp">Japanese</option>\n</select>'
        )        
if __name__ == '__main__':
    suite = map(unittest.makeSuite, [
        TestModelTagsHelperWithObject,
        TestModelTagsHelperWithDict,
        TestModelTagsHelperWithIdGeneration,
        TestModelTagsHelperWithoutObject
        ])
    for testsuite in suite:
        unittest.TextTestRunner(verbosity=1).run(testsuite)

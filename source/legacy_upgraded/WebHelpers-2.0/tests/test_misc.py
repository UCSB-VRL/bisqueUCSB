from nose.tools import eq_

from webhelpers.misc import *

def by_name(class_):
    return class_.__name__

#### Simple test

class DummyBase(object):  pass
class Subclass1(DummyBase):  pass
class Subclass2(DummyBase):  pass

def test_subclasses_only():
    subclasses = subclasses_only(DummyBase, globals())
    subclasses.sort(key=by_name)
    control = [Subclass1, Subclass2]
    eq_(subclasses, control)

#### Tea test

class Tea(object):  pass

# Abstract subclasses
class Black(Tea):  pass
class Green(Tea):  pass

# Concrete classes (grandchildren)
class EnglishBreakfast(Black):  pass
class Sencha(Green):  pass
class EarlGrey(Black):  pass
class JasminePearl(Green):  pass

def test_subclasses_only_with_exclude():
    subclasses = subclasses_only(Tea, globals(), [Black, Green])
    subclasses.sort(key=by_name)
    control = [EarlGrey, EnglishBreakfast, JasminePearl, Sencha]
    eq_(subclasses, control)

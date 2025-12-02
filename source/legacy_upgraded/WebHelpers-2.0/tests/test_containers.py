# -*- coding: utf-8 -*-
import os
import copy
import tempfile

from nose.tools import eq_

from util import raises

from webhelpers.containers import DumbObject
from webhelpers.containers import defaultdict as webhelpers_containers_defaultdict
from webhelpers.containers import distribute, get_many

# Tests from Python 2.5 test_defaultdict_defaultdict.py, as this is just a 2.4 backport
# anyway
def foobar():
    return list

def test_defaultdict_basic():
    d1 = webhelpers_containers_defaultdict()
    eq_(d1.default_factory, None)
    d1.default_factory = list
    d1[12].append(42)
    eq_(d1, {12: [42]})
    d1[12].append(24)
    eq_(d1, {12: [42, 24]})
    d1[13]
    d1[14]
    eq_(d1, {12: [42, 24], 13: [], 14: []})
    assert d1[12] is not d1[13] is not d1[14]
    d2 = webhelpers_containers_defaultdict(list, foo=1, bar=2)
    eq_(d2.default_factory, list)
    eq_(d2, {"foo": 1, "bar": 2})
    eq_(d2["foo"], 1)
    eq_(d2["bar"], 2)
    eq_(d2[42], [])
    assert "foo" in d2
    assert "foo" in d2.keys()
    assert "bar" in d2
    assert "bar" in d2.keys()
    assert 42 in d2
    assert 42 in d2.keys()
    assert 12 not in d2
    assert 12 not in d2.keys()
    d2.default_factory = None
    eq_(d2.default_factory, None)
    try:
        d2[15]
    except KeyError, err:
        eq_(err.args, (15,))
    else:
        message = "d2[15] didn't raise KeyError"
        raise AssertionError(message)

def test_defaultdict_missing():
    d1 = webhelpers_containers_defaultdict()
    try:
        d1.__missing__(42)
    except KeyError:
        pass
    else:
        raise AssertionError("d1.__missing__ did not raise KeyError")
    d1.default_factory = list
    eq_(d1.__missing__(42), [])

def test_defaultdict_repr():
    d1 = webhelpers_containers_defaultdict()
    eq_(d1.default_factory, None)
    eq_(repr(d1), "defaultdict(None, {})")
    d1[11] = 41
    eq_(repr(d1), "defaultdict(None, {11: 41})")

def test_defaultdict_repr_2():
    def foo(): return 43
    d3 = webhelpers_containers_defaultdict(foo)
    assert d3.default_factory is foo
    d3[13]
    eq_(repr(d3), "defaultdict(%s, {13: 43})" % repr(foo))

def test_defaultdict_print():
    d1 = webhelpers_containers_defaultdict()
    def foo(): return 42
    d2 = webhelpers_containers_defaultdict(foo, {1: 2})
    # NOTE: We can't use tempfile.[Named]TemporaryFile since this
    # code must exercise the tp_print C code, which only gets
    # invoked for *real* files.
    tfn = tempfile.mktemp()
    try:
        f = open(tfn, "w+")
        try:
            print >>f, d1
            print >>f, d2
            f.seek(0)
            eq_(f.readline(), repr(d1) + "\n")
            eq_(f.readline(), repr(d2) + "\n")
        finally:
            f.close()
    finally:
        os.remove(tfn)

def test_defaultdict_copy():
    d1 = webhelpers_containers_defaultdict()
    d2 = d1.copy()
    eq_(type(d2), webhelpers_containers_defaultdict)
    eq_(d2.default_factory, None)
    eq_(d2, {})
    d1.default_factory = list
    d3 = d1.copy()
    eq_(type(d3), webhelpers_containers_defaultdict)
    eq_(d3.default_factory, list)
    eq_(d3, {})
    d1[42]
    d4 = d1.copy()
    eq_(type(d4), webhelpers_containers_defaultdict)
    eq_(d4.default_factory, list)
    eq_(d4, {42: []})
    d4[12]
    eq_(d4, {42: [], 12: []})

def test_defaultdict_shallow_copy():
    d1 = webhelpers_containers_defaultdict(foobar, {1: 1})
    d2 = copy.copy(d1)
    eq_(d2.default_factory, foobar)
    eq_(d2, d1)
    d1.default_factory = list
    d2 = copy.copy(d1)
    eq_(d2.default_factory, list)
    eq_(d2, d1)

def test_defaultdict_deep_copy():
    d1 = webhelpers_containers_defaultdict(foobar, {1: [1]})
    d2 = copy.deepcopy(d1)
    eq_(d2.default_factory, foobar)
    eq_(d2, d1)
    assert d1[1] is not d2[1]
    d1.default_factory = list
    d2 = copy.deepcopy(d1)
    eq_(d2.default_factory, list)
    eq_(d2, d1)

def test_distribute():
        food = ["apple", "banana", "carrot", "daikon", "egg", "fish", "gelato", "honey"]
        eq_(distribute(food, 3, "H", ""), [['apple', 'banana', 'carrot'], ['daikon', 'egg', 'fish'], ['gelato', 'honey', '']])
        eq_(distribute(food, 3, "V", ""), [['apple', 'daikon', 'gelato'], ['banana', 'egg', 'honey'], ['carrot', 'fish', '']])
        eq_(distribute(food, 2, "H", ""), [['apple', 'banana'], ['carrot', 'daikon'], ['egg', 'fish'], ['gelato', 'honey']])
        eq_(distribute(food, 2, "V", ""), [['apple', 'egg'], ['banana', 'fish'], ['carrot', 'gelato'], ['daikon', 'honey']])

def test_distribute_with_extra():
        food = ["apple", "banana", "carrot", "daikon", "egg", "fish", "gelato", "honey", "EXTRA"]
        eq_(distribute(food, 3, "H", ""), [['apple', 'banana', 'carrot'], ['daikon', 'egg', 'fish'], ['gelato', 'honey', 'EXTRA']])
        eq_(distribute(food, 3, "V", ""), [['apple', 'daikon', 'gelato'], ['banana', 'egg', 'honey'], ['carrot', 'fish', 'EXTRA']])
        eq_(distribute(food, 2, "H", ""), [['apple', 'banana'], ['carrot', 'daikon'], ['egg', 'fish'], ['gelato', 'honey'], ['EXTRA', '']])
        eq_(distribute(food, 2, "V", ""), [['apple', 'fish'], ['banana', 'gelato'], ['carrot', 'honey'], ['daikon', 'EXTRA'], ['egg', '']])

def test_get_many():
    # Dict with keys and values of 0, 1, 2, 3, 4
    params = dict((n,n) for n in range(5))

    eq_(get_many(params), [])
    eq_(get_many(params, required=[1, 2]), [1, 2])
    eq_(get_many(params, optional=[1, 2]), [1, 2])
    eq_(get_many(params, optional=[6, 7, 8]), [None, None, None])
    eq_(get_many(params, one_of=[1, 2]), [1])
    eq_(get_many(params, one_of=[6, 1]), [1])

    eq_(get_many(params, optional=[6, 1]), [None, 1])
    eq_(get_many(params, required=[1, 2], optional=[6, 1]), [1, 2, None, 1])
    eq_(get_many(params, required=[1, 2], optional=[6, 1], one_of=[7, 8, 3]), [1, 2, None, 1, 3])

    raises(KeyError, get_many, params, required=[1, 6])
    raises(KeyError, get_many, params, one_of=[7, 6])

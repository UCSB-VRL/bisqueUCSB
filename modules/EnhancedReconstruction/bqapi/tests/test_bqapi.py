import pytest

from lxml import etree
from bqapi import BQSession
from bqapi.bqclass import BQFactory
from tg import config


pytestmark = pytest.mark.functional



def test_load (session):
    'Check that loading works'

    #host = config.get ('host.root')
    #user = config.get ('host.user')
    #passwd = config.get ('host.password')
    #bq = BQSession()
    #bq.init_local (user, passwd, bisque_root = host, create_mex = False)
    x = session.load ('/data_service/image/?limit=10')
    print "loading /data_service/images->", BQFactory.to_string((x))


def test_load_pixels(session):
    'check that you can load pixels from an image'
    #bq = BQSession()
    x = session.load ('/data_service/image/?limit=10')

    if len(x.kids):
        i0 = x.kids[0]
        pixels = i0.pixels().slice(z=1,t=1).fetch()
        print len(pixels)

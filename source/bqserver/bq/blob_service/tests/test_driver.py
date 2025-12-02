
import os
import pytest
from io import StringIO, BytesIO
import shutil
import shortuuid

from bq.blob_service.controllers.blob_drivers import make_storage_driver
from bqapi import BQSession


@pytest.fixture(scope="module")
def admin_session():
    """Admin session with enhanced authentication"""
    session = BQSession()
    session.init_local('admin', 'admin', bisque_root='http://localhost:8080')
    return session


@pytest.fixture(scope="module")
def user_session():
    """User session with enhanced authentication"""
    session = BQSession()
    session.init_local('admin', 'admin', bisque_root='http://localhost:8080')
    return session



pytestmark = pytest.mark.unit

local_driver = {
    'mount_url' : 'file://tests/tests',
    'top' : 'file://tests/tests',
}
MSG=b'A'*10

TSTDIR="tests/tests"



@pytest.fixture(scope='module')
def test_dir ():
    tstdir = TSTDIR + shortuuid.uuid()
    if not os.path.exists (tstdir):
        os.makedirs (tstdir)
    yield tstdir
    shutil.rmtree (tstdir)




def test_local_valid():
    drv = make_storage_driver (**local_driver)
    assert drv.valid ("file://tests/tests/a.jpg"), 'valid url fails'
    #assert drv.valid ("tests/tests/a.jpg"), 'valid url fails'
    assert not drv.valid ("/tests/tests/a.jpg"), 'invalid url passes'



def test_local_write (test_dir):
    drv = make_storage_driver (**local_driver)

    sf = BytesIO(MSG)
    sf.name = 'none'
    storeurl, localpath = drv.push (sf, 'file://%s/msg.txt' % test_dir)
    print("GOT", storeurl, localpath)

    assert os.path.exists (localpath), "Created file exists"

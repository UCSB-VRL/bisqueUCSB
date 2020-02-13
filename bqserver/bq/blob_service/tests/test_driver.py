
import os
import pytest
from StringIO import StringIO
import shutil
import shortuuid

from bq.blob_service.controllers.blob_drivers import make_storage_driver



pytestmark = pytest.mark.unit

local_driver = {
    'mount_url' : 'file://tests/tests',
    'top' : 'file://tests/tests',
}
MSG='A'*10

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

    sf = StringIO(MSG)
    sf.name = 'none'
    storeurl, localpath = drv.push (sf, 'file://%s/msg.txt' % test_dir)
    print "GOT", storeurl, localpath

    assert os.path.exists (localpath), "Created file exists"

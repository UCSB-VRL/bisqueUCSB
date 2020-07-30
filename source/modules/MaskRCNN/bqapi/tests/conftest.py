##
## Add local fixtures here
import pytest
from collections import OrderedDict, namedtuple

from bq.util.bunch import Bunch
from bq.util.mkdir import _mkdir
from .util import  fetch_file
from bqapi import BQServer

@pytest.fixture(scope="module")
def server():
    return BQServer()


LocalFile = namedtuple('LocalFile', ['name', 'location'])

@pytest.fixture(scope="module")
def stores(config):
    samples = config.store.samples_url
    inputs = config.store.input_dir
    results = config.store.results_dir
    _mkdir(results)

    files = []
    for name in [ x.strip() for x in config.store.files.split() ]:
        print "Fetching", name
        files.append (LocalFile (name, fetch_file(name, samples, inputs)))

    return Bunch(samples=samples, inputs=inputs, results=results, files=files)

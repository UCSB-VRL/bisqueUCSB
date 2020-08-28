
import pytest

@pytest.fixture(scope="class")
def testapp(request, application):
    request.cls.app = application

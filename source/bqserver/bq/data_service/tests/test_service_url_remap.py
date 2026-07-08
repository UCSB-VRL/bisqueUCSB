import pytest

from bq.core.service_urls import remap_bisque_service_xml

pytestmark = pytest.mark.unit


def test_remaps_data_service_xml_to_internal_request_origin():
    xml = """
    <image uri="http://bisque.localhost:8080/data_service/00-image"
           owner="http://bisque.localhost:8080/data_service/00-user"
           type="http://bisque.localhost:8080/data_service/00-module">
      <tag name="source" value="http://bisque.localhost:8080/image_service/00-image"/>
      <tag name="external" value="https://example.org/data_service/00-external"/>
      <tag name="client" value="http://bisque.localhost:8080/client_service/view"/>
    </image>
    """

    remapped, rewritten = remap_bisque_service_xml(
        xml,
        ("http://bisque.localhost", "http://bisque:8080"),
        "http://bisque:8080",
        allow_same_host=True,
    )

    assert rewritten == 4
    assert "http://bisque:8080/data_service/00-image" in remapped
    assert "http://bisque:8080/data_service/00-user" in remapped
    assert "http://bisque:8080/data_service/00-module" in remapped
    assert "http://bisque:8080/image_service/00-image" in remapped
    assert "https://example.org/data_service/00-external" in remapped
    assert "http://bisque.localhost:8080/client_service/view" in remapped


def test_leaves_data_service_xml_unchanged_for_external_origin():
    xml = '<image uri="https://external.example/data_service/00-image"/>'

    remapped, rewritten = remap_bisque_service_xml(
        xml,
        ("http://bisque.localhost", "http://bisque:8080"),
        "http://bisque:8080",
        allow_same_host=True,
    )

    assert rewritten == 0
    assert remapped == xml

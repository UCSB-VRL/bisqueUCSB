import pytest
from bq.module_service.controllers.module_server import (
    canonicalize_mex_output_urls,
    remap_mex_service_urls,
)
from lxml import etree

pytestmark = pytest.mark.unit


def _mex(xml):
    return etree.XML(xml)


def test_canonicalizes_docker_callback_output_url_to_relative_path():
    mex = _mex(
        """
        <mex value="FINISHED">
          <tag name="outputs">
            <tag name="Output Image"
                 value="http://host.docker.internal:8081/data_service/00-result"/>
          </tag>
        </mex>
        """
    )

    rewritten = canonicalize_mex_output_urls(mex, roots=["http://host.docker.internal:8081"])

    assert rewritten == 1
    assert mex.xpath('string(./tag[@name="outputs"]/tag[@name="Output Image"]/@value)') == (
        "/data_service/00-result"
    )


def test_canonicalizes_internal_output_url_with_query_and_fragment():
    mex = _mex(
        """
        <mex value="FINISHED">
          <tag name="outputs">
            <tag name="Preview"
                 value="http://127.0.0.1:8080/image_service/00-result?tile=0#view"/>
          </tag>
        </mex>
        """
    )

    rewritten = canonicalize_mex_output_urls(mex, roots=["http://127.0.0.1:8080"])

    assert rewritten == 1
    assert mex.xpath('string(./tag[@name="outputs"]/tag[@name="Preview"]/@value)') == (
        "/image_service/00-result?tile=0#view"
    )


def test_canonicalizes_same_origin_with_default_port():
    mex = _mex(
        """
        <mex value="FINISHED">
          <tag name="outputs">
            <tag name="Output Image" value="http://bisque.example/data_service/00-result"/>
          </tag>
        </mex>
        """
    )

    rewritten = canonicalize_mex_output_urls(mex, roots=["http://bisque.example:80"])

    assert rewritten == 1
    assert mex.xpath('string(./tag[@name="outputs"]/tag[@name="Output Image"]/@value)') == (
        "/data_service/00-result"
    )


def test_leaves_relative_external_and_input_urls_unchanged():
    mex = _mex(
        """
        <mex value="FINISHED">
          <tag name="inputs">
            <tag name="Input Image"
                 value="http://host.docker.internal:8081/data_service/00-input"/>
          </tag>
          <tag name="outputs">
            <tag name="Relative" value="/data_service/00-relative"/>
            <tag name="External" value="https://example.org/data_service/00-external"/>
            <tag name="Other Path"
                 value="http://host.docker.internal:8081/client_service/view"/>
          </tag>
        </mex>
        """
    )

    rewritten = canonicalize_mex_output_urls(mex, roots=["http://host.docker.internal:8081"])

    assert rewritten == 0
    assert mex.xpath('string(./tag[@name="inputs"]/tag[@name="Input Image"]/@value)') == (
        "http://host.docker.internal:8081/data_service/00-input"
    )
    assert mex.xpath('string(./tag[@name="outputs"]/tag[@name="Relative"]/@value)') == (
        "/data_service/00-relative"
    )
    assert mex.xpath('string(./tag[@name="outputs"]/tag[@name="External"]/@value)') == (
        "https://example.org/data_service/00-external"
    )
    assert mex.xpath('string(./tag[@name="outputs"]/tag[@name="Other Path"]/@value)') == (
        "http://host.docker.internal:8081/client_service/view"
    )


def test_remaps_mex_service_urls_to_internal_request_origin():
    mex = _mex(
        """
        <mex uri="http://bisque.localhost:8080/module_service/mex/00-mex">
          <tag name="inputs">
            <tag name="Input Image"
                 value="http://bisque.localhost:8080/data_service/00-input"/>
          </tag>
        </mex>
        """
    )

    rewritten = remap_mex_service_urls(
        mex,
        target_root="http://bisque:8080",
        roots=["http://bisque.localhost:8080"],
    )

    assert rewritten == 2
    assert mex.get("uri") == "http://bisque:8080/module_service/mex/00-mex"
    assert mex.xpath('string(./tag[@name="inputs"]/tag[@name="Input Image"]/@value)') == (
        "http://bisque:8080/data_service/00-input"
    )


def test_remaps_public_url_with_explicit_local_port_to_internal_request_origin():
    mex = _mex(
        """
        <mex uri="http://bisque.localhost:8080/module_service/mex/00-mex">
          <tag name="inputs">
            <tag name="Input Image"
                 value="http://bisque.localhost:8080/data_service/00-input"/>
          </tag>
        </mex>
        """
    )

    rewritten = remap_mex_service_urls(
        mex,
        target_root="http://bisque:8080",
        roots=["http://bisque.localhost"],
    )

    assert rewritten == 2
    assert mex.get("uri") == "http://bisque:8080/module_service/mex/00-mex"
    assert mex.xpath('string(./tag[@name="inputs"]/tag[@name="Input Image"]/@value)') == (
        "http://bisque:8080/data_service/00-input"
    )


def test_remaps_mex_service_urls_to_public_request_origin():
    mex = _mex(
        """
        <mex uri="http://bisque:8080/module_service/mex/00-mex">
          <tag name="inputs">
            <tag name="Input Image" value="http://bisque:8080/data_service/00-input"/>
          </tag>
        </mex>
        """
    )

    rewritten = remap_mex_service_urls(
        mex,
        target_root="http://bisque.localhost:8080",
        roots=["http://bisque:8080"],
    )

    assert rewritten == 2
    assert mex.get("uri") == "http://bisque.localhost:8080/module_service/mex/00-mex"
    assert mex.xpath('string(./tag[@name="inputs"]/tag[@name="Input Image"]/@value)') == (
        "http://bisque.localhost:8080/data_service/00-input"
    )


def test_remap_mex_service_urls_leaves_external_urls_unchanged():
    mex = _mex(
        """
        <mex uri="https://external.example/module_service/mex/00-mex">
          <tag name="inputs">
            <tag name="Input Image" value="https://external.example/data_service/00-input"/>
          </tag>
        </mex>
        """
    )

    rewritten = remap_mex_service_urls(
        mex,
        target_root="http://bisque:8080",
        roots=["http://bisque.localhost:8080"],
    )

    assert rewritten == 0
    assert mex.get("uri") == "https://external.example/module_service/mex/00-mex"
    assert mex.xpath('string(./tag[@name="inputs"]/tag[@name="Input Image"]/@value)') == (
        "https://external.example/data_service/00-input"
    )

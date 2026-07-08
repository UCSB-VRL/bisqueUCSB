import pytest
from bq.engine.controllers.engine_service import EngineModuleResource
from lxml import etree

pytestmark = pytest.mark.unit


def module_resource(tmp_path, xml):
    resource = EngineModuleResource.__new__(EngineModuleResource)
    resource.path = str(tmp_path)
    resource.name = "ExampleModule"
    resource.module_xml = etree.fromstring(xml)
    resource.module_uri = lambda: "http://example.test/engine_service/ExampleModule"
    return resource


def test_definition_skips_missing_interface_files(tmp_path):
    resource = module_resource(
        tmp_path,
        """
        <module name="ExampleModule">
          <tag name="interface">
            <tag name="javascript" type="file" value="webapp.js" />
            <tag name="css" type="file" value="webapp.css" />
          </tag>
        </module>
        """,
    )

    definition = resource.definition_as_dict()

    assert "interface/javascript" not in definition
    assert "interface/css" not in definition
    assert definition["module/name"] == "ExampleModule"


def test_definition_keeps_existing_interface_files(tmp_path):
    (tmp_path / "webapp.js").write_text("console.log('module');")
    resource = module_resource(
        tmp_path,
        """
        <module name="ExampleModule">
          <tag name="interface">
            <tag name="javascript" type="file" value="webapp.js" />
          </tag>
        </module>
        """,
    )

    definition = resource.definition_as_dict()

    assert definition["interface/javascript"] == "webapp.js"

import pytest
from ply import lex

from bq.data_service.controllers import resource_query

pytestmark = pytest.mark.unit


def test_quoted_tag_query_token_supports_python_311_regex_rules():
    lexer = lex.lex(module=resource_query)
    lexer.input('"http://localhost:8080/data_service/00-test"')

    tokens = [(token.type, token.value) for token in lexer]

    assert tokens == [("TAGVAL", "http://localhost:8080/data_service/00-test")]

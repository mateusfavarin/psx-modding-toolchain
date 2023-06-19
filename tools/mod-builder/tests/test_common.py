"""
TODO: This breaks because common calls some functions repeatedly and immediately
"""
import pytest

import common

cases_build_id = (
    ([], None),
    (["These", "don't", "have", "ids"], None),
    (["", "-DBUILD=926", "", ""], 926),    
)
@pytest.mark.parametrize("list_tokens, expected", cases_build_id)
def test_extract_build_id(list_tokens, expected):
    assert common.extract_build_id(list_tokens, expected)

cases_makefiles = (
    ("tests/makefiles/fake_makefile", 926),
)
@pytest.mark.parametrize("fname, expected", cases_makefiles)
def test_get_build_id(fname, expected):
    assert common.get_build_id(fname) == expected
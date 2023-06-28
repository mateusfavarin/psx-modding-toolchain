import pytest

import redux

# cases_path_settings = (
#     ("tests/test_settings.json"),
# )
# @pytest.mark.parametrize("fname", cases_path_settings)
# def test_load_config(fname, expected):
def test_load_config():
    fname = "tests/fake_settings.json"
    instance_redux = redux.Redux()
    is_found = instance_redux.load_config(fname)
    assert not is_found

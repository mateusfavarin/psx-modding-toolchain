"""
Ensures reproducibility amongst the paths
"""
import pytest

import _files
cases_file = (
    ("common.py", True),
    ("../../games/Example_CrashTeamRacing/config.json", True),
    ("fake-file.txt", False)
)
@pytest.mark.parametrize("fname, expected", cases_file)
def test_check_file(fname, expected):
    assert _files.check_file(fname) == expected

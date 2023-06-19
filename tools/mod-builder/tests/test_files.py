"""
Ensures reproducibility amongst the paths

Arrange
Action
Assert
"""
import pytest

import _files
cases_file = (
    ("common.py", True),
    ("../../games/Example_CrashTeamRacing/config.json", True),
    ("buildList.txt", True), # common.COMPILE_LIST
    ("fake-file.txt", False)
)
@pytest.mark.parametrize("fname, expected", cases_file)
def test_check_file(fname, expected):
    assert _files.check_file(fname) == expected

cases_files = (
    (["common.py", "../../games/Example_CrashTeamRacing/config.json"], True),
    (["common.py", "../../games/Example_CrashTeamRacing/config.json", "fake.txt"], False),
    (["buildList.txt", "disc.json", "settings.json"], False), # prerequisites
)
@pytest.mark.parametrize("list_strings, expected", cases_files)
def test_check_files(list_strings, expected):
    assert _files.check_files(list_strings) == expected
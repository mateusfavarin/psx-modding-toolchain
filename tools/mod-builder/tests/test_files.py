"""
Ensures reproducibility amongst the paths

Arrange
Action
Assert
"""
import pathlib
import pytest

import _files

# fname, folder
cases_distance_to_file = (
    ("common.py", "tools", pathlib.Path.cwd()), # look in this directory
    ("mipsel-none-elf-gcc.rb", "tools", pathlib.Path.cwd().parents[1] / "tools" / "macos-mips"), # doesn't do an os.walk
    ("config.json", "psx-modding-toolchain", pathlib.Path.cwd().parents[1] / "games" / "Example_CrashTeamRacing"), # doesn't do an os.walk
    ("config.json", "tools", pathlib.Path.cwd().parents[1] / "tools" ), # didn't find it
)
@pytest.mark.parametrize("fname, folder, expected", cases_distance_to_file)
def test_file_distance(fname, folder, expected):
    # pytest.set_trace()
    assert _files.get_file_directory(fname, folder) == expected


def test_file_directory(fname, expected):
    assert _files.get_file_directory(fname) == expected

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
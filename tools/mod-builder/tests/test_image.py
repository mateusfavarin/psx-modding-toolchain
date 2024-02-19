import pathlib
import pytest

import image

@pytest.fixture(scope="module")
def image_directory():
    """ hard-coded directory """
    dirname = pathlib.Path(__file__).resolve().parents[3] / "games" / "Example_CrashTeamRacing" / "mods" / "TextureReplacement"
    yield dirname

cases_fnames = ( # fname stems
    "SPYRO_368_216_1_251_44_26_4",
    "ZERO_1_2_3_4_5_6_7",
)
@pytest.mark.parametrize("string", cases_fnames)
def test_check_naming_convention(string):
    assert image.Image.check_naming_convention(string)

def test_create_images(image_directory):
    """
    TODO: Replace hard-coded directory
    """
    print(image_directory)
    assert image.create_images(image_directory) == 1

def test_as_c_struct(image_directory):
    """
    TODO: create a fake image file
    """
    fname_image_texture = "SPYRO_368_216_1_251_44_26_4.png"
    instance = image.Image(image_directory / "newtex" / fname_image_texture)
    string_test = instance.as_c_struct()
    string_actual = ""
    with open(pathlib.Path.cwd() / "tests" / "spyro_c_struct.c", "r") as f:
        string_actual = f.read()
    print(string_actual)
    print(string_test)
    assert instance.is_valid()
    assert string_actual == string_test
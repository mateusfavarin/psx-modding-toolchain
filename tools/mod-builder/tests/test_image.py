import pathlib
import pytest

import image

cases_fnames = ( # fname stems
    "SPYRO_368_216_1_251_44_26_4",
    "ZERO_1_2_3_4_5_6_7",
)
@pytest.mark.parametrize("string", cases_fnames)
def test_check_naming_convention(string):
    assert image.Image.check_naming_convention(string)

def test_create_images():
    dirname = pathlib.Path(__file__).resolve().parents[3] / "games" / "Example_CrashTeamRacing" / "mods" / "TextureReplacement"
    print(dirname)
    # pytest.set_trace()
    assert image.create_images(dirname) == 0
    # count_images = 0
    # for root, _, files in os.walk(directory):
    #     for filename in files:
    #         if filename[-4:].lower() == ".png":
    #             count_images += 1
    #             path = root + filename
    #             img = Image(path)
    #             if img.is_valid():
    #                 imgs.append(img)
    #                 img.img2psx()
    #                 if img.pil_img.mode == "PA":
    #                     img.clut.add_indexed_colors(img.pil_img)
    # return count_images

def test_as_c_struct():
    """
    TODO: create a fake image file
    """
    fname_image_texture = "SPYRO_368_216_1_251_44_26_4"
    instance = image.Image(fname_image_texture)

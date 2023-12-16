import pathlib
import pytest

import compile_list

cases_replace = (
    ("// Include patches for PAL and NTSC-J", ",//, Include patches for PAL and NTSC-J"),
    ("// Include patches for PAL and NTSC-J //", ",//, Include patches for PAL and NTSC-J ,//,"),
    ("// Include patches // for PAL and NTSC-J //", ",//, Include patches ,//, for PAL and NTSC-J ,//,"),
    # no comment, no change
    ("1006, exe, 0x80012534, 0x0, ../../Patches/JpnModchips/src/jpnModchips.s","1006, exe, 0x80012534, 0x0, ../../Patches/JpnModchips/src/jpnModchips.s")
)
@pytest.mark.parametrize("string, expected", cases_replace)
def test_comment_replace(string, expected):
    comment = "//"
    assert string.replace(comment, f",{comment},") == expected

cases_tokens = (
    (",//, Include patches for PAL and NTSC-J", ["//", "Include patches for PAL and NTSC-J"]),
    (",//, Include patches for PAL and NTSC-J,//,", ["//","Include patches for PAL and NTSC-J","//"]),
    (",//, Include patches ,//, for PAL and NTSC-J,//,", ["//","Include patches","//","for PAL and NTSC-J","//"]),
    ("// Include anti-anti-piracy patches for PAL and NTSC-J",["// Include anti-anti-piracy patches for PAL and NTSC-J"]),
    ("1006, exe, 0x80012534, 0x0, ../../Patches/JpnModchips/src/jpnModchips.s",["1006", "exe", "0x80012534", "0x0","../../Patches/JpnModchips/src/jpnModchips.s"]),
    ("1111, exe, 0x80012570, 0x0, ../../Patches/JpnModchips/src/jpnModchips.s",["1111", "exe", "0x80012570", "0x0", "../../Patches/JpnModchips/src/jpnModchips.s"]),
    ("1020, exe, 0x80031cc8, 0x0, ../../Patches/EurLibcrypt/src/libcrypt.s",["1020", "exe", "0x80031cc8", "0x0", "../../Patches/EurLibcrypt/src/libcrypt.s"]),
    ('// Hooked at the end of BOTS_UpdateGlobals, which will make the code run every frame at all times, excluding the loading screen', ['// Hooked at the end of BOTS_UpdateGlobals', 'which will make the code run every frame at all times', 'excluding the loading screen'])
)
@pytest.mark.parametrize("string, expected", cases_tokens)
def test_tokenize_line(string, expected):
    assert compile_list.CompileList.tokenize_line(string) == expected

cases_commments = (
    (["//", "Include patches for PAL and NTSC-J"], []), # starts with comment
    (["//","Include patches for PAL and NTSC-J","//"], []), # starts with comment
    (["//","Include patches","//","for PAL and NTSC-J","//"], []), # starts with comment
    (["// Fake sentence "], ["// Fake sentence "]), # starts with comment but no commas
    (['// Hooked', 'which', 'excluding'], ['// Hooked', 'which', 'excluding']), # starts with comment with commas
    (["1006", "exe", "0x80012534", "0x0","../../Patches/JpnModchips/src/jpnModchips.s"], ["1006", "exe", "0x80012534", "0x0","../../Patches/JpnModchips/src/jpnModchips.s"]),
    (["1111", "exe", "0x80012570", "0x0", "../../Patches/JpnModchips/src/jpnModchips.s"], ["1111", "exe", "0x80012570", "0x0", "../../Patches/JpnModchips/src/jpnModchips.s"]),
    (["1020", "exe", "0x80031cc8", "0x0", "../../Patches/EurLibcrypt/src/libcrypt.s"], ["1020", "exe", "0x80031cc8", "0x0", "../../Patches/EurLibcrypt/src/libcrypt.s"]),
)
@pytest.mark.parametrize("list_strings, expected", cases_commments)
def test_skip_comments(list_strings, expected):
    assert compile_list.CompileList.skip_comments(list_strings) == expected

# "// Include anti-anti-piracy patches for PAL and NTSC-J"
# "1006, exe, 0x80012534, 0x0, ../../Patches/JpnModchips/src/jpnModchips.s"
# "1111, exe, 0x80012570, 0x0, ../../Patches/JpnModchips/src/jpnModchips.s"
# "1020, exe, 0x80031cc8, 0x0, ../../Patches/EurLibcrypt/src/libcrypt.s"

# "// Compile the code in the empty space in RDATA"
# "common, exe, rdata_free, 0x0, src/main.c src/menubox.c"

# "// Compile the ASM injection that will load our code"
# '// ASM injections for loading modded functions are typically done at the "jr ra" or "return" instruction of a function, which is 8 bytes away from the start of the function that follows it
# '// Hooked at the end of BOTS_UpdateGlobals, which will make the code run every frame at all times, excluding the loading screen'
# 'common, exe, BOTS_SetRotation, -0x8, src/hook.s'

# '926, bigfilelangenlng, 0x0, 0x0, assets/NTSC-U.lng'

# '// USAUnlimitedPenta //'

# "// Inject compiled code for Penta's stats into the executable"
# '926, exe, 0x80088A0C, 0x0, ../../Patches/USAUnlimitedPenta/assets/stats.bin'

# '// Compile modified VehInit_SetConsts'
# '926, exe, VehInit_SetConsts, 0x0, ../../Patches/USAUnlimitedPenta/src/USAUnlimitedPenta.c'

# '// ExpandedFont //'

# '926, exe, DecalFont_DrawLineStrlen, 0x0, ../../Modules/ExpandedFont/src/addquotationmarks.c'
cases_sources = (
    ("../../Patches/JpnModchips/src/jpnModchips.s", 'jpnModchipss'),
    ("../../Patches/JpnModchips/src/jpnModchips.s", 'jpnModchipss'),
    ("../../Patches/EurLibcrypt/src/libcrypt.s", 'libcrypts'),
    ("src/main.c src/menubox.c", 'menuboxc'),
    ("src/*.c", '*c'),
    ("assets/title01_usa.tim", 'title01_usatim')
)
@pytest.mark.parametrize("string, expected", cases_sources)
def test_get_section_name_from_filepath(string, expected):
    prefix = "/mnt/c/dev/psx-modding-toolchain/games/CTR-ModSDK-main/mods/Standalones/StatsEditor/"
    path = pathlib.Path(prefix + string).resolve()
    assert compile_list.CompileList.get_section_name_from_filepath(path) == expected
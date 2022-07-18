from makefile import Makefile
from compile_list import CompileList, free_sections
from syms import Syms
from redux import Redux
from common import LOG_FILE, COMPILE_LIST, DEBUG_FOLDER, TEXTURES_FOLDER, TEXTURES_OUTPUT_FOLDER, request_user_input, cli_clear, cli_pause, check_compile_list, check_prerequisite_files, create_directory
from mkpsxiso import Mkpsxiso
from nops import Nops
from game_options import game_options
from image import create_images, clear_images, dump_images
from clut import clear_cluts, dump_cluts

import shutil
import os
import logging

redux = Redux()
mkpsxiso = Mkpsxiso()
nops = Nops()

def parse_compile_list(make: Makefile, sym: Syms):
    with open(COMPILE_LIST, "r") as file:
        for line in file:
            cl = CompileList(line, sym)
            if not cl.should_ignore():
                make.add_cl(cl)

def get_options() -> int:
    error_msg = "ERROR: Wrong option. Please type a number from 1-11.\n"
    print("Please select an action:")
    print()
    print("Mod:")
    print()
    print("1 - Compile")
    print("2 - Clean")
    print()
    print("Iso:")
    print()
    print("3 - Extract Iso")
    print("4 - Build Iso")
    print("5 - Clean Build")
    print()
    print("PCSX-Redux:")
    print()
    print("6 - Hot Reload Mod")
    print("7 - Restore Mod")
    print("8 - Replace Textures")
    print("9 - Restore Textures")
    print()
    print("NotPSXSerial:")
    print()
    print("10 - Hot Reload")
    print("11 - Restore")
    print()
    print("Misc:")
    print()
    print("12 - Disassemble Elf")
    print("13 - Clean All")
    print()
    return request_user_input(first_option=1, last_option=11, error_msg=error_msg)

def compile() -> None:
    if not check_compile_list():
        print("\n[Compile-py] ERROR: " + COMPILE_LIST + " not found.\n")
        return
    game_syms = Syms()
    make = Makefile(game_syms.get_build_id(), game_syms.get_files())
    parse_compile_list(make, game_syms)
    make.build_makefile()
    make.make()
    free_sections()

def clean() -> None:
    os.system("make clean")
    if os.path.isdir(TEXTURES_OUTPUT_FOLDER):
        shutil.rmtree(TEXTURES_OUTPUT_FOLDER)

def clean_all() -> None:
    mkpsxiso.clean(all=True)
    clean()

def replace_textures() -> None:
    create_directory(TEXTURES_OUTPUT_FOLDER)
    create_images(TEXTURES_FOLDER)
    dump_images(TEXTURES_OUTPUT_FOLDER)
    dump_cluts(TEXTURES_OUTPUT_FOLDER)
    redux.replace_textures()
    clear_images()
    clear_cluts()

def disasm() -> None:
    os.system("mipsel-none-elf-objdump -d " + DEBUG_FOLDER + "mod.elf >> " + DEBUG_FOLDER + "disasm.txt")
    print("\nDisassembly saved at " + DEBUG_FOLDER + "disasm.txt\n")

def main():
    while not check_prerequisite_files():
        cli_pause()
    game_options.load_config()
    redux.load_config()
    nops.load_config()
    actions = {
        1   :   compile,
        2   :   clean,
        3   :   mkpsxiso.extract_iso,
        4   :   mkpsxiso.build,
        5   :   mkpsxiso.clean,
        6   :   redux.hot_reload,
        7   :   redux.restore,
        8   :   replace_textures,
        9   :   redux.restore_textures,
        10  :   nops.hot_reload,
        11  :   nops.restore,
        12  :   disasm,
        13  :   clean_all,
    }
    while True:
        cli_clear()
        i = get_options()
        actions[i]()
        cli_pause()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.basicConfig(filename=LOG_FILE, filemode="w", format='%(levelname)s:%(message)s')
        logging.exception(e)
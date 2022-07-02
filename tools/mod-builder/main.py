from makefile import Makefile
from compile_list import CompileList, free_sections
from syms import Syms
from redux import Redux
from common import LOG_FILE, COMPILE_LIST, DEBUG_FOLDER, request_user_input, cli_clear, cli_pause, check_compile_list
from mkpsxiso import Mkpsxiso
from nops import Nops

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
    error_msg = "ERROR: Wrong option. Please type a number from 1-3.\n"
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
    print("6 - Hot Reload")
    print("7 - Restore")
    print()
    print("NotPSXSerial:")
    print()
    print("8 - Hot Reload")
    print("9 - Restore")
    print()
    print("Misc:")
    print()
    print("10 - Disassemble Elf")
    print("11 - Clean All")
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

def clean_all() -> None:
    mkpsxiso.clean(all=True)
    clean()

def disasm() -> None:
    os.system("mipsel-none-elf-objdump -d " + DEBUG_FOLDER + "mod.elf >> " + DEBUG_FOLDER + "disasm.txt")
    print("\nDisassembly saved at " + DEBUG_FOLDER + "disasm.txt\n")

def main():
    actions = {
        1   :   compile,
        2   :   clean,
        3   :   mkpsxiso.extract_iso,
        4   :   mkpsxiso.build,
        5   :   mkpsxiso.clean,
        6   :   redux.hot_reload,
        7   :   redux.restore,
        8   :   nops.hot_reload,
        9   :   nops.restore,
        10  :   disasm,
        11  :   clean_all,
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
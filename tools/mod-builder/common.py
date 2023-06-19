import copy
import os
import pathlib
import sys

remaining_args = copy.deepcopy(sys.argv[1:])
using_cl_args = len(sys.argv) > 1

def cli_pause() -> None:
    if using_cl_args:
        if len(remaining_args) == 0:
            sys.exit(0)
    else:
        print("Press Enter to continue...")
        input()

IS_WINDOWS_OS = sys.platform == "win32"
LOG_FILE = "crash.log"
CONFIG_FILE = "config.json"
CONFIG_PATH = _files.get_file_directory(fname = "config.json", folder = "games", max_iterations = 5)
logger.debug(f"FOLDER_DISTANCE: {CONFIG_PATH}")
logger.debug(f"CWD: {pathlib.Path.cwd()}")
DISTANCE_LENGTH = str(CONFIG_PATH).count("/") + 1
ISO_PATH = CONFIG_PATH / "build"
SYMS_PATH = CONFIG_PATH / "symbols"
PLUGIN_PATH = CONFIG_PATH / "plugins"
GAME_INCLUDE_PATH = CONFIG_PATH / "include"
MOD_PATH = CONFIG_PATH / "mods"
MAKEFILE = "Makefile"
COMPILE_LIST = "buildList.txt"
SRC_FOLDER = "src/"
OUTPUT_FOLDER = "output/"
BACKUP_FOLDER = "backup/"
DEBUG_FOLDER = "debug/"
OBJ_FOLDER = DEBUG_FOLDER + "obj/"
DEP_FOLDER = DEBUG_FOLDER + "dep/"
COMP_SOURCE = DEBUG_FOLDER + "source.txt"
TEXTURES_FOLDER = "newtex/"
TEXTURES_OUTPUT_FOLDER = TEXTURES_FOLDER + "output/"
GCC_MAP_FILE = DEBUG_FOLDER + "mod.map"
GCC_OUT_FILE = DEBUG_FOLDER + "gcc_out.txt"
TRIMBIN_OFFSET = DEBUG_FOLDER + "offset.txt"
COMPILATION_RESIDUES = ["overlay.ld", MAKEFILE, "comport.txt"]
REDUX_MAP_FILE = DEBUG_FOLDER + "redux.map"
CONFIG_PATH = CONFIG_PATH / CONFIG_FILE
SETTINGS_FILE = "settings.json"
SETTINGS_PATH = CONFIG_PATH.parent / SETTINGS_FILE
RECURSIVE_COMP_FILE = ".recursive"
RECURSIVE_COMP_PATH = CONFIG_PATH / RECURSIVE_COMP_FILE
ABORT_FILE = ".abort"
ABORT_PATH = CONFIG_PATH / ABORT_FILE
DISC_FILE = "disc.json"
DISC_PATH = CONFIG_PATH / DISC_FILE
TOOLS_PATH = CONFIG_PATH.parents[1] / "tools"
PSYQ_CONVERTED_PATH = TOOLS_PATH / "gcc-psyq-converted" / "lib"
PSYQ_RENAME_CONFIRM_FILE = PSYQ_CONVERTED_PATH / ".sections-renamed"
COMMENT_SYMBOL = "//"
MOD_NAME = pathlib.Path.cwd().name # TODO: Pass this as an arg 
GAME_NAME = pathlib.Path.cwd().parents[DISTANCE_LENGTH].name # not sure, number of folders?
logger.debug(f"GAME_NAME: {GAME_NAME}")
HEXDIGITS = ["A", "B", "C", "D", "E", "F"]

def rename_psyq_sections() -> None:
    sections = ["text", "data", "bss", "rdata", "sdata", "sbss", "note"]
    prefix = "mipsel-none-elf-"
    command = prefix + "objcopy"
    for section in sections:
        command += " --rename-section ." + section + "=.psyq" + section
    print("\n[Common-py] Renaming PSYQ sections...")
    curr_directory = ""
    for root, _, files in os.walk(PSYQ_CONVERTED_PATH):
        for filename in files:
            split_filename = filename.rsplit(".", 1)
            if len(split_filename) != 2:
                continue
            extension = split_filename[1]
            if extension == "a" or extension == "o":
                if root[-1] != "/":
                    root = root + "/"
                directory = root.split("/")[-2]
                if directory != curr_directory:
                    curr_directory = directory
                    print("[Common-py] Converting " + directory + "/ directory...")
                filepath = root + filename
                os.system(command + " " + filepath)
    with open(PSYQ_RENAME_CONFIRM_FILE, "w"):
        pass
    print("[Common-py] PSYQ sections renamed successfully.\n")

def request_user_input(first_option: int, last_option: int, intro_msg: str, error_msg: str) -> int:
    if using_cl_args and len(remaining_args) == 0:
        raise Exception("ERROR: Not enough arguments to complete command.")

    if not using_cl_args:
        print(intro_msg)

    raise_exception = False
    i = 0
    while True:
        try:
            i = int(input()) if not using_cl_args else int(remaining_args.pop(0))
            if (i < first_option) or (i > last_option):
                if using_cl_args:
                    raise_exception = True
                    break
                else:
                    print(error_msg)
            else:
                break
        except:
            if using_cl_args:
                raise_exception = True
                break
            else:
                print(error_msg)

    if raise_exception:
        raise Exception(error_msg)

    return i

def get_build_id() -> int:
    if not os.path.isfile(MAKEFILE):
        return None
    with open(MAKEFILE, "r") as file:
        for line in file:
            line = line.split()
            if len(line) and line[0] == "CPPFLAGS":
                build_var = line[-1]
                build_id = int(build_var.split("=")[-1].strip())
                return build_id

def is_number(s: str) -> bool:
    is_hex = False
    if len(s) > 1 and s[0] == "-":
        s = s[1:]
    if len(s) > 2 and s[:2] == "0x":
        s = s[2:]
        is_hex = True
    if len(s) == 0:
        return False
    for char in s:
        if not ((char.isdigit()) or (is_hex and char.upper() in HEXDIGITS)):
            return False
    return True

def cli_clear() -> None:
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def check_compile_list() -> bool:
    if os.path.isfile(COMPILE_LIST):
        return True
    return False
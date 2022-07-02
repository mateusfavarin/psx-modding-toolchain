import os

LOG_FILE = "crash.log"
ISO_PATH = "../../build/"
COMPILE_LIST = "buildList.txt"
SYMS_PATH = "../../symbols/"
OUTPUT_FOLDER = "output/"
BACKUP_FOLDER = "backup/"
DEBUG_FOLDER = "debug/"
GCC_MAP_FILE = DEBUG_FOLDER + "mod.map"
REDUX_MAP_FILE = DEBUG_FOLDER + "redux.map"
CONFIG_PATH = "../../config.json"
SETTINGS_PATH = "../../../settings.json"
DISC_PATH = "../../disc.json"
COMMENT_SYMBOL = "//"
MOD_NAME = os.getcwd().replace("\\", "/").split("/")[-1]
HEXDIGITS = ["A", "B", "C", "D", "E", "F"]

def create_directory(dirname: str) -> None:
    if not os.path.isdir(dirname):
        os.mkdir(dirname)

def request_user_input(first_option: int, last_option: int, error_msg: str) -> int:
    i = 0
    while True:
        try:
            i = int(input())
            if (i < first_option) or (i > last_option):
                print(error_msg)
            else:
                break
        except:
            print(error_msg)
    return i

def get_build_id() -> int:
    if not os.path.isfile("Makefile"):
        return None
    with open("Makefile", "r") as file:
        for line in file:
            line = line.split()
            if len(line) and line[0] == "CPPFLAGS":
                build_var = line[-1]
                build_id = int(build_var.split("=")[-1].strip())
                return build_id

def is_number(s: str) -> bool:
    if len(s) > 1 and s[0] == "-":
        s = s[1:]
    if len(s) > 2 and s[:2] == "0x":
        s = s[2:]
    for char in s:
        if not ((char.isdigit()) or (char.upper() in HEXDIGITS)):
            return False
    return True

def cli_clear() -> None:
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def cli_pause() -> None:
    print("Press any key to continue...")
    input()

def check_compile_list() -> bool:
    if os.path.isfile(COMPILE_LIST):
        return True
    return False
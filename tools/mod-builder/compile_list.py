"""
Parses the buildList.txt file line by line assuming a tabluar format 
"""
import _files # check_file
from common import COMMENT_SYMBOL, CONFIG_PATH, OUTPUT_FOLDER, MOD_PATH, is_number
from syms import Syms

import json
import logging
import re
import os
import pathlib

logger = logging.getLogger(__name__)

sections = dict()
line_count = [0]
print_errors = [False]

def error_print(error: str):
    """
    TODO: Find out what print_errors is for
    """
    logger.error(error)
    print_errors[0] = True

class CompileList:
    def __init__(self, line: str, sym: Syms, prefix: str) -> None:
        self.original_line = line
        self.sym = sym
        self.prefix = prefix
        self.ignore = False
        self.is_bin = False
        self.cl = False
        self.path_build_list = None
        self.pch = str()
        self.min_addr = 0x80000000
        self.max_addr = 0x807FFFFF if self.is_8mb() else 0x801FFFFF
        self.parse_line(line)
        line_count[0] += 1

    def is_8mb(self) -> bool:
        with open(CONFIG_PATH, "r") as file:
            data = json.load(file)["compiler"]
            return data["8mb"] == 1

    def parse_line(self, string) -> None:
        """
        TODO: This does much more than just parse a line
        """
        string_p = string.replace(COMMENT_SYMBOL, f",{COMMENT_SYMBOL},")
        list_tokens = [l.strip() for l in string_p.split(",") if l.strip() != ""]
        # BUG: Prone to bugs as it's modifying the list as we iterate through it
        for index, token in enumerate(list_tokens):
            if token == COMMENT_SYMBOL:
                if index == 0:
                    list_tokens = []
                else:
                    list_tokens = list_tokens[:index]
                break
        if len(list_tokens) < 5:
            if len(list_tokens) == 2 and list_tokens[0] == "add":
                list_tokens[1] = list_tokens[1].replace("\\", "/")
                if list_tokens[1][-1] != "/":
                    list_tokens[1] += "/"
                self.path_build_list = MOD_PATH / list_tokens[1]
                if _files.check_file(self.path_build_list):
                    self.cl = True
                else:
                    error_print(f"Mod directory not found at line {line_count[0]}: {self.path_build_list}\n")
            if (not self.cl) and (len(list_tokens) > 0):
                error_print(f"Wrong syntax at line {line_count[0]}: {self.original_line}\n")
            self.ignore = True
            return

        version = list_tokens[0]
        if is_number(version):
            version = int(version, 0)
            if version != self.sym.get_build_id():
                self.ignore = True
                return
        else:
            if (version.lower() != "common") and (version != self.sym.get_version()):
                self.ignore = True
                return

        self.game_file = list_tokens[1]
        offset = 0
        try:
            offset = eval(list_tokens[3])
        except Exception:
            error_print("Invalid arithmetic expression for offset at line {line_count[0]}: {self.original_line}\n")

        self.address = self.calculate_address_base(list_tokens[2], offset)
        srcs = [l.strip() for l in list_tokens[4].split()]
        self.source = list()
        folders = dict()
        for src in srcs:
            # TODO: Replace with pathlib
            src = (self.prefix + src).replace("\\", "/").rsplit("/", 1)
            directory = src[0] + "/"
            regex = re.compile(src[1].replace("*", "(.*)"))
            output_name = src[1].split(".")[0]
            if not directory in folders:
                for _, _, files in os.walk(directory):
                    folders[directory] = files
                    break
            if directory.rsplit("/", 1)[-1] == str(OUTPUT_FOLDER) and output_name in sections:
                self.source.append(directory + src[1])
            else:
                if directory in folders:
                    for file in folders[directory]:
                        if regex.search(file):
                            self.source.append(directory + file)
                else:
                    error_print("\n[BuildList-py] WARNING: directory " + directory + " not found.")
                    error_print(f"at line: {line_count[0]}: {self.original_line}\n")
                    self.ignore = True
                    return

        if len(self.source) == 0:
            error_print(f"\n[BuildList-py] WARNING: no file(s) found at line: {line_count[0]}: {self.original_line}\n")
            self.ignore = True
            return
        if len(list_tokens) == 6:
            self.section_name = list_tokens[5].split(".")[0]
        else:
            self.section_name = self.get_section_name_from_filepath(self.source[0])

        extension = self.source[0].rsplit(".", 1)[1]
        if not (extension.lower() in ["c", "s", "cpp", "cc"]):
            self.is_bin = True
            self.ignore = True
            return

        if (self.address != 0) and ((self.address < self.min_addr) or (self.address > self.max_addr)):
            if self.address != -1:
                error_print(f"address specified is not in the [{hex(self.min_addr)}, {hex(self.max_addr)}] range.")
                error_print(f"at line {line_count[0]}: {self.original_line}\n")
            self.ignore = True
            return

        if self.section_name in sections:
            self.ignore = True
            error_print("Binary filename already in use, please define another alias.")
            error_print(f"at line {line_count[0]}: {self.original_line}\n")
            return
        else:
            sections[self.section_name] = True

    def get_section_name_from_filepath(self, filepath: str) -> str:
        """ TODO: Get an example """
        return filepath.rsplit("/", 1)[-1].replace(".", "").replace("-", "_")

    def calculate_address_base(self, symbol: str, offset: int) -> int:
        addr = self.sym.get_address(symbol)
        if addr is not None:
            return addr + offset
        if is_number(symbol):
            return int(symbol, 0) + offset
        error_print(f"Undefined symbol: {symbol} at line: {line_count[0]}: {self.original_line}\n")
        return -1

    def get_output_name(self) -> str:
        if self.is_bin:
            return self.source[0]
        return pathlib.Path(self.prefix) / OUTPUT_FOLDER / (self.section_name + ".bin")

    def should_ignore(self) -> bool:
        return self.ignore

    def should_build(self) -> bool:
        if self.ignore and not self.is_bin:
            return False
        return True

    def is_cl(self) -> bool:
        return self.cl

def free_sections() -> None:
    sections.clear()
    line_count[0] = 0
    print_errors[0] = False

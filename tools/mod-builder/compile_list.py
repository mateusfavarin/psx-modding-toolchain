"""
Parses the buildList.txt file line by line assuming a tabluar format 
Use pathlib.Path().resolve() to handle concatenation of ../.. syntax
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
        self.prefix = prefix # path prefix
        self.ignore = False
        self.is_bin = False
        self.cl = False
        self.path_build_list = None
        self.source = None
        self.pch = str()
        self.min_addr = 0x80000000
        self.max_addr = 0x807FFFFF if self.is_8mb() else 0x801FFFFF
        self.parse_line(line)
        line_count[0] += 1

    def is_8mb(self) -> bool:
        with open(CONFIG_PATH, "r") as file:
            data = json.load(file)["compiler"]
            return data["8mb"] == 1

    @staticmethod
    def tokenize_line(string, delimiter = ","):
        """ Strip and delimit """
        list_out = [l.strip() for l in string.split(delimiter) if l.strip() != ""]
        return list_out

    @staticmethod
    def skip_comments(list_tokens, string_comment = COMMENT_SYMBOL):
        """
        Lines that start with comments go to empty
        Lines that end with comments get truncated
        """
        list_out = list_tokens[::] # copy
        for index, token in enumerate(list_tokens):
            if token.lower() == string_comment.lower():
                if index == 0:
                    list_out = []
                else: # comment is after the first
                    list_out = list_tokens[:index] # truncate line
                break
        return list_out

    def parse_line(self, string) -> None:
        """
        TODO: This does much more than just parse a line
        """
        string_p = string.replace(COMMENT_SYMBOL, f",{COMMENT_SYMBOL},")
        list_tokens = self.tokenize_line(string_p)
        list_tokens = self.skip_comments(list_tokens)
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
            error_print(f"Invalid arithmetic expression for offset at line {line_count[0]}: {self.original_line}\n")

        self.address = self.calculate_address_base(list_tokens[2], offset)
        # construct source_directories
        srcs = [l.strip() for l in list_tokens[4].split()]
        self.source = []
        dict_folders = dict()
        for src in srcs:
            src_path = pathlib.Path(self.prefix + src).resolve()
            directory = src_path.parent
            regex = re.compile(src_path.name.replace("*", "(.*)"))
            output_name = src_path.stem
            if not directory in dict_folders:
                for _, _, files in os.walk(directory):
                    dict_folders[directory] = files
                    break
            # TODO: Figure out why we need this weird if-block
            # TODO: Workaround until OUTPUT_FOLDER is a pathlib object
            if (directory.name + os.sep == OUTPUT_FOLDER) and output_name in sections:
                self.source.append(directory / src_path.name)
            else:
                if directory in dict_folders:
                    for file in dict_folders[directory]:
                        if regex.search(file):
                            self.source.append(directory / file)
                else:
                    logger.warning(f"directory {directory} not found at line: {line_count[0]}: {self.original_line}")
                    self.ignore = True
                    return

        if len(self.source) == 0:
            error_print(f"No file(s) found at line: {line_count[0]}: {self.original_line}")
            self.ignore = True
            return
        if len(list_tokens) == 6:
            self.section_name = list_tokens[5].split(".")[0]
        else:
            self.section_name = self.get_section_name_from_filepath(self.source[0])

        extension = self.source[0].suffix
        if extension.lower() not in [".c", ".s", ".cpp", ".cc"]:
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

    @staticmethod
    def get_section_name_from_filepath(filepath):
        """ 
        Removes dots in the extension and replaces hypens with underscores
        TODO: This function name is unintuitive
        """
        return filepath.name.replace(".", "").replace("-", "_")

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
        return pathlib.Path(self.prefix + OUTPUT_FOLDER).resolve() / (self.section_name + ".bin")

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

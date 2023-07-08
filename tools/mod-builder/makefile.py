from __future__ import annotations # to use type in python 3.7

"""
Constructs the makefile
TODO: Use subprocess instead of os.system
"""

from compile_list import CompileList
import _files # create_directory, delete_file
from common import request_user_input, rename_psyq_sections, cli_clear, MAKEFILE, TRIMBIN_OFFSET, GCC_OUT_FILE, COMP_SOURCE, GAME_INCLUDE_PATH, CONFIG_PATH, SRC_FOLDER, DEBUG_FOLDER, OUTPUT_FOLDER, BACKUP_FOLDER, OBJ_FOLDER, DEP_FOLDER, GCC_MAP_FILE, REDUX_MAP_FILE, CONFIG_PATH, PSYQ_RENAME_CONFIRM_FILE, MOD_NAME

import logging
import json
import re
import os
import shutil
import subprocess
import textwrap
from time import time

# import pdb # debugging

logger = logging.getLogger(__name__)

def clean_pch() -> None:
    with open(CONFIG_PATH, "r") as file:
        data = json.load(file)["compiler"]
        if "pch" in data:
            pch = data["pch"] + ".gch"
            _files.delete_file(GAME_INCLUDE_PATH / pch)

class Makefile:
    def __init__(self, build_id: int, files_symbols: list[str]) -> None:
        self.build_id = build_id
        self.files_symbols = files_symbols
        self.list_compile_lists = []
        self.pch = str()
        self.opt_ccflags = str()
        self.opt_ldflags = str()
        self.srcs = None # list
        self.load_config()

    def load_config(self) -> None:
        with open(CONFIG_PATH, "r") as file:
            data = json.load(file)["compiler"]
            self.use_function_sections = str(data["function_sections"] == 1).lower()
            self.disable_function_reorder = str(data["reorder_functions"] == 0).lower()
            optimization_level = data["optimization"]
            if optimization_level > 3:
                self.compiler_flags = "-Os"
            else:
                self.compiler_flags = "-O" + str(optimization_level)
            if data["debug"] != 0:
                self.compiler_flags += " -g"
            self.use_psyq_str = str(data["psyq"] != 0).lower()
            self.use_psyq = data["psyq"] != 0
            if "pch" in data:
                self.pch = data["pch"] + ".gch"
            if "ccflags" in data:
                self.opt_ccflags = data["ccflags"]
            if "ldflags" in data:
                self.opt_ldflags = data["ldflags"]

    def add_cl(self, instance: CompileList) -> None:
        self.list_compile_lists.append(instance)

    def set_base_address(self) -> bool:
        address = 0x807FFFFF
        for instance in self.list_compile_lists:
            address = min(address, instance.address)
        self.base_addr = address
        return True

    def build_makefile_objects(self) -> None:
        self.srcs = []
        self.ovr_section = []
        self.ovrs = []
        for instance in self.list_compile_lists:
            for src in instance.source: #pathlibs
                self.srcs.append(src)
            self.ovrs.append((instance.section_name, instance.source, instance.address))
            # self.ovr_section += "." + instance.section_name + " "
            self.ovr_section.append("." + instance.section_name)

    def build_linker_script(self, filename="overlay.ld") -> str:
        offset_buffer = str()
        add_psyq = True
        buffer =  "__heap_base = __ovr_end;\n"
        buffer += "\n"
        buffer += "__ovr_start = " + hex(self.base_addr) + ";\n"
        buffer += "\n"
        buffer += "SECTIONS {\n"
        buffer += " " * 4 + "OVERLAY __ovr_start : SUBALIGN(4) {\n"
        for ovr in self.ovrs:
            section_name = ovr[0]
            source = ovr[1] # list of pathlib
            addr = ovr[2]
            offset = addr - self.base_addr
            offset_buffer += section_name + " " + hex(offset) + "\n"
            buffer += " " * 8 + "." + section_name + " {\n"
            if addr > self.base_addr:
                buffer += " " * 12 + ". = . + " + hex(offset) + ";\n"
            text, rodata, sdata, data, sbss, bss, ctors, psyq = [], [], [], [], [], [], [], []
            sections = [text, rodata, sdata, data, sbss, bss, ctors, psyq]
            for src in source: # pathlib objects
                # TODO: Utilize pathlib completely
                src_o = src.with_suffix(".o") # remove suffix
                is_c = False
                if src.suffix == ".c":
                    is_c = True                    
                text.append(" " * 12 + f"KEEP({str(src_o)}(.text*))\n")
                rodata.append(" " * 12 + f"KEEP({str(src_o)}(.rodata*))\n")
                sdata.append(" " * 12 + f"KEEP({str(src_o)}(.sdata*))\n")
                data.append(" " * 12 + f"KEEP({str(src_o)}(.data*))\n")
                sbss.append(" " * 12 + f"KEEP({str(src_o)}(.sbss*))\n")
                bss.append(" " * 12 + f"KEEP({str(src_o)}(.bss*))\n")
                if add_psyq and self.use_psyq and is_c:
                    add_psyq = False
                    psyq.append(" " * 12 + "KEEP(*(.psyqtext*))\n")
                    psyq.append(" " * 12 + "KEEP(*(.psyqrdata*))\n")
                    psyq.append(" " * 12 + "KEEP(*(.psyqsdata*))\n")
                    psyq.append(" " * 12 + "KEEP(*(.psyqdata*))\n")
                    psyq.append(" " * 12 + "KEEP(*(.psyqsbss*))\n")
                    psyq.append(" " * 12 + "KEEP(*(.psyqbss*))\n")
            for section in sections:
                for line in section:
                    buffer += line
            buffer += " " * 12 + ". = ALIGN(4);\n"
            buffer += " " * 12 + "__ovr_end = .;\n"
            buffer += " " * 8 + "}" + "\n"
        buffer += " " * 4 + "}" + "\n"
        buffer += "}" + "\n"

        with open(filename, "w") as file:
            file.write(buffer)

        _files.create_directory(DEBUG_FOLDER)
        with open(TRIMBIN_OFFSET, "w") as file:
            file.write(offset_buffer)

        return filename

    def build_makefile(self) -> bool:
        if self.use_psyq and not _files.check_file(PSYQ_RENAME_CONFIRM_FILE):
            print("\n[Makefile-py] WARNING: your project configuration may be trying to import PSYQ functions,")
            print("but you haven't renamed your psyq sections.")
            min_option = 1
            max_option = 2
            intro_msg = "Would you like to convert them now?\n1 - Yes\n2 - No"
            error_msg = "ERROR: Please select a number between " + str(min_option) + " and " + str(max_option)
            if request_user_input(min_option, max_option, intro_msg=intro_msg, error_msg=error_msg) == 1:
                rename_psyq_sections()
            else:
                intro_msg = "Would you like to abort the compilation?\n1 - Yes\n2 - No"
                if request_user_input(min_option, max_option, intro_msg=intro_msg, error_msg=error_msg) == 1:
                    return False

        self.set_base_address()
        self.build_makefile_objects()
        buffer = f"""
        MODDIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
        TARGET = mod

        SRCS = {" ".join([str(i) for i in self.srcs])}
        CPPFLAGS = -DBUILD={self.build_id}
        LDSYMS = {" ".join(f"-T{str(sym)}" for sym in self.files_symbols)}

        USE_FUNCTION_SECTIONS ?= {self.use_function_sections}
        DISABLE_FUNCTION_REORDER ?= {self.disable_function_reorder}
        USE_PSYQ ?= {self.use_psyq_str}
        OVERLAYSECTION ?= {" ".join(self.ovr_section)} triple
        OVR_START_ADDR = {hex(self.base_addr)}
        OVERLAYSCRIPT = {self.build_linker_script()}
        BUILDDIR = $(MODDIR){OUTPUT_FOLDER}
        SRCINCLUDEDIR = $(MODDIR){SRC_FOLDER}
        GAMEINCLUDEDIR = {str(GAME_INCLUDE_PATH)}
        EXTRA_CC_FLAGS = {self.compiler_flags}
        OPT_CC_FLAGS = {self.opt_ccflags}
        OPT_LD_FLAGS = {self.opt_ldflags}
        PCHS = {str(GAME_INCLUDE_PATH/self.pch)}
        TRIMBIN_OFFSET = $(MODDIR){str(TRIMBIN_OFFSET)}

        include {str(CONFIG_PATH.parents[1] / 'common.mk')}
        """

        with open(MAKEFILE, "w") as file:
            file.write(textwrap.dedent(buffer)) # removes indentation

        return True

    def delete_temp_files(self) -> None:
        for ovr in self.ovrs:
            for src in ovr[1]: # list of pathlibs
                _files.delete_file(src.with_suffix(".o"))
                _files.delete_file(src.with_suffix(".dep"))

    # Moving the .o and .dep to debug/
    def move_temp_files(self) -> None:
        buffer = str()
        for ovr in self.ovrs:
            for src in ovr[1]:
                obj_path = src.with_suffix(".o")
                dep_path = src.with_suffix(".dep")
                if _files.check_file(obj_path) and _files.check_file(dep_path):
                    obj_dst = OBJ_FOLDER / obj_path.name
                    dep_dst = DEP_FOLDER / dep_path.name
                    buffer += f"{obj_dst} {obj_path}\n"
                    buffer += f"{dep_dst} {dep_path}\n"
                    shutil.move(obj_path, obj_dst)
                    shutil.move(dep_path, dep_dst)
        with open(COMP_SOURCE, "w") as file:
            file.write(buffer)

    # Restoring the saved .o and .dep for faster compilation
    def restore_temp_files(self) -> None:
        if _files.check_file(COMP_SOURCE):
            with open(COMP_SOURCE, "r") as file:
                for line in file:
                    line = [l.strip() for l in line.split()]
                    shutil.move(line[0], line[1])

    def make(self) -> bool:
        """
        TODO: Creating all of these directories right now instead of upfront is bad design
        TODO: Keep track of all files incase this fails to clean up after ourselves
        """
        _files.create_directory(OUTPUT_FOLDER)
        _files.create_directory(BACKUP_FOLDER)
        _files.create_directory(OBJ_FOLDER)
        _files.create_directory(DEP_FOLDER)
        self.restore_temp_files()
        cli_clear()
        print("\n[Makefile-py] Compiling " + MOD_NAME + "...\n")
        start_time = time()
        try:
            command = ["make", "--silent"] # TODO: Point to the CWD directory 
            with open(GCC_OUT_FILE, "w") as outfile:
                result = subprocess.run(command, stdout=outfile, stderr=subprocess.STDOUT)
                if result.returncode != 0:
                    logger.critical(f"Compilation failed. See {GCC_OUT_FILE}")
                    return False
        except subprocess.CalledProcessError as error:
            logger.exception(error, exc_info = False)
            logger.critical(f"Compilation failed. See {GCC_OUT_FILE}")
            return False
        end_time = time()
        total_time = str(round(end_time - start_time, 3))
        with open(GCC_OUT_FILE, "r") as file:
            for line in file:
                print(line)

        # These are relaive to the current Makefile
        if (not os.path.isfile("mod.map")) or (not os.path.isfile("mod.elf")):
            self.move_temp_files()
            self.delete_temp_files()
            logger.critical(f"Compilation completed but unsuccessful. ({total_time}s)")
            return False

        shutil.move("mod.map", DEBUG_FOLDER / "mod.map")
        shutil.move("mod.elf", DEBUG_FOLDER / "mod.elf")
        self.move_temp_files()

        logger.info(f"Compilation successful ({total_time}s)")
        pattern = re.compile(r"0x0000000080[0-7][0-9a-fA-F]{5}\s+([a-zA-Z]|_)\w*")
        special_symbols = ["__heap_base", "__ovr_start", "__ovr_end", "OVR_START_ADDR"]
        buffer = ""
        with open(GCC_MAP_FILE, "r") as file:
            for line in file:
                for match in re.finditer(pattern, line):
                    res = match.group().split()
                    if res[1] in special_symbols:
                        continue
                    buffer += res[0][10:] + " " + res[1] + "\n"

        with open(REDUX_MAP_FILE, "w") as file:
            file.write(buffer)
        return True
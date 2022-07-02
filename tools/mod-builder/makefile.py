from compile_list import CompileList
from common import create_directory, DEBUG_FOLDER, OUTPUT_FOLDER, BACKUP_FOLDER, GCC_MAP_FILE, REDUX_MAP_FILE, CONFIG_PATH

import re
import json
import os

class Makefile:
    def __init__(self, build_id: int, sym_file: list[str]) -> None:
        self.build_id = build_id
        self.sym_file = sym_file
        self.cl = list()
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
            self.use_psyq = str(data["psyq"] == 1).lower()

    def add_cl(self, cl: CompileList) -> None:
        self.cl.append(cl)

    def set_base_address(self) -> bool:
        address = 0x807FFFFF
        for cl in self.cl:
            address = min(address, cl.address)
        self.base_addr = address
        return True

    def build_makefile_objects(self) -> None:
        self.srcs = str()
        self.ovr_section = str()
        self.ovrs = list()
        for cl in self.cl:
            for src in cl.source:
                self.srcs += src + " "
            self.ovrs.append((cl.section_name, cl.source, cl.address))
            self.ovr_section += "." + cl.section_name + " "

    def build_linker_script(self, filename="overlay.ld") -> str:
        offset_buffer = str()
        buffer = "__heap_base = __ovr_end;\n"
        buffer += "\n"
        buffer += "__ovr_start = " + hex(self.base_addr) + ";\n"
        buffer += "\n"
        buffer += "SECTIONS {\n"
        buffer += " " * 4 + "OVERLAY __ovr_start : SUBALIGN(4)\n"
        buffer += " " * 4 + "{\n"
        for ovr in self.ovrs:
            section_name = ovr[0]
            source = ovr[1]
            addr = ovr[2]
            offset = addr - self.base_addr
            offset_buffer += section_name + " " + hex(offset) + "\n"
            buffer += " " * 8 + "." + section_name + "\n"
            buffer += " " * 8 + "{" + "\n"
            if addr > self.base_addr:
                buffer += " " * 12 + ". = . + " + hex(offset) + ";\n"
            for src in source:
                src = src[:-2]
                buffer += " " * 12 + "KEEP(" + src + ".o(.text))\n"
                buffer += " " * 12 + "KEEP(" + src + ".o(.text.startup._GLOBAL__*))\n"
                buffer += " " * 12 + "KEEP(" + src + ".o(.text.*))\n"
                buffer += " " * 12 + "KEEP(" + src + ".o(.rodata*))\n"
                buffer += " " * 12 + "KEEP(" + src + ".o(.sdata*))\n"
                buffer += " " * 12 + "KEEP(" + src + ".o(.data*))\n"
                buffer += " " * 12 + "KEEP(" + src + ".o(.sbss*))\n"
                buffer += " " * 12 + "KEEP(" + src + ".o(.bss*))\n"
                buffer += " " * 12 + "KEEP(" + src + ".o(.ctors))\n"
            buffer += " " * 12 + "\n"
            buffer += " " * 12 + ". = ALIGN(4);\n"
            buffer += " " * 12 + "__ovr_end = .;\n"
            buffer += " " * 8 + "}" + "\n"
        buffer += " " * 4 + "}" + "\n"
        buffer += "}" + "\n"

        with open(filename, "w") as file:
            file.write(buffer)

        with open("offset.txt", "w") as file:
            file.write(offset_buffer)

        return filename

    def build_makefile(self) -> None:
        self.set_base_address()
        self.build_makefile_objects()
        buffer = "MODDIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))\n"
        buffer += "TARGET = mod\n"
        buffer += "\n"
        buffer += "SRCS = " + self.srcs + "\n"
        buffer += "CPPFLAGS = -DBUILD=" + str(self.build_id) + "\n"
        buffer += "LDSYMS = "
        for sym in self.sym_file:
            buffer += "-T$(MODDIR)" + sym + " "
        buffer += "\n"
        buffer += "USE_FUNCTION_SECTIONS ?= " + self.use_function_sections + "\n"
        buffer += "DISABLE_FUNCTION_REORDER ?= " + self.disable_function_reorder + "\n"
        buffer += "USE_PSYQ ?= " + self.use_psyq + "\n"
        buffer += "OVERLAYSECTION ?= " + self.ovr_section + "\n"
        buffer += "OVR_START_ADDR = " + hex(self.base_addr) + "\n"
        buffer += "OVERLAYSCRIPT = " + self.build_linker_script() + "\n"
        buffer += "BUILDDIR = $(MODDIR)" + OUTPUT_FOLDER + "\n"
        buffer += "DEBUGDIR = $(MODDIR)" + DEBUG_FOLDER + "\n"
        buffer += "BACKUPDIR = $(MODDIR)" + BACKUP_FOLDER + "\n"
        buffer += "EXTRA_CC_FLAGS = " + self.compiler_flags + "\n"
        buffer += "\n"
        buffer += "include ../../../common.mk\n"

        with open("Makefile", "w") as file:
            file.write(buffer)

    def make(self) -> None:
        create_directory(OUTPUT_FOLDER)
        create_directory(BACKUP_FOLDER)
        create_directory(DEBUG_FOLDER)
        os.system("make -s -j8")
        os.system("move mod.map " + DEBUG_FOLDER)
        os.system("move mod.elf " + DEBUG_FOLDER)

        if not os.path.isfile(GCC_MAP_FILE):
            print("\n[Makefile-py] ERROR: compilation was not successful.\n")
            return

        print("\n[Makefile-py] Successful compilation.\n")
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
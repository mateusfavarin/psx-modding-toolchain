"""
TODO: Replace with Click
"""

import _files # check_file, delete_file, create_directory, delete_directory
from common import ISO_PATH, MOD_NAME, OUTPUT_FOLDER, COMPILE_LIST, PLUGIN_PATH, TOOLS_PATH, request_user_input, cli_pause, get_build_id
from game_options import game_options
from disc import Disc
from compile_list import CompileList, free_sections
from syms import Syms

import importlib
import logging
import os
import pathlib
import pyxdelta
import pymkpsxiso
import shutil
import sys
import xml.etree.ElementTree as et
logger = logging.getLogger(__name__)

MB = 1024 * 1024

def _copyfileobj_patched(fsrc, fdst, length=64*MB):
    """Patches shutil method to hugely improve copy speed"""
    while True:
        buf = fsrc.read(length)
        if not buf:
            break
        fdst.write(buf)

shutil.copyfileobj = _copyfileobj_patched # overwrites a class method directly (dangerous)

class Mkpsxiso:
    def __init__(self) -> None:
        path = (PLUGIN_PATH / "plugin.py").resolve() # absolute
        spec = importlib.util.spec_from_file_location("plugin", path)
        self.plugin = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.plugin)
        self.python_path = pathlib.Path.cwd()

    def find_iso(self, gv) -> bool:
        if not _files.check_file(ISO_PATH / gv.rom_name):
            print(f"Please insert your {gv.version} game in {ISO_PATH} and rename it to {gv.rom_name}")
            return False
        return True

    def ask_user_for_version(self):
        names = game_options.get_version_names()
        intro_msg = "Select the game version:\n"
        for i, name in enumerate(names):
            intro_msg += f"{i + 1} - {name}\n"
        error_msg = f"ERROR: Invalid version. Please select a number from 1-{len(names)}."
        version = request_user_input(first_option=1, last_option=len(names), intro_msg=intro_msg, error_msg=error_msg)
        return game_options.get_gv_by_name(names[version - 1])

    def extract(self, gv, extract_folder: str, xml: str) -> None:
        has_iso = self.find_iso(gv)
        while not has_iso:
            cli_pause()
            has_iso = self.find_iso(gv)
        rom_path = ISO_PATH + gv.rom_name
        _files.create_directory(extract_folder)
        pymkpsxiso.dump(rom_path, extract_folder, xml)
        self.plugin.extract(self.python_path / PLUGIN_PATH, self.python_path / (extract_folder + "/"))

    def abort_build_request(self) -> bool:
        """ TODO: Replace with click """
        intro_msg = (
            "Abort iso build?\n"
            "1 - Yes\n"
            "2 - No\n"
        )
        error_msg = "Invalid input. Please type a number from 1-2."
        return request_user_input(first_option=1, last_option=2, intro_msg=intro_msg, error_msg=error_msg) == 1

    def patch_iso(self, version: str, build_id: int, build_files_folder: str, modified_rom_name: str, xml: str) -> bool:
        disc = Disc(version)
        sym = Syms(build_id)
        modded_files = dict()
        iso_changed = False
        build_files_folder += "/"
        xml_tree = et.parse(xml)
        dir_tree = xml_tree.findall(".//directory_tree")[0]
        build_lists = ["./"]
        while build_lists:
            prefix = build_lists.pop(0)
            bl = pathlib.Path(prefix) / COMPILE_LIST # TODO: Double check
            free_sections()
            with open(bl, "r") as file:
                for line in file:
                    cl = CompileList(line, sym, prefix)
                    if cl.is_cl():
                        build_lists.append(cl.bl_path)
                    if not cl.should_build():
                        continue

                    # if it's a file to be overwritten in the game
                    df = disc.get_df(cl.game_file)
                    if df is not None:
                        # checking file start boundaries
                        if cl.address < df.address:
                            error_msg = (
                                f"\n[ISO-py] ERROR: Cannot overwrite {df.physical_file}\n"
                                f"Base address {hex(df.address)} is bigger than the requested address {hex(cl.address)}\n"
                                f"At line: {cl.original_line}\n\n"
                            )
                            print(error_msg)
                            if self.abort_build_request():
                                return False
                            continue

                        # checking whether the original file exists and retrieving its size
                        game_file = build_files_folder + df.physical_file
                        if not _files.check_file(game_file):
                            if self.abort_build_request():
                                return False
                            continue
                        game_file_size = os.path.getsize(game_file)

                        # checking whether the modded file exists and retrieving its size
                        mod_file = cl.get_output_name()
                        if not os.path.isfile(mod_file):
                            print("\n[ISO-py] ERROR: " + mod_file + " not found.\n")
                            if self.abort_build_request():
                                return False
                            continue
                        mod_size = os.path.getsize(mod_file)

                        # Checking potential file size overflows and warning the user about them
                        offset = cl.address - df.address + df.offset
                        if (mod_size + offset) > game_file_size:
                            logger.warning(f"{mod_file} will increase total file size of {game_file}\n")

                        mod_data = bytearray()
                        with open(mod_file, "rb") as mod:
                            mod_data = bytearray(mod.read())
                        if game_file not in modded_files:
                            modified_game_file = build_files_folder + df.physical_file
                            modded_stream = open(modified_game_file, "r+b")
                            modded_files[game_file] = [modded_stream, bytearray(modded_stream.read())]
                            iso_changed = True

                        modded_stream = modded_files[game_file][0]
                        modded_buffer = modded_files[game_file][1]
                        # Add zeroes if the new total file size is more than the original file size
                        for i in range(len(modded_buffer), offset + mod_size):
                            modded_buffer.append(0)
                        for i in range(mod_size):
                            modded_buffer[i + offset] = mod_data[i]

                    # if it's not a file to be overwritten in the game
                    # assume it's a new file to be inserted in the disc
                    else:
                        filename = (cl.section_name + ".bin").upper()
                        filename_len = len(filename)
                        if filename_len > 12:
                            filename = filename[(filename_len - 12):]
                        mod_file = OUTPUT_FOLDER + cl.section_name + ".bin"
                        dst = build_files_folder + filename
                        shutil.copyfile(mod_file, dst)
                        contents = {
                            "name": filename,
                            "source": modified_rom_name + "/" + filename,
                            "type": "data"
                        }
                        element = et.Element("file", contents)
                        dir_tree.insert(-1, element)
                        iso_changed = True

                # writing changes to files we overwrote
                for game_file in modded_files:
                    modded_stream = modded_files[game_file][0]
                    modded_buffer = modded_files[game_file][1]
                    modded_stream.seek(0)
                    modded_stream.write(modded_buffer)
                    modded_stream.close()
                if iso_changed:
                    xml_tree.write(xml)

        return iso_changed

    def convert_xml(self, xml: str, new_xml: str, modified_rom_name: str) -> None:
        xml_tree = et.parse(xml)
        for element in xml_tree.iter():
            key = "source"
            if key in element.attrib:
                element_source = element.attrib[key].split("/")
                element_source[0] = modified_rom_name
                element_source = "/".join(element_source)
                element.attrib[key] = element_source
        xml_tree.write(new_xml)

    def build(self, only_extract=False) -> None:
        gv = self.ask_user_for_version()
        last_compiled_version = get_build_id()
        if last_compiled_version is not None and gv.build_id != last_compiled_version:
            print("\n[ISO-py] WARNING: iso build was requested for version: " + gv.version + ", but last compiled version was: " + game_options.get_gv_by_build_id(last_compiled_version).version)
            print("This could mean that some output files may contain data for the wrong version, resulting in a corrupted disc.")
            if self.abort_build_request():
                return
        rom_name = gv.rom_name.split(".")[0]
        extract_folder = ISO_PATH / rom_name
        xml = extract_folder.with_suffix(".xml")
        if only_extract:
            self.extract_iso_to_xml(gv, extract_folder, xml)
            return
        if not _files.check_file(COMPILE_LIST):
            return
        if not os.path.isfile(xml):
            self.extract(gv, extract_folder, xml)
        modified_rom_name = f"{rom_name}_{MOD_NAME}"
        build_files_folder = ISO_PATH / modified_rom_name
        new_xml = build_files_folder + ".xml"
        _files.delete_directory(build_files_folder)
        logger.info("Copying files...")
        shutil.copytree(extract_folder, build_files_folder)
        logger.info("Converting XML...")
        self.convert_xml(xml, new_xml, modified_rom_name)
        build_bin = build_files_folder + ".bin"
        build_cue = build_files_folder + ".cue"
        logger.info("Patching files...")
        if self.patch_iso(gv.version, gv.build_id, build_files_folder, modified_rom_name, new_xml):
            logger.info("Building iso...")
            self.plugin.build(self.python_path / PLUGIN_PATH, self.python_path / build_files_folder)
            pymkpsxiso.make(build_bin, build_cue, new_xml)
            logger.info("Build completed.")
        else:
            logger.warning("No files changed. ISO building skipped.")

    def xdelta(self) -> None:
        gv = self.ask_user_for_version()
        original_game = ISO_PATH / gv.rom_name
        mod_name = gv.rom_name.split(".")[0] + "_" + MOD_NAME
        modded_game = ISO_PATH / (mod_name + ".bin")
        if not _files.check_file(original_game):
            print(f"Make sure your original game is in {ISO_PATH}.\n")
            return
        if not _files.check_file(modded_game):
            print("Make sure you compiled and built your mod before trying to generate a xdelta patch.\n")
            return
        print("Generating xdelta patch...")
        output = ISO_PATH / (mod_name + ".xdelta")
        pyxdelta.run(original_game, modded_game, output)
        logger.info(f"{output} generated!")

    def clean(self, all=False) -> None:
        for version in game_options.get_version_names():
            gv = game_options.get_gv_by_name(version)
            rom_name = gv.rom_name.split(".")[0]
            modified_rom_name = rom_name + "_" + MOD_NAME
            build_files_folder = ISO_PATH / modified_rom_name
            build_cue = build_files_folder.with_suffix(".cue")
            build_bin = build_files_folder.with_suffix(".bin")
            build_xml = build_files_folder.with_suffix(".xml")
            build_xdelta = build_files_folder.with_suffix(".xdelta")
            if all:
                extract_xml = ISO_PATH / (rom_name + ".xml")
                extract_folder = extract_xml.stem

                _files.delete_directory(extract_folder)
                _files.delete_file(extract_xml)
            _files.delete_directory(build_files_folder)
            _files.delete_file(build_bin)
            _files.delete_file(build_cue)
            _files.delete_file(build_xml)
            _files.delete_file(build_xdelta)

    def extract_iso(self) -> None:
        self.build(only_extract=True)
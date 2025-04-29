"""
TODO: Replace with Click
pyxdelta doesn't support pathlib
Assume all plugins.py don't support pathlib
plugins assume os.sep is there
"""

import _files # check_file, delete_file, create_directory, delete_directory
from common import ISO_PATH, MOD_NAME, OUTPUT_FOLDER, COMPILE_LIST , FILE_LIST , MOD_DIR, PLUGIN_PATH, request_user_input, cli_pause, get_build_id
from game_options import game_options
from disc import Disc
from compile_list import CompileList, free_sections
from syms import Syms

import importlib
import logging
import os
import pathlib
import pdb
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
        path = PLUGIN_PATH / "plugin.py"
        spec = importlib.util.spec_from_file_location("plugin", path)
        self.plugin = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.plugin)

    def find_iso(self, instance_version) -> bool:
        if not _files.check_file(ISO_PATH / instance_version.rom_name):
            print(f"Please insert your {instance_version.version} game in {ISO_PATH} and rename it to {instance_version.rom_name}")
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

    def extract_iso_to_xml(self, instance_version, dir_out, fname_out: str) -> None:
        """
        NOTE: We're converting some of the pathlibs to strings
            because we don't know if the pymkpsxiso or self.plugin support pathlib yet

        """
        has_iso = self.find_iso(instance_version)
        count_retries = 0
        while (not has_iso):
            cli_pause()
            has_iso = self.find_iso(instance_version)
            count_retries += 1
            if 5 <= count_retries:
                logger.critical("Max retries exeeced to find iso. Exiting")
                sys.exit(9)
        rom_path = ISO_PATH / instance_version.rom_name
        _files.create_directory(dir_out)
        # TODO: Find out if the plugin and pymk... support pathlib
        pymkpsxiso.dump(str(rom_path), f"{str(dir_out)}{os.sep}", str(fname_out))
        self.plugin.extract(f"{str(PLUGIN_PATH)}{os.sep}", f"{str(dir_out)}{os.sep}", f"{instance_version.version}")

    def abort_build_request(self) -> bool:
        """ TODO: Replace with click """
        intro_msg = """
        Abort iso build?
        1 - Yes
        2 - No
        """
        error_msg = "Invalid input. Please type a number from 1-2."
        return request_user_input(first_option=1, last_option=2, intro_msg=intro_msg, error_msg=error_msg) == 1

    def patch_iso(self, version: str, build_id: int, dir_in_build, modified_rom_name: str, fname_xml: str, usedFileList: bool) -> bool:
        """
        dir_in_build and xml are paths
        TODO: Refactor this since it's doing way too much
        """
        disc = Disc(version)
        sym = Syms(build_id)
        modded_files = dict()
        iso_changed = False
        xml_tree = et.parse(fname_xml)
        dir_tree = xml_tree.findall(".//directory_tree")[0]
        build_lists = ["./"] # cwd
        while build_lists:
            prefix = build_lists.pop(0)
            bl = (pathlib.Path(prefix) / COMPILE_LIST).resolve() # TODO: Double check
            free_sections()
            with open(bl, "r") as file:
                for line in file:
                    instance_cl = CompileList(line, sym, prefix)
                    if not instance_cl.should_build():
                        continue

                    # if it's a file to be overwritten in the game
                    df = disc.get_df(instance_cl.game_file)
                    if df is not None:
                        # checking file start boundaries
                        if instance_cl.address < df.address:
                            error_msg = f"""
                            [ISO-py] ERROR: Cannot overwrite {df.physical_file}
                            Base address {hex(df.address)} is bigger than the requested address {hex(instance_cl.address)}
                            At line: {instance_cl.original_line}
                            """
                            print(error_msg)
                            if self.abort_build_request():
                                return False
                            continue

                        # checking whether the original file exists and retrieving its size
                        game_file = dir_in_build / df.physical_file
                        if not _files.check_file(game_file):
                            if self.abort_build_request():
                                return False
                            continue
                        game_file_size = os.path.getsize(game_file)

                        # checking whether the modded file exists and retrieving its size
                        mod_file = instance_cl.get_output_name()
                        if not _files.check_file(mod_file):
                            if self.abort_build_request():
                                return False
                            continue
                        mod_size = os.path.getsize(mod_file)

                        # Checking potential file size overflows and warning the user about them
                        offset = instance_cl.address - df.address + df.offset
                        if (mod_size + offset) > game_file_size:
                            logger.warning(f"{mod_file} will increase total file size of {game_file}\n")

                        mod_data = bytearray()
                        with open(mod_file, "rb") as mod:
                            mod_data = bytearray(mod.read())
                        if game_file not in modded_files:
                            modified_game_file = dir_in_build / df.physical_file
                            modded_stream = open(modified_game_file, "r+b") # BUG: Should this be closed?
                            modded_files[game_file] = [modded_stream, bytearray(modded_stream.read())]
                            iso_changed = True

                        modded_stream = modded_files[game_file][0]
                        modded_buffer = modded_files[game_file][1]
                        # Add zeroes if the new total file size is more than the original file size
                        for i in range(len(modded_buffer), offset + mod_size):
                            modded_buffer.append(0)
                        for i in range(mod_size):
                            modded_buffer[i + offset] = mod_data[i]

                # writing changes to files we overwrote
                for game_file in modded_files:
                    modded_stream = modded_files[game_file][0]
                    modded_buffer = modded_files[game_file][1]
                    modded_stream.seek(0)
                    modded_stream.write(modded_buffer)
                    modded_stream.close()
                if iso_changed or usedFileList:
                    xml_tree.write(fname_xml)

        
        return iso_changed

    def convert_xml(self, fname, fname_out, modified_rom_name: str,fextra: list[str]) -> None:
        xml_tree = et.parse(fname) # filename

        if fextra:
            for element in xml_tree.iter("directory_tree"):
                for srcName in fextra:
                    new_element = et.Element('file')
                    discName = srcName.split('/')[-1]
                    new_element.set('name',discName)
                    new_element.set('source',modified_rom_name + '/' + discName)
                    new_element.set('type','data')
                    new_element.tail = '\n\t\t'
                    element.insert(-1,new_element)
                break

        for element in xml_tree.iter():
            key = "source"
            if key in element.attrib:
                element_source = element.attrib[key].split("/")
                element_source[0] = modified_rom_name
                element_source = "/".join(element_source)
                element.attrib[key] = element_source
        xml_tree.write(fname_out)

    def build_iso(self, only_extract=False) -> None:
        instance_version = self.ask_user_for_version()
        last_compiled_version = get_build_id()
        if last_compiled_version is not None and instance_version.build_id != last_compiled_version:
            print("\n[ISO-py] WARNING: iso build was requested for version: " + instance_version.version + ", but last compiled version was: " + game_options.get_gv_by_build_id(last_compiled_version).version)
            print("This could mean that some output files may contain data for the wrong version, resulting in a corrupted disc.")
            if self.abort_build_request():
                return
        rom_name = instance_version.rom_name.split(".")[0]
        extract_folder = ISO_PATH / rom_name
        xml = extract_folder.with_suffix(".xml")
        if only_extract:
            self.extract_iso_to_xml(instance_version, extract_folder, xml)
            return
        if not _files.check_file(COMPILE_LIST):
            return
        if not pathlib.Path(xml).exists(): # don't need to log error
            self.extract_iso_to_xml(instance_version, extract_folder, xml)
        modified_rom_name = f"{rom_name}_{MOD_NAME}"
        build_files_folder = ISO_PATH / modified_rom_name
        new_xml = build_files_folder.with_suffix(".xml")
        _files.delete_directory(build_files_folder)
        logger.info("Copying files...")
        shutil.copytree(extract_folder, build_files_folder)

        extraFiles = []
        usedFileList = False

        #check for optional fileList.txt
        if os.path.exists(MOD_DIR + FILE_LIST):
            logger.info("Adding files from fileList.txt ...")
            with open(MOD_DIR + FILE_LIST, 'r') as file:
                lines = file.readlines()
            for line in lines:
                cleaned_line = line.strip().replace(' ', '').replace('\t','')
                if not cleaned_line or cleaned_line.startswith("//"):
                    continue
                words = cleaned_line.split(',')
                if words[0] == instance_version.version:
                    srcFile = words[1]

                    if len(words) < 3:
                        extraFiles.append(srcFile)
                        shutil.copyfile(MOD_DIR + srcFile, build_files_folder / words[1].split('/')[-1])
                    else:
                        shutil.copyfile(MOD_DIR + srcFile, build_files_folder / words[2])
                    usedFileList = True
        

        logger.info("Converting XML...")
        self.convert_xml(xml, new_xml, modified_rom_name,extraFiles)
        build_bin = build_files_folder.with_suffix(".bin")
        build_cue = build_files_folder.with_suffix(".cue")
        logger.info("Patching files...")
        if self.patch_iso(instance_version.version, instance_version.build_id, build_files_folder, modified_rom_name, new_xml, usedFileList):
            logger.info("Building iso...")
            self.plugin.build(f"{str(PLUGIN_PATH)}{os.sep}", f"{str(build_files_folder)}{os.sep}", f"{instance_version.version}")
            pymkpsxiso.make(str(build_bin), str(build_cue), str(new_xml))
            logger.info("Build completed.")
        else:
            logger.warning("No files changed. ISO building skipped.")

    def xdelta(self) -> None:
        instance_version = self.ask_user_for_version()
        original_game = ISO_PATH / instance_version.rom_name
        mod_name = instance_version.rom_name.split(".")[0] + "_" + MOD_NAME
        modded_game = ISO_PATH / (mod_name + ".bin")
        if not _files.check_file(original_game):
            print(f"Make sure your original game is in {ISO_PATH}.\n")
            return
        if not _files.check_file(modded_game):
            print("Make sure you compiled and built your mod before trying to generate a xdelta patch.\n")
            return
        print("Generating xdelta patch...")
        output = ISO_PATH / (mod_name + ".xdelta")
        pyxdelta.run(str(original_game), str(modded_game), str(output))
        logger.info(f"{output} generated!")

    def clean(self, all=False) -> None:
        for version in game_options.get_version_names():
            instance_version = game_options.get_gv_by_name(version)
            rom_name = instance_version.rom_name.split(".")[0]
            modified_rom_name = rom_name + "_" + MOD_NAME
            build_files_folder = ISO_PATH / modified_rom_name
            build_cue = build_files_folder.with_suffix(".cue")
            build_bin = build_files_folder.with_suffix(".bin")
            build_xml = build_files_folder.with_suffix(".xml")
            build_xdelta = build_files_folder.with_suffix(".xdelta")
            if all:
                extract_xml = ISO_PATH / (rom_name + ".xml")
                extract_folder = ISO_PATH / extract_xml.stem
                _files.delete_directory(extract_folder)
                _files.delete_file(extract_xml)
            _files.delete_directory(build_files_folder)
            _files.delete_file(build_bin)
            _files.delete_file(build_cue)
            _files.delete_file(build_xml)
            _files.delete_file(build_xdelta)

    def extract_iso(self) -> None:
        self.build_iso(only_extract=True)

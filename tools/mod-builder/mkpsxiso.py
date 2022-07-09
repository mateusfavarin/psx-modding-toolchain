from common import ISO_PATH, MOD_NAME, OUTPUT_FOLDER, COMPILE_LIST, request_user_input, create_directory, cli_pause, check_compile_list
from game_options import game_options
from disc import Disc
from compile_list import CompileList, free_sections
from syms import Syms

import xml.etree.ElementTree as et
import shutil
import os

class Mkpsxiso:
    def __init__(self) -> None:
        pass

    def find_iso(self, gv) -> bool:
        if (not os.path.isfile(ISO_PATH + gv.rom_name)):
            print("ERROR:")
            print(ISO_PATH + gv.rom_name + " not found.")
            print("Please insert your " + gv.version + " game in the " + ISO_PATH + " directory,")
            print("and rename it to " + gv.rom_name)
            return False
        return True

    def ask_user_for_version(self):
        names = game_options.get_version_names()
        print("Select the game version:")
        for i in range(len(names)):
            print(str(i + 1) + " - " + names[i])
        error_msg = "ERROR: Invalid version. Please select a number from 1-" + str(len(names)) +"."
        version = request_user_input(first_option=1, last_option=len(names), error_msg=error_msg)
        return game_options.get_gv_by_name(names[version - 1])

    def extract(self, gv, extract_folder: str, xml: str) -> None:
        has_iso = self.find_iso(gv)
        while not has_iso:
            cli_pause()
            has_iso = self.find_iso(gv)
        rom_path = ISO_PATH + gv.rom_name
        create_directory(extract_folder)
        os.system("dumpsxiso -x " + extract_folder + " -s " + xml + " " + rom_path)

    def patch_iso(self, version: str, build_id: int, extract_folder: str, build_files_folder: str, rom_name: str, modified_rom_name: str, xml: str, new_xml: str) -> bool:
        disc = Disc(version)
        sym = Syms(build_id)
        modded_files = dict()
        iso_changed = False
        extract_folder += "/"
        build_files_folder += "/"
        xml_tree = et.parse(xml)
        dir_tree = xml_tree.findall(".//directory_tree")[0]
        with open(COMPILE_LIST, "r") as file:
            for line in file:
                cl = CompileList(line, sym)
                if not cl.should_build():
                    continue
                df = disc.get_df(cl.game_file)
                if df is not None:
                    if (cl.address - df.address) < 0:
                        print("\n[Mkpsxiso-py] ERROR: Cannot overwrite " + df.physical_file)
                        print("Base address " + hex(df.address) + " is bigger than the requested address " + hex(cl.address))
                        print("At line: " + cl.original_line + "\n")
                        print("Abort iso build?")
                        print("1 - Yes")
                        print("2 - No")
                        error_msg = "Invalid input. Please type a number from 1-2."
                        should_quit = request_user_input(first_option=1, last_option=2, error_msg=error_msg) == 1
                        if should_quit:
                            iso_changed = False
                            return
                        continue
                    game_file = extract_folder + df.physical_file
                    game_file_size = os.path.getsize(game_file)
                    mod_file = OUTPUT_FOLDER + cl.section_name + ".bin"
                    if not os.path.isfile(mod_file):
                        print("\n[Mkpsxiso-py] ERROR: " + mod_file + " not found.\n")
                        continue
                    mod_size = os.path.getsize(mod_file)
                    offset = cl.address - df.address + df.offset
                    if (mod_size + offset) > game_file_size:
                        print("\n[Mkpsxiso-py] ERROR: " + mod_file + " is bigger than " + game_file + "\n")
                        continue
                    mod_data = bytearray()
                    with open(mod_file, "rb") as mod:
                        mod_data = bytearray(mod.read())
                    if game_file not in modded_files:
                        modified_game_file = build_files_folder + df.physical_file
                        shutil.copyfile(game_file, modified_game_file)
                        element = xml_tree.find(".//file[@name='" + df.physical_file + "']")
                        element_source = element.attrib["source"].split("/")
                        element_source[0] = modified_rom_name
                        element_source = "/".join(element_source)
                        element.attrib["source"] = element_source
                        iso_changed = True
                        modded_stream = open(modified_game_file, "r+b")
                        modded_files[game_file] = [modded_stream, bytearray(modded_stream.read())]
                    modded_stream = modded_files[game_file][0]
                    modded_buffer = modded_files[game_file][1]
                    modded_stream.seek(0)
                    for i in range(mod_size):
                        modded_buffer[i + offset] = mod_data[i]
                    modded_stream.write(modded_buffer)
                else:
                    # assume it's a new file to be inserted in the disc
                    filename = (cl.section_name + ".bin").upper()
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
            for game_file in modded_files:
                modded_stream = modded_files[game_file][0]
                modded_stream.close()
            if iso_changed:
                xml_tree.write(new_xml)
            free_sections()
        return iso_changed

    def build(self, only_extract=False) -> None:
        gv = self.ask_user_for_version()
        rom_name = gv.rom_name.split(".")[0]
        extract_folder = ISO_PATH + rom_name
        xml = extract_folder + ".xml"
        if only_extract:
            self.extract(gv, extract_folder, xml)
            return
        if not check_compile_list():
            print("\n[Mkpsxiso-py] ERROR: " + COMPILE_LIST + " not found.\n")
            return
        if not os.path.isfile(xml):
            self.extract(gv, extract_folder, xml)
        modified_rom_name = rom_name + "_" + MOD_NAME
        build_files_folder = ISO_PATH + modified_rom_name
        new_xml = build_files_folder + ".xml"
        if os.path.isdir(build_files_folder):
            shutil.rmtree(build_files_folder)
        create_directory(build_files_folder)
        hack_bin = build_files_folder + ".bin"
        hack_cue = build_files_folder + ".cue"
        if self.patch_iso(gv.version, gv.build_id, extract_folder, build_files_folder, rom_name, modified_rom_name, xml, new_xml):
            print("Building iso...")
            os.system("mkpsxiso -y -q -o " + hack_bin + " -c " + hack_cue + " " + new_xml)
            print("Build completed.")
        else:
            print("\n[Mkpsxiso-py] WARNING: No files changed. ISO building skipped.\n")

    def clean(self, all=False) -> None:
        for version in game_options.get_version_names():
            gv = game_options.get_gv_by_name(version)
            rom_name = gv.rom_name.split(".")[0]
            modified_rom_name = rom_name + "_" + MOD_NAME
            build_files_folder = ISO_PATH + modified_rom_name
            if all:
                extract_folder = ISO_PATH + rom_name
                os.system("rm " + extract_folder + ".xml")
                os.system("rm -rf " + extract_folder)
            os.system("rm " + build_files_folder + ".* ")
            os.system("rm -rf " + build_files_folder)

    def extract_iso(self) -> None:
        self.build(only_extract=True)
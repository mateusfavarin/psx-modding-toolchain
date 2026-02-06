import _files # check_file
from syms import Syms
from compile_list import CompileList, free_sections
from common import COMPILE_LIST, ISO_PATH, REDUX_MAP_FILE, SETTINGS_PATH, BACKUP_FOLDER, TEXTURES_OUTPUT_FOLDER, MOD_NAME, request_user_input, get_build_id, cli_pause
from image import get_image_list
from clut import get_clut_list
from game_options import game_options
from mkpsxiso import Mkpsxiso
from disc import Disc, DiscFile

import logging
import json
import os
import pathlib
import requests
import subprocess
import sys

logger = logging.getLogger(__name__)

REDUX_EXES = ["pcsx-redux", "pcsx-redux.exe"]

class Redux:
    def __init__(self) -> None:
        pass

    def load_config(self, fname) -> bool:
        """
        fname is a path to settings.json
        Assumes of the form
        {
            "redux": {"port": int, "path": absolute path }
        }
        TODO: Abstract loading a JSON and passing in this data directly
        """
        with open(fname) as file:
            data = json.load(file)["redux"]
            self.port = str(data["port"])
            self.url = "http://127.0.0.1:" + str(self.port)
            self.found_redux = False
            self.path = pathlib.Path(data["path"]) # pathlib object
            if not _files.check_file(self.path):
                return False
            self.command = []
            for exe in REDUX_EXES: # find the REDUX file
                cmd = self.path / exe
                if _files.check_file(cmd):
                    self.command.append(str(cmd))
                    self.found_redux = True
                    return True
            return False

    def get_game_name(self) -> str:
        names = game_options.get_version_names()
        intro_msg = "Select the game version:\n"
        for i, name in enumerate(names):
            intro_msg += f"{i + 1} - {name}\n"
        error_msg = f"ERROR: Invalid version. Please select a number from 1-{len(names)}."
        version = request_user_input(first_option=1, last_option=len(names), intro_msg=intro_msg, error_msg=error_msg)
        out = game_options.get_gv_by_name(names[version - 1]).rom_name

        return out

    def construct_path_game(self):
        """ TODO: This can be simplified """
        if not self.found_redux:
            count_retries = 0
            while not self.load_config(SETTINGS_PATH):
                print("\n[Redux-py] Could not find a valid path to PCSX-Redux emulator.")
                print("Please check your settings.json and provide a valid path to redux.\n")
                cli_pause()
                count_retries += 1
                if 5 <= count_retries:
                    logger.critical("Max retries exeeced to find redux path. Exiting")
                    sys.exit(9)
            logger.info(f"Found PCSX-Redux executable at {self.command}")
        dir_current = pathlib.Path.cwd()
        game_name = self.get_game_name()
        logger.debug(f"game_name: {game_name}")
        mod_name = game_name.split(".")[0] + "_" + MOD_NAME + ".bin"
        generic_path = dir_current / ISO_PATH
        path_game = generic_path / mod_name
        if not _files.check_file(path_game):
            # if modded game not found, fallback to original game
            path_game = generic_path / game_name
            if not _files.check_file(path_game):
                print("PCSX-Redux will start without booting the iso.")

        return path_game

    def start_emulation(self) -> None:
        """ TODO: Way too much going on here """
        path_game = self.construct_path_game()
        dir_current = pathlib.Path.cwd()
        os.chdir(self.path)
        self.command.append("-run")
        self.command.append("-loadiso")
        self.command.append(str(path_game))

        dict_params = {
            "shell": False,
            "stdout": None,
            "stderr": None,
            "start_new_session": True,
            "close_fds": True, # prevent deadlocks
            # "check": True
        }
        if os.name == "posix": # linux
            dict_params["preexec_fn"]=os.setpgrp
            self.command.insert("nohup", 0)
        elif os.name == 'nt': # windows
            dict_params["stdin"]=None
            dict_params["creationflags"] = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP

        try:
            result = subprocess.Popen(self.command, **dict_params)
            # output, error = instance_process.communicate()
            # if instance_process.returncode != 0:
            #     logger.exception(f"Process failed: {instance_process.returncode} {output} {error}", exc_info=False)
        except subprocess.CalledProcessError as error:
            logger.exception(error, exc_info = False)

        os.chdir(dir_current) # go back to cwd
        self.load_map(warnings=False)

    def flush_cache(self) -> None:
        response = requests.post(self.url + "/api/v1/cpu/cache?function=flush")
        if response.status_code == 200:
            print("Cache flushed.")
        else:
            print("\n[Redux - Web Server] error flushing cache.\n")

    def get_emulation_running_state(self) -> bool:
        response = requests.get(self.url + "/api/v1/execution-flow")
        if response.status_code == 200:
            print("Retrieved emulation state.")
        else:
            print("\n[Redux - Web Server] error retrieving the emulation state.\n")
            return False
        return response.json()["running"]

    def pause_emulation(self) -> None:
        response = requests.post(self.url + "/api/v1/execution-flow?function=pause")
        if response.status_code == 200:
            print("Paused the emulator.")
        else:
            print("\n[Redux - Web Server] error pausing the emulator.\n")

    def resume_emulation(self) -> None:
        response = requests.post(self.url + "/api/v1/execution-flow?function=resume")
        if response.status_code == 200:
            print("Resumed the emulation.")
        else:
            print("\n[Redux - Web Server] error resuming the emulation.\n")

    def reset_map(self) -> None:
        response = requests.post(self.url + "/api/v1/assembly/symbols?function=reset")
        if response.ok:
            if response.status_code == 200:
                logger.info("Successfully reset redux map symbols.")
        else:
            logger.error("Web Server: error resetting the map file.")

    def load_map(self, warnings=True) -> None:
        self.reset_map()
        if not _files.check_file(REDUX_MAP_FILE):
            if warnings:
                print("\n[Redux-py] ERROR: No map file found. Make sure you have compiled your mod before trying to hot reload.\n")
            return
        file = open(REDUX_MAP_FILE, "rb")
        files = {"file": file}
        response = requests.post(self.url + "/api/v1/assembly/symbols?function=upload", files=files)
        if response.ok:
            if response.status_code == 200:
                logger.info(f"Successfully loaded {REDUX_MAP_FILE}")
        else:
            logger.error(f"Web Server: error loading {REDUX_MAP_FILE}")

    def inject(self, backup: bool, restore: bool) -> None:
        build_id = get_build_id()
        if build_id is None:
            print("\n[Redux-py] ERROR: No output files found. Make sure that you have compiled your mod before trying to hot reload.\n")
            return
        sym = Syms(get_build_id())
        url = self.url + "/api/v1/cpu/ram/raw"
        psx_ram = bytearray()
        if backup:
            response = requests.get(url)
            if response.ok:
                if response.status_code == 200:
                    psx_ram = response.content
                    logger.info("Successfully retrieved a backup of the RAM.")
            else:
                logger.error("Web Server: error backing up the RAM.")
        build_lists = ["./"]
        while build_lists:
            prefix = build_lists.pop(0)
            build_list = prefix + COMPILE_LIST
            free_sections()
            with open(build_list, "r") as file:
                for line in file:
                    cl = CompileList(line, sym, prefix)
                    if not cl.should_build() or cl.skip_reload:
                        continue
                    bin = cl.get_output_name() # pathlib object
                    backup_bin = pathlib.Path(prefix) / BACKUP_FOLDER / ("redux_" + cl.section_name + ".bin")
                    offset = cl.address & 0xFFFFFFF
                    if not _files.check_file(bin):
                        continue
                    size = os.path.getsize(bin)
                    if backup:
                        section = psx_ram[offset : (offset + size)]
                        with open(backup_bin, "wb") as file:
                            file.write(section)
                    if restore:
                        bin = backup_bin
                        if not _files.check_file(bin):
                            continue
                        size = os.path.getsize(bin)
                    file = open(bin, "rb")
                    files = {"file": file}
                    response = requests.post(url + "?offset=" + str(offset) + "&size=" + str(size), files=files)
                    if response.ok:
                        if response.status_code == 200:
                            if restore:
                                logger.info(f"{bin} successfully restored.")
                            else:
                                logger.info(f"{bin} successfully injected.")
                    else:
                        logger.error(f"Web Server: error injecting {bin}")
                    file.close()

    def inject_textures(self, backup: bool, restore: bool) -> None:
        url = self.url + "/api/v1/gpu/vram/raw"
        vram_path = TEXTURES_OUTPUT_FOLDER / "vram.bin"
        if backup:
            response = requests.get(url)
            if response.ok:
                if response.status_code == 200:
                    vram = response.content
                    logger.info("Successfully retrieved a backup of the VRAM.")
            else:
                logger.error("Web Server: Error backing up the VRAM.")
            with open(vram_path, "wb") as file:
                file.write(vram)
        if restore:
            if os.path.isfile(vram_path):
                vram_width = 1024
                vram_height = 512
                file = open(vram_path, "rb")
                files = {"file": file}
                response = requests.post(url + "?x=" + str(0) + "&y=" + str(0) + "&width=" + str(vram_width) + "&height=" + str(vram_height), files=files)
                if response.status_code == 200:
                    print(vram_path + " successfully restored.")
                else:
                    print("\n[Redux - Web Server] Error restoring the VRAM.\n")
                file.close()
            else:
                print("\n[Redux - Web Server] ERROR: backup file " + vram_path + "not found.\n")
            return
        imgs = get_image_list()
        cluts = get_clut_list()
        data = [imgs, cluts]
        for textures in data:
            for img in textures:
                path = img.get_path()
                if path is not None:
                    with open(path, "rb") as file:
                        files = {"file": file}
                        url_endpoint = f"{url}?x={img.x}&y={img.y}&width={img.w}&height={img.h}"
                        response = requests.post(url_endpoint, files=files)
                        if response.ok:
                            if response.status_code == 200:
                                logger.info(f"{path} successfully injected.")
                        else:
                            logger.error(f"Web Server: error injecting {path}")

    def hot_reload(self) -> None:
        if not _files.check_file(COMPILE_LIST):
            return
        is_running = bool()
        try:
            is_running = self.get_emulation_running_state()
        except Exception:
            print("\n[Redux - Web Server] ERROR: Couldn't start a connection with redux.")
            print("Make sure that redux is running, its web server is active, and")
            print("the port configuration saved in settings.json is correct.\n")
            return
        intro_msg = """
        Would you like to backup the RAM?
        1 - Yes
        2 - No
        Note: this option is required if you want to uninstall the mod.
        By selecting yes you'll overwrite the current backup.
        """
        error_msg = "ERROR: Invalid input. Please enter 1 for Yes or 2 for No."
        backup = request_user_input(first_option=1, last_option=2, intro_msg=intro_msg, error_msg=error_msg) == 1
        self.pause_emulation()
        self.inject(backup, False)
        self.load_map()
        self.flush_cache()
        if is_running:
            self.resume_emulation()

    def restore(self) -> None:
        if not _files.check_file(COMPILE_LIST):
            return
        is_running = bool()
        try:
            is_running = self.get_emulation_running_state()
        except Exception:
            print("\n[Redux - Web Server] ERROR: Couldn't start a connection with redux.")
            print("Make sure that redux is running, its web server is active, and")
            print("the port configuration saved in settings.json is correct.\n")
            return
        self.pause_emulation()
        self.inject(False, True)
        self.flush_cache()
        if is_running:
            self.resume_emulation()

    def replace_textures(self) -> None:
        print("[Redux-py] Replacing textures...\n")
        is_running = bool()
        try:
            is_running = self.get_emulation_running_state()
        except Exception:
            print("\n[Redux - Web Server] ERROR: Couldn't start a connection with redux.")
            print("Make sure that redux is running, its web server is active, and")
            print("the port configuration saved in settings.json is correct.\n")
            return

        intro_msg = """
        Would you like to backup the VRAM?
        1 - Yes
        2 - No
        Note: this option is required if you want to restore the original textures.
        By selecting yes you'll overwrite the current backup.
        """
        error_msg = "ERROR: Invalid input. Please enter 1 for Yes or 2 for No."
        backup = request_user_input(first_option=1, last_option=2, intro_msg=intro_msg, error_msg=error_msg) == 1

        self.pause_emulation()
        self.inject_textures(backup, False)
        if is_running:
            self.resume_emulation()

    def restore_textures(self) -> None:
        print("\n[Redux-py] Restoring textures...\n")
        is_running = bool()
        try:
            is_running = self.get_emulation_running_state()
        except Exception:
            print("\n[Redux - Web Server] ERROR: Couldn't start a connection with redux.")
            print("Make sure that redux is running, its web server is active, and")
            print("the port configuration saved in settings.json is correct.\n")
            return
        self.pause_emulation()
        self.inject_textures(False, True)
        if is_running:
            self.resume_emulation()

    def compare_asset_sizes(self, og_file_df: DiscFile, og_file_path: str, patch_file_path: str) -> bool:
        # this looks kinda ugly. is there a better way of doing this?
        binary = pathlib.Path(patch_file_path)
        patch_file = open(binary, "rb").read()
        binary = pathlib.Path(og_file_path)
        og_file = open(binary, "rb").read()

        if (len(patch_file) > len(og_file)):
            print("ERROR: Patch file")
            print(f"{patch_file_path}")
            print(f"is larger than {og_file_df.physical_file}.")
            return True

        return False

    def load_patch_file(self, og_file_df: DiscFile, og_file_path: str, patch_file_path: str) -> bytes:
        # this looks kinda ugly. is there a better way of doing this?
        binary = pathlib.Path(patch_file_path)
        patch_file = open(binary, "rb").read()
        binary = pathlib.Path(og_file_path)
        og_file = open(binary, "rb").read()

        if (len(patch_file) != len(og_file)):
            intro_msg = f"""
            Patch file
            {patch_file_path}
            is smaller than {og_file_df.physical_file}.
            Would you like to pad its size to match?
            1 - Yes
            2 - No
            """
            error_msg = "ERROR: Invalid input. Please enter 1 for Yes or 2 for No."
            willPad = request_user_input(first_option=1, last_option=2, intro_msg=intro_msg, error_msg=error_msg) == 1

            if (willPad):
                len_diff = len(og_file) - len(patch_file)
                patch_file += bytes(bytearray(len_diff))

        return patch_file

    def patch_disc_files(self, restore_files: bool) -> None:
        instance_version = Mkpsxiso().ask_user_for_version()

        print("\n[Redux-py] Comparing disc and patch file sizes...\n")

        # initialize disc and toolchain information
        rom_name = instance_version.rom_name.split(".")[0]
        extract_folder = ISO_PATH / rom_name
        xml = extract_folder.with_suffix(".xml")
        disc = Disc(instance_version.version)
        sym = Syms(instance_version.build_id)
        build_lists = ["./"] # cwd

        # initialize arrays to be used in file patching
        bl_line_array = []
        df_array = []

        if not pathlib.Path(xml).exists:
            print("ERROR: Extracted game files were not found.")
            return

        # read buildList contents
        while build_lists:
            prefix = build_lists.pop(0)
            bl = (pathlib.Path(prefix) / COMPILE_LIST).resolve() # TODO: Double check
            free_sections()
            with open(bl, "r") as bl_file:
                for line in bl_file:
                    instance_cl = CompileList(line, sym, prefix)

                    # check if buildList line is for a valid patch file
                    # in this context, a valid patch file is any binary (ergo, non-code (i.e. .c, .s, .cpp)) file which
                    # disc location, referred to as section in terms of the toolchain, is set to that of an existing
                    # disc file. note that the section must have its address set to 0x0 in disc.json in order to count as valid
                    if (instance_cl.is_bin):
                        df = disc.get_df(instance_cl.game_file)
                        if (not df):
                            print(f"Ignoring {instance_cl.source[0]}:")
                            print(f"section aliased \"{instance_cl.game_file}\" doesn't correspond to a disc file.\n")
                        else:
                            if (df.address != 0):
                                print(f"Ignoring {instance_cl.source[0]}:")
                                print(f"section aliased \"{instance_cl.game_file}\" has an address.\n")
                            else:
                                # if line is valid, check if patch file is larger than the disc file
                                # if yes, return
                                # if not, add relevant information to arrays for actual patching

                                # by the way this code sucks please forgive me
                                willCancel = False;
                                isLarger = self.compare_asset_sizes(df, f"{extract_folder}/{df.physical_file}".replace("\\", "/"), instance_cl.source[0])
                                if (isLarger):
                                    willCancel = True;
                                if (willCancel):
                                    return
                                bl_line_array.append(instance_cl)
                                df_array.append(df)

        if (not bl_line_array):
            print("ERROR: There are no valid patch files in the buildList.")
            return

        print("[Redux-py] Patching disc assets...\n")

        # check if pcsx redux is running, then pause
        is_running = bool()
        try:
            is_running = self.get_emulation_running_state()
        except Exception:
            print("\n[Redux - Web Server] ERROR: Couldn't start a connection with redux.")
            print("Make sure that redux is running, its web server is active, and")
            print("the port configuration saved in settings.json is correct.\n")
            return

        self.pause_emulation()

        # actual web server request code
        url = self.url + "/api/v1/cd/patch"

        count = 0 # I only know C...

        # go through array of valid patch files
        for bl_line in bl_line_array:
            filename = f"{df_array[count].physical_file};1"
            params = {"filename": filename}
            og_file_path = f"{extract_folder}/{df_array[count].physical_file}".replace("\\", "/")

            # load patch file
            # if the "Hot Reload Disc Files Restore" command was selected,
            # the patch file will instead be the original disc file
            if (restore_files):
                patch_file = self.load_patch_file(df_array[count], og_file_path, og_file_path)
            else:
                patch_file = self.load_patch_file(df_array[count], og_file_path, bl_line.source[0])
            patch_files = {"file": patch_file}

            # send HTTP request for hot-patching a disc file
            response = requests.post(url, params=params, files=patch_files)
            if response.ok:
                if response.status_code == 200:
                    logger.info("Successfully patched disc assets.")
            else:
                logger.error("Web Server: error patching disc assets.")
                return

            count = count + 1 # :')

        #resume emulator
        if is_running:
            self.resume_emulation()
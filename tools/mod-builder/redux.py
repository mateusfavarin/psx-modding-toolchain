import _files # check_file
from syms import Syms
from compile_list import CompileList, free_sections
from common import COMPILE_LIST, ISO_PATH, REDUX_MAP_FILE, SETTINGS_PATH, BACKUP_FOLDER, TEXTURES_OUTPUT_FOLDER, MOD_NAME, DISC_PATH, request_user_input, get_build_id, cli_pause
from image import get_image_list
from clut import get_clut_list
from game_options import game_options

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
        logger.debug("game_name: {game_name}")
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
                logger.info("Successfully loaded {REDUX_MAP_FILE}")
        else:
            logger.error("Web Server: error loading {REDUX_MAP_FILE}")

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
                    if cl.is_cl():
                        if cl.path_build_list is not None:
                            build_lists.append(str(cl.path_build_list))
                        else:
                            logger.warning("buildList path not set")
                    if not cl.should_build():
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
        vram_path = TEXTURES_OUTPUT_FOLDER + "vram.bin"
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
                    with open(path, "rb"):
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

    def load_patch_file(self) -> bytes:
        print("\n[Redux-py] Retrieving patch files...\n")

        binary = pathlib.Path("C:/CTR/psx-modding-toolchain-dhern023/games/Crash1/build/c1-usa/S1/S000001E.NSF")
        file = open(binary, "rb").read()

        if (len(file) > 6840320):
            print("ERROR: The replacement file is larger than the original.\n")
            return 0

        if (len(file) != 6840320):
            intro_msg = """
            The replacement file is smaller than the original.
            Would you like to pad its size to match?
            1 - Yes
            2 - No
            """
            error_msg = "ERROR: Invalid input. Please enter 1 for Yes or 2 for No."
            willPad = request_user_input(first_option=1, last_option=2, intro_msg=intro_msg, error_msg=error_msg) == 1

            if (willPad):
                len_diff = 6480320 - len(file)
                padding = [0x0 for _ in range(len_diff)]
                file += bytes(bytearray(len_diff))

        return file

    def superstarxalien(self) -> None:
        file = self.load_patch_file()

        if (file == 0):
            return

        print("\n[Redux-py] Patching disc assets...\n")
        is_running = bool()
        try:
            is_running = self.get_emulation_running_state()
        except Exception:
            print("\n[Redux - Web Server] ERROR: Couldn't start a connection with redux.")
            print("Make sure that redux is running, its web server is active, and")
            print("the port configuration saved in settings.json is correct.\n")
            return
        self.pause_emulation()
        #actual web server request code
        url = self.url + "/api/v1/cd/patch"
        params = {"filename": "S0/S0000009.NSF;1"}
        files = {"file": file}
        response = requests.post(url, params=params, files=files)
        if response.ok:
            if response.status_code == 200:
                logger.info("Successfully patched disc assets.")
        else:
            logger.error("Web Server: error patching disc assets.")

        #lemme do it again ok
        params = {"filename": "S0/S0000009.NSD;1"}
        binary = pathlib.Path("C:/CTR/psx-modding-toolchain-dhern023/games/Crash1/mods/WillyExperiments/src/S0000009.NSD")
        file = open(binary, "rb")
        files = {"file": file}
        requests.post(url, params=params, files=files)

        #resume emulator
        if is_running:
            self.resume_emulation()
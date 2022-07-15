from syms import Syms
from compile_list import CompileList, free_sections
from common import COMPILE_LIST, REDUX_MAP_FILE, SETTINGS_PATH, OUTPUT_FOLDER, BACKUP_FOLDER, request_user_input, get_build_id, check_compile_list

import os
import json
import requests as r

class Redux:
    def __init__(self) -> None:
        pass

    def load_config(self) -> None:
        with open(SETTINGS_PATH) as file:
            data = json.load(file)["redux"]
            self.port = str(data["port"])
            self.url = "http://127.0.0.1:" + str(self.port)

    def flush_cache(self) -> None:
        response = r.post(self.url + "/api/v1/cpu/cache?function=flush")
        if response.status_code == 200:
            print("Cache flushed.")
        else:
            print("\n[Redux - Web Server] error flushing cache.\n")

    def get_emulation_running_state(self) -> bool:
        response = r.get(self.url + "/api/v1/execution-flow")
        if response.status_code == 200:
            print("Retrieved emulation state.")
        else:
            print("\n[Redux - Web Server] error retrieving the emulation state.\n")
            return False
        return response.json()["running"]

    def pause_emulation(self) -> None:
        response = r.post(self.url + "/api/v1/execution-flow?function=pause")
        if response.status_code == 200:
            print("Paused the emulator.")
        else:
            print("\n[Redux - Web Server] error pausing the emulator.\n")

    def resume_emulation(self) -> None:
        response = r.post(self.url + "/api/v1/execution-flow?function=resume")
        if response.status_code == 200:
            print("Resumed the emulation.")
        else:
            print("\n[Redux - Web Server] error resuming the emulation.\n")

    def reset_map(self) -> None:
        response = r.post(self.url + "/api/v1/assembly/symbols?function=reset")
        if response.status_code == 200:
            print("Successfully reset redux map symbols.")
        else:
            print("\n[Redux - Web Server] error resetting the map file.\n")

    def load_map(self) -> None:
        self.reset_map()
        if not os.path.isfile(REDUX_MAP_FILE):
            print("\n[Redux-py] ERROR: No map file found. Make sure you have compiled your mod before trying to hot reload.\n")
            return
        file = open(REDUX_MAP_FILE, "rb")
        files = {"file": file}
        response = r.post(self.url + "/api/v1/assembly/symbols?function=upload", files=files)
        if response.status_code == 200:
            print("Successfully loaded " + REDUX_MAP_FILE)
        else:
            print("\n[Redux - Web Server] error loading " + REDUX_MAP_FILE + "\n")

    def inject(self, backup: bool, restore: bool) -> None:
        build_id = get_build_id()
        if build_id is None:
            print("\n[Redux-py] ERROR: No output files found. Make sure that you have compiled your mod before trying to hot reload.\n")
            return
        sym = Syms(get_build_id())
        url = self.url + "/api/v1/cpu/ram/raw"
        psx_ram = bytearray()
        if backup:
            response = r.get(url)
            if response.status_code == 200:
                psx_ram = response.content
                print("Successfully retrieved a backup of the RAM.")
            else:
                print("\n[Redux - Web Server] error backing up RAM.\n")
        with open(COMPILE_LIST, "r") as file:
            for line in file:
                cl = CompileList(line, sym)
                if not cl.should_build():
                    continue
                bin = str()
                if cl.is_bin:
                    bin = cl.source[0]
                else:
                    bin = OUTPUT_FOLDER + cl.section_name + ".bin"
                backup_bin = BACKUP_FOLDER + "redux_" + cl.section_name + ".bin"
                offset = cl.address & 0xFFFFFFF
                if not os.path.isfile(bin):
                    print("\n[Redux-py] ERROR: " + bin + " not found.\n")
                    continue
                size = os.path.getsize(bin)
                if backup:
                    section = psx_ram[offset : (offset + size)]
                    with open(backup_bin, "wb") as file:
                        file.write(section)
                if restore:
                    bin = backup_bin
                    if not os.path.isfile(bin):
                        print("\n[Redux-py] ERROR: " + bin + " not found.\n")
                        continue
                    size = os.path.getsize(bin)
                file = open(bin, "rb")
                files = {"file": file}
                if not cl.should_ignore():
                    response = r.post(url + "?offset=" + str(offset) + "&size=" + str(size), files=files)
                    if response.status_code == 200:
                        if restore:
                            print(bin + " successfully restored.")
                        else:
                            print(bin + " successfully injected.")
                    else:
                        print("\n[Redux - Web Server] error injecting " + bin + "\n")
                file.close()

    def hot_reload(self) -> None:
        if not check_compile_list():
            print("\n[Redux-py] ERROR: " + COMPILE_LIST + " not found.\n")
            return
        is_running = bool()
        try:
            is_running = self.get_emulation_running_state()
        except Exception:
            print("\n[Redux - Web Server] ERROR: Couldn't start a connection with redux.")
            print("Make sure that redux is running, its web server is active, and")
            print("the port configuration saved in settings.json is correct.\n")
            return
        print("Would you like to backup the RAM?")
        print("1 - Yes")
        print("2 - No")
        print("Note: this option is required if you want to uninstall the mod.")
        print("By selecting yes you'll overwrite the current backup.")
        error_msg = "ERROR: Invalid input. Please enter 1 for Yes or 2 for No."
        backup = request_user_input(first_option=1, last_option=2, error_msg=error_msg) == 1
        self.pause_emulation()
        self.inject(backup, False)
        self.load_map()
        self.flush_cache()
        if is_running:
            self.resume_emulation()
        free_sections()

    def restore(self) -> None:
        if not check_compile_list():
            print("\n[Redux-py] ERROR: " + COMPILE_LIST + " not found.\n")
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
        free_sections()
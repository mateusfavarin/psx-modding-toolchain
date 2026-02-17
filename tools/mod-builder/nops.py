import _files # check_file
from syms import Syms
from compile_list import CompileList, free_sections
from common import COMPILE_LIST, SETTINGS_PATH, BACKUP_FOLDER, get_build_id, request_user_input

import os
import json
import pathlib
import subprocess

class Nops:
    def __init__(self) -> None:
        pass

    def load_config(self) -> None:
        """ TODO: Put in try/except """
        with open(SETTINGS_PATH) as file:
            data = json.load(file)["nops"]
            self.prefix = ["nops", f"/{data['mode'].lower()}"]
            self.comport = [data["comport"].upper()]

    def fire_command(self, list_args):
        """TODO: Put this in logging"""
        command = [self.prefix]
        command.extend(list_args)
        command.append(self.comport)
        result = subprocess.run(command)

    def inject(self, backup: bool, restore: bool) -> None:
        """
        COMPILE_LIST is a string
        """
        sym = Syms(get_build_id())
        build_lists = ["./"]
        while build_lists:
            prefix = build_lists.pop(0)
            bl = prefix + COMPILE_LIST
            free_sections()
            with open(bl, "r") as file:
                for line in file:
                    cl = CompileList(line, sym, prefix)
                    if not cl.should_build() or cl.skip_reload:
                        continue
                    bin = cl.get_output_name()
                    backup_bin = pathlib.Path(prefix) / BACKUP_FOLDER / ("nops_" + cl.section_name + ".bin")
                    if backup:
                        if not _files.check_file(bin):
                            continue
                        size = os.path.getsize(bin)
                        self.fire_command(["/dump", hex(cl.address), hex(size),backup_bin])
                    if restore:
                        bin = backup_bin
                    if not _files.check_file(bin):
                        continue
                    self.fire_command(["/bin", hex(cl.address), bin])

    def hot_reload(self) -> None:
        if not _files.check_file(COMPILE_LIST):
            return
        intro_msg = """
        Would you like to backup the state?
        1 - Yes
        2 - No
        Note: this option is required if you want to uninstall the mod.
        By selecting yes you'll overwrite the current backup.
        """
        error_msg = "ERROR: Invalid input. Please enter 1 for Yes or 2 for No."
        backup = request_user_input(first_option=1, last_option=2, intro_msg=intro_msg, error_msg=error_msg) == 1
        self.fire_command(["/halt"])
        self.inject(backup, False)
        self.fire_command(["/cont"])

    def restore(self) -> None:
        if not _files.check_file(COMPILE_LIST):
            return
        self.fire_command(["/halt"])
        self.inject(False, True)
        self.fire_command(["/cont"])

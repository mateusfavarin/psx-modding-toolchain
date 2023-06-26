"""
Reads in the all the diretories
Does stuff with them
Runs in basically an infinite while loop
TODO: Replace with Click
"""
import _files # check_file, check_files, delete_file, create_directory, delete_directory
from makefile import Makefile, clean_pch
from compile_list import CompileList, free_sections, print_errors
from syms import Syms
from redux import Redux
from common import MOD_NAME, GAME_NAME, LOG_FILE, COMPILE_LIST, DEBUG_FOLDER, BACKUP_FOLDER, OUTPUT_FOLDER, COMPILATION_RESIDUES, TEXTURES_FOLDER, TEXTURES_OUTPUT_FOLDER, RECURSIVE_COMP_PATH, ABORT_PATH, CONFIG_PATH, IS_WINDOWS_OS, request_user_input, cli_clear, cli_pause, rename_psyq_sections, DISC_PATH, SETTINGS_PATH, CONFIG_PATH
from mkpsxiso import Mkpsxiso
from nops import Nops
from game_options import game_options
from image import create_images, clear_images, dump_images
from clut import clear_cluts, dump_cluts
from c import export_as_c

import logging
import os
import pathlib
import subprocess
import sys

logger = logging.getLogger(__name__)

class Main:
    def __init__(self) -> None:
        self.redux = Redux()
        self.mkpsxiso = Mkpsxiso()
        self.nops = Nops()
        self.nops.load_config()
        self.redux.load_config()
        self.actions = {
            1   :   self.compile,
            2   :   self.clean,
            3   :   self.mkpsxiso.extract_iso, # makes it awkward to pass arguments
            4   :   self.mkpsxiso.build_iso,
            5   :   self.mkpsxiso.xdelta,
            6   :   self.mkpsxiso.clean,
            7   :   self.redux.hot_reload,
            8   :   self.redux.restore,
            9   :   self.replace_textures,
            10  :   self.redux.restore_textures,
            11  :   self.redux.start_emulation,
            12  :   self.nops.hot_reload,
            13  :   self.nops.restore,
            14  :   self.clean_pch,
            15  :   self.disasm,
            16  :   export_as_c,
            17  :   rename_psyq_sections,
            18  :   self.clean_all,
            19  :   self.shutdown
        }
        self.num_options = len(self.actions)
        self.window_title = f"{GAME_NAME} - {MOD_NAME}"
        self.python = None
        if IS_WINDOWS_OS:
            self.python = "python"
        else:
            self.python = "python3"
        self.update_title()

    def shutdown(self):
        logger.info("EXITING")
        sys.exit(0)

    def update_title(self):
        """ TODO: Identify these commands """
        if IS_WINDOWS_OS:
            os.system("title " + self.window_title)
        else:
            os.system('echo -n -e "\\033]0;' + self.window_title + '\\007"')

    def get_options(self) -> int:
        intro_msg = (
            "Please select an action:\n\n"
            "Mod:\n"
            "1 - Compile\n"
            "2 - Clean\n\n"
            "Iso:\n"
            "3 - Extract Iso\n"
            "4 - Build Iso\n"
            "5 - Generate xdelta patch\n"
            "6 - Clean Build\n\n"
            "PCSX-Redux:\n"
            "7 - Hot Reload Mod\n"
            "8 - Restore Mod\n"
            "9 - Replace Textures\n"
            "10 - Restore Textures\n"
            "11 - Start Emulation\n\n"
            "NotPSXSerial:\n"
            "12 - Hot Reload\n"
            "13 - Restore\n\n"
            "General:\n"
            "14 - Clean Precompiled Header\n"
            "15 - Disassemble Elf\n"
            "16 - Export textures as C file\n"
            "17 - Rename PSYQ Sections\n"
            "18 - Clean All\n"
            "19 - Quit\n"
        )
        error_msg = "ERROR: Wrong option. Please type a number from 1-" + str(self.num_options) + ".\n"
        return request_user_input(first_option=1, last_option=self.num_options, intro_msg=intro_msg, error_msg=error_msg)

    def abort_compilation(self, root: bool, warning: bool) -> None:
        if warning:
            print("[Compile-py] Aborting ongoing compilations.")
            cli_pause()
        if root:
            _files.delete_file(RECURSIVE_COMP_PATH)
            return
        else:
            with open(ABORT_PATH, "w") as _:
                return

    def compile(self) -> None:
        if ABORT_PATH.exists(): # Shouldn't log ERROR for this one
            return # Abort ongoing compilation chain due to an error that occured
        if not _files.check_file(COMPILE_LIST):
            logger.exception(f"{COMPILE_LIST} not found.")
            return
        root = False
        if not _files.check_file(RECURSIVE_COMP_PATH):
            with open(RECURSIVE_COMP_PATH, "w") as _:
                root = True
        else:
            with open(RECURSIVE_COMP_PATH, "r") as file:
                if MOD_NAME in file.readline().split():
                    return # checking whether the mod was already compiled
        instance_symbols = Syms()
        make = Makefile(instance_symbols.get_build_id(), instance_symbols.get_files())
        dependencies = []
        # parsing compile list
        free_sections()
        with open(COMPILE_LIST, "r") as file:
            for line in file:
                cl = CompileList(line, instance_symbols, "./")
                if cl.is_cl():
                    dependencies.append(cl.bl_path)
                if not cl.should_ignore():
                    make.add_cl(cl)
        if print_errors[0]:
            intro_msg = "[Compile-py] Would you like to continue to compilation process?\n\n1 - Yes\n2 - No\n"
            error_msg = "ERROR: Wrong option. Please type a number from 1-2.\n"
            if request_user_input(first_option=1, last_option=2, intro_msg=intro_msg, error_msg=error_msg) == 2:
                self.abort_compilation(root=root, warning=False)
        if make.build_makefile():
            if make.make():
                with open(RECURSIVE_COMP_PATH, "a") as file:
                    file.write(MOD_NAME + " ")
            else:
                self.abort_compilation(root=root, warning=True)
        else:
            self.abort_compilation(root=root, warning=True)
        curr_dir = pathlib.Path.cwd()
        for dep in dependencies: # Does this matter since we know the full path?
            os.chdir(dep)
            path_module = CONFIG_PATH.parents[1] / "tools" / "mod-builder" / "main.py"
            # use to use get_distance_to_file(False, CONFIG_FILE), same as CONFIG_PATH?
            command = [self.python, str(path_module), "1", instance_symbols.version]
            result = subprocess.call(command) # only returns code
            if result != 0:
                logger.critical("Couldn't run the symbols version")
        os.chdir(curr_dir)
        if root:
            _files.delete_file(RECURSIVE_COMP_PATH)
            _files.delete_file(ABORT_PATH)
            self.update_title()

    def clean(self) -> None:
        """
        TODO: rename method to clean_files for explicit
        """
        _files.delete_directory(DEBUG_FOLDER)
        _files.delete_directory(BACKUP_FOLDER)
        _files.delete_directory(OUTPUT_FOLDER)
        _files.delete_directory(TEXTURES_OUTPUT_FOLDER)
        for file in COMPILATION_RESIDUES:
            _files.delete_file(file)

    def clean_pch(self) -> None:
        clean_pch()

    def clean_all(self) -> None:
        self.mkpsxiso.clean(all=True)
        self.clean()
        self.clean_pch()

    def replace_textures(self) -> None:
        _files.create_directory(TEXTURES_OUTPUT_FOLDER)
        img_count = create_images(TEXTURES_FOLDER)
        if img_count == 0:
            print("\n[Image-py] WARNING: 0 images found. No textures were replaced.\n")
            return
        dump_images(TEXTURES_OUTPUT_FOLDER)
        dump_cluts(TEXTURES_OUTPUT_FOLDER)
        self.redux.replace_textures()
        clear_images()
        clear_cluts()

    def disasm(self) -> None:
        path_in = DEBUG_FOLDER / 'mod.elf'
        path_out = DEBUG_FOLDER / 'disasm.txt'
        with open(path_out, "w") as file:
            command = ["mipsel-none-elf-objdump", "-d", str(path_in)]
            result = subprocess.call(command, stdout=file, stderr=subprocess.STDOUT)
            if result.returncode != 0:
                logger.critical("Disassembly failed")
        logger.info(f"Disassembly saved at {path_out}")

    def exec(self):
        while not _files.check_files([COMPILE_LIST, DISC_PATH, SETTINGS_PATH]):
            cli_pause()
        game_options.load_config()
        while True:
            cli_clear()
            i = self.get_options()
            self.actions[i]()
            cli_pause()

if __name__ == "__main__":
    try:
        main = Main()
        main.exec()
    except Exception as e:
        _files.delete_file(RECURSIVE_COMP_PATH)
        _files.delete_file(ABORT_PATH)
        logging.basicConfig(filename=LOG_FILE, filemode="w", format='%(levelname)s:%(message)s')
        logging.exception(e)
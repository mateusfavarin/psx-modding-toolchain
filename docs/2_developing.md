# Developing
This page is dedicated for developers looking for using the tool to build mods. It includes every bit of information needed in order to set up a new game from scratch, and start writing code for it. Remember: you can always look at the folders `Example_CrashTeamRacing` , `Example_SpyroRiptosRage` and `Example_MegaManX4` in order to check an up-to-date working environment.

Note: when writing addresses for the PSX, always use the prefix 0x80 (KSEG0)

## Setting up a new game
Modify the JSON file in `games/startup_game.json` and then run `STARTUP.BAT` (or `STARTUP.SH` if you're on linux/macos). Don't worry if you miss something in the configuration - you can add modify your game environment manually as described in the following sections.

### games/startup_game.json
JSON file used to automatically start a new game environment.
```
game_name: str # The script will use the name you set here as the name of the folder/game environment.
symbols: list[str] # List of custom symbol files that will be fed to the linker.
versions: list of versions that your game environment will support. They're structured as:
    "your_version_name":
            "build_id": int
            "game_path": str # Path to the copy of your game
    # Further discussed in the section about the structure of the file games/game_name/config.json
compiler: compiler settings # Further discussed in the section about the structure of the file games/game_name/config.json
```

## Configuring the environment
This section discusses in detail how each file of the environment works, so you can adapt them for your needs.

### games/setting.json
This file describes general settings about the environment, which applies to all games.
```
redux:
    port: int # Your redux web server port
nops:
    comport: str # Your serial comport
    mode: str # Mode selected to run NoPS at. Currently supports fast and slow.
```

### games/game_name/config.json
This file describes game specific settings, such as game versions and compiler configurations.

```
version: list # List of versions that your game environment support. You can give any name for the versions.
    [
        {
            yourVersion:
                name: str # Name of the ISO that the tool will look for in the games/game_name/build/ folder
                symbols: list # List of linker symbol files that the tool will look for when compiling for this version of the game
                [
                    yourSymbolFile: str # filename. This file must be in the games/game_name/symbols/ folder
                    ...
                ]
                build_id: int # unique ID for this version. This will be used during compilation time to create the variable BUILD, which will have the value of build_id (-DBUILD=build_id).
        }
        ...
    ]
compiler:
    function_sections: int # 0 or 1. When 1, the flag -ffunction-sections will be set during compilation time.
    reorder_functions: int # 0 or 1. When 0, the flag -fno-toplevel-reorder will be set during compilation time.
    optimization: int # Compiler optization flags. 0 = -O0, 1 = -O1, 2 = -O2, 3 = -O3, 4 = -Os, 5+ = -Oz
    debug: int # 0 or 1. When 1, the flag -g will be set during compilation time.
    psyq: int # 0 or 1. When 1, the files at tools/gcc-psyq-converted/ will be included/linked in the compilation/linking process.
    8mb: int # 0 or 1. This configuration only affects the boundary check when compiling your mod.
    pch: str # OPTIONAL. Name of your precompiled header. Header must be located in the include/ folder.
    ccflags: str # OPTIONAL. Optional flags to feed the compiler with.
    ldflags: str # OPTIONAL. Optional flags to feed the linker with.
```
Note: `common` is a reserved name and shouldn't be used to name any of your custom versions.
Note: this project supports gcc precompiled headers. To learn more about it, read [here](https://gcc.gnu.org/onlinedocs/gcc/Precompiled-Headers.html)

### games/game_name/disc.json
This file should contain a description of the ISO structure of your game for each game version. The version names should be same ones that you defined in `games/game_name/config.json`.
```
common: list # Container for files that are the same in all versions of your game
    [
        {
            file1: list # list of sections which may correspond to one or more executables in the same file
            [
                {
                    name: str # alias of the file, which will be used as a look-up during the iso building process.
                    address: str # address that this section of the file is loaded at in the PSX RAM.
                    offset: str # file offset indicating where this section starts in the file
                }
                ...
            ]
        }
        ...
    ]
version1: list # Container for a specific version of the game. The name of version must be the same specified in games/game_name/config.json
    [
        ...
    ]
```

### games/game_name/include/
This is a folder which the compiler will always look at for include files. This is where your files describing the memory map of your game should go.

### games/game_name/plugins/plugin.py
During the iso building process, the program will call the `extract` and `build` functions from this `plugin.py` file. This allows the user to write custom code in order to handle automatically building custom game archives. See the `PluginExample` mod in the `Example_CrashTeamRacing` folder as a reference.

### games/game_name/mods/mod/buildList.txt
This file should contain a description of how to compile and build your mod. Each line in the file will correspond to one different binary compiled. Each line has different fields, which are separated using the `,` token. Comments are supported using the `//` token.

A general line looks like this:
```
version, section, address, offset, path, binary name [optional]
```

Fields:
```
version: set this to one of your versions defined in config.json, or use the special word "common" to apply to all versions. This line will only be compiled if it matches the version you selected to compile.
you can also specify 'noreload' after the version to skip reloading the code while using the hot-reload feature or 
'nofile' to specify that section should not be added as new file (this only works for sections that dont already exists in `disc.json` ) .
section: name of the section defined in disc.json which will be used to overwrite the data in the disc. You can leave this section empty if you want to add a new file to the disc.
address: address which the binary will be compiled to. It can either be a decimal number, a hexadecimal number, or a symbol.
offset: an offset which will be applied to the address. This field can be any valid python arithmetic expression.
path: path to the file you want to compile. If you want to compile multiple files into the same binary, separate each path with a space. e.g "src/file1.c src/file2.c ..."
binary name: optional field. Specifies the final name of the binary. If not specified, the name of the binary will be the name of the first file specified in the "path" field.
```

Note: if you want to add assets in your mod, rename their extension to `.bin` and add them to the `buildList.txt`. This will ensure that the file will be used when hot-reloading and building the iso, but it won't be fed to the compiler.

### games/game_name/mods/mod/fileList.txt
This is an `optional` file should contain the description on witch files you want to be added to the build disc process.
A line should look like this:

```
version, sourceFile , destFile [optional]
```

The `version` does the same thing as the version in buildList.txt. The `sourceFile` is the path to the file you wish to be added to
the build disc process. The `destFile` is the file (that already exists in the game) that you wish to be replaced. Optionally you could ignore the `destFile` argument and it will instead be placed at the end of the disc instead of replacing an already existing game file

### define.mk
This is an `optional` make file that be included in the directory of your mod that will be `-included` by the dynamicly generated
makefile at mod compolation. Useful if you want to include mod specfic linker scripts or setup compile rules for specfic files.

### games/game_name/mods/mod/newtex/
Place here any image png that you want to inject in game. The image name must be in the following format: `name_x_y_clutx_cluty_width_height_bpp`.

Note: `clutx` is in 16 half steps, i.e one unit corresponds to 16 pixels.

### tools/gcc-psyq-converted
If you own a copy of PSYQ, you can use it in this modding toolchain by converting them using [Nicolas Noble's psyq-obj-parser](https://github.com/grumpycoders/pcsx-redux/blob/main/src/mips/psyq/README.md), then copying the headers in the `tools/gcc-psyq-converted/include/` folder, and the libs in the `tools/gcc-psyq-convered/lib/` folder.

Note: the psyq functions will be compiled to the last c file described in `buildList.txt`.
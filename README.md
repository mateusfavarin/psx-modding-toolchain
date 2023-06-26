# PSX Modding Toolchain
The goal of this project is to provide a set of tools for PSX developers in order to make modding and reverse engineering games easier, while using modern non-proprietary software.

Watch the demo:
[![video](https://imgur.com/Mdqs9JH.jpg)](https://www.youtube.com/watch?v=-AE4QKrx5uY)

## Features
* Compile, playtest and build an ISO in just a few clicks;
* Compile C code into multiple overlays, targetting any PSX RAM address;
* Test your changes in game during runtime;
* Replace game textures using custom images;
* Automatic rebuild a PSX iso with your own modifications.
* Generate xdelta patches to easily distribute your ROM hacks. You can apply xdelta patches using this [web application](https://kotcrab.github.io/xdelta-wasm/)

To discuss PSX development, hacking, and reverse engineering in general, please join the PSXDev Network Discord server: [![Discord](https://img.shields.io/discord/642647820683444236)](https://discord.gg/QByKPpH)

## Setup

## Prerequisites
```
python3.7+
python-pip
```
Note: some python installations might be incomplete. Make sure that you have installed `python`, `pip` and add them to your `PATH`.

To compile the GCC mipsel toolchain (incomplete)
```
make
libgl1 with GLIBC_2.35 # if using prebuilt
```

## Setup

### Clone this repository:
```
$ git clone https://github.com/mateusfavarin/psx-modding-toolchain.git
```

### python dependencies
Install the python dependencies from the command line
```
$ pip install --upgrade pip setuptools wheel
$ pip install -r requirements.txt
```
Note: don't use whitespaces in the folder names. This will break the `make` script.
TODO: Verify this is still the case

### gcc-mipsel-none-elf toolchain:

##### Windows:
Run the following command in a terminal like cmd or powershell
```
$ powershell -c "& { iwr -UseBasicParsing https://raw.githubusercontent.com/grumpycoders/pcsx-redux/main/mips.ps1 | iex }"
```
In a new terminal, run the following
```
mips install 13.1.0
```

OR pre-built installations are found at
- https://static.grumpycoder.net/pixel/mips/g++-mipsel-none-elf-13.1.0.zip
- https://www.github.com/Lameguy64/PSn00bSDK/releases/latest

Extract the folder, e.g. `g++-mipsel-none-elf`
Then add both of these folders to your `PATH`
```
g++-mipsel-none-elf/bin
g++-mipsel-none-elf/mipsel-non-elf/bin
```

#### Linux

You can compile the necessary gcc && mipsel-none-elf from source using [this script](https://github.com/grumpycoders/pcsx-redux/tree/main/tools/linux-mips). It takes a few hours.

OR you can find pre-built binaries here 
- https://www.github.com/Lameguy64/PSn00bSDK/releases/latest

The `install_toolchain_prebuilt.sh` extracts them to /opt/gcc-mipsel-none-elf/ (you may need sudo access). You just need to add them to your PATH
```
export PATH="$PATH:/opt/gcc-mipsel-none-elf/bin"
export PATH="$PATH:/opt/gcc-mipsel-none-elf/mipsel-none-elf/bin"
```
Note: This isn't permanent and only works in a single terminal at a time.

OR you can run the dockerfile (EXPERIMENTAL) from the root of this directory
```
docker build -t psx-modding .
docker run -d -t psx-modding
```

##### MacOS
You'll need [brew](https://brew.sh/), and then run:
```
brew install ./tools/macos-mips/mipsel-none-elf-binutils.rb
brew install ./tools/macos-mips/mipsel-none-elf-gcc.rb
```

#### PCSX-Redux
PCSX-Redux is a PSX emulator heavily focused on development, debuggability, and reverse engineering. This project uses Redux's web server in order to connect the PSX modding toolchain to the emulator, allowing the developer to seamlessly hot-reload code while playing the game and update the emulator debugger symbols during runtime.

In order to setup the emulator, you'll need to download [PCSX-Redux](https://github.com/grumpycoders/pcsx-redux/#where) and change the following settings under the `configuration/emulation` tab:

```
[ ] Dynarec CPU # Leave this unchecked
[ ] 8MB # Optional
[x] Enable Debugger
[x] Enable GDB Server
[x] Enable Web Server
```

#### NoPS
NotPSXSerial, or NoPS for short, is a Serial/TTY suite for Unirom 8 featuring kernel-resident debugging, cart/EEPROM flasher, .exe/.elf upload, memcard tools, peeks, pokes, dumps and bugs. This project is integrates NoPS in order to hot-reload code directly in your PS1.

You can download the latest release of Unirom [here](https://github.com/JonathanDotCel/unirom8_bootdisc_and_firmware_for_ps1/releases), and then set the NoPS folder to your `PATH`.

#### Usage
Check the [docs](docs/) for information about configuring and using the tools.

If you're interested in decompiling a game, you might be interested in checking out [this](games/Example_CrashTeamRacing/mods/DecompUnitTester/README.md) real time function unit tester.

## Testing
We use pytest for testing
```
cd /tools/mod-builder
python -m pytest
```
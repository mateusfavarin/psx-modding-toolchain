#ifndef COMMON_H
#define COMMON_H

#define NTSC_U 926
#define PAL 1020
#define NTSC_J 1111

enum gameModes {
    BATTLE_MODE         = 0x20,
    RACE_INTRO_CUTSCENE = 0x40,
    WARPBALL_HELD       = 0x1000,
    MAIN_MENU           = 0x2000,
    TIME_TRIAL          = 0x20000,
    ADVENTURE_MODE      = 0x80000,
    ADVENTURE_HUB       = 0x100000,
    RACE_OUTRO_CUTSCENE = 0x200000,
    ARCADE_MODE         = 0x400000,
    ROLLING_ITEM        = 0x800000,
    CRYSTAL_CHALLENGE   = 0x8000000,
    ADVENTURE_CUP       = 0x10000000,
    GAME_INTRO          = 0x20000000,
    LOADING             = 0x40000000,
    ADVENTURE_BOSS      = 0x80000000
};

enum RawButtons
{
	RAW_BTN_SELECT = 0x1,
	RAW_BTN_START = 0x8,
	RAW_BTN_UP = 0x10,
	RAW_BTN_RIGHT = 0x20,
	RAW_BTN_DOWN = 0x40,
	RAW_BTN_LEFT = 0x80,
	RAW_BTN_L2 = 0x100,
	RAW_BTN_R2 = 0x200,
	RAW_BTN_L1 = 0x400,
	RAW_BTN_R1 = 0x800,
	RAW_BTN_TRIANGLE = 0x1000,
	RAW_BTN_CIRCLE = 0x2000,
	RAW_BTN_CROSS = 0x4000,
	RAW_BTN_SQUARE = 0x8000,
    RAW_BTN_COUNT = 14
};

struct GamepadBuffer
{
	char unk[0x20]; // 0x0
	unsigned short * rawController; // 0x20
    char unk2[0x2C]; // 0x24
};

struct GamepadSystem
{
    struct GamepadBuffer gamepadBuffer[8]; // 0x0
};

void DrawText(char * text, int x, int y, int size, int color);

// 0x8008D2AC - NTSC-U
// 0x8008D644 - PAL
// 0x800906B8 - NTSC-J
extern unsigned int gameMode;
extern struct GamepadSystem * gamepadSystem;

#endif
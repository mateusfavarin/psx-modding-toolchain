#ifndef LAYER_H
#define LAYER_H
#include <sys/types.h>
#include <stdbool.h>

typedef unsigned char   undefined;
typedef unsigned char    byte;
typedef unsigned int    dword;
typedef char    sbyte;
typedef unsigned char    undefined1;
typedef unsigned short    undefined2;
typedef unsigned int    undefined4;
typedef unsigned short    word;

void AssignLayer(int layer);

void DefaultLayers();
void DrawLayer(int layer);
void DumpActiveScreens();
void DumpLayerScreens(int layer); //BG1-3

void LoadTiles(int id,short x,short y);
void LoadTiles2(int id,short x,short y); //Not Permanet

void ResetLayerPointers(int layer);

typedef struct{
    int layer;
    ushort settings; // tttt ttti , T = TileCount I = Increament-X (if 1 Increament-X instead of Y)
    ushort destX;
    ushort destY;
    ushort pad;
    u_char*tableP;
    int proceed;
} tilesetStruct;

typedef struct {
    undefined field0_0x0;
    undefined field1_0x1;
    undefined field2_0x2;
    bool display;
    char type;
    undefined field5_0x5;
    undefined field6_0x6;
    undefined field7_0x7;
    undefined field8_0x8;
    undefined field9_0x9;
    short x;
    undefined field11_0xc;
    undefined field12_0xd;
    short y;
    undefined field14_0x10;
    undefined field15_0x11;
    undefined field16_0x12;
    undefined field17_0x13;
    undefined field18_0x14;
    undefined field19_0x15;
    short pastX;
    undefined field21_0x18;
    undefined field22_0x19;
    short pastY;
    short pastBorderR;
    short pastBorderL;
    short pastBorderB;
    short pastBorderT;
    short borderR;
    short borderL;
    short borderB;
    short borderT;
    undefined field32_0x2c;
    undefined field33_0x2d;
    undefined field34_0x2e;
    undefined field35_0x2f;
    undefined field36_0x30;
    undefined field37_0x31;
    undefined field38_0x32;
    undefined field39_0x33;
    undefined field40_0x34;
    undefined field41_0x35;
    undefined field42_0x36;
    undefined field43_0x37;
    undefined field44_0x38;
    undefined field45_0x39;
    undefined field46_0x3a;
    undefined field47_0x3b;
    undefined field48_0x3c;
    undefined field49_0x3d;
    undefined field50_0x3e;
    undefined field51_0x3f;
    short baseX;
    short baseY;
    bool enabled;
    undefined field55_0x45;
    undefined field56_0x46;
    undefined field57_0x47;
    undefined field58_0x48;
    undefined field59_0x49;
    byte normalOT;
    byte priorityOT;
    bool update;
    undefined field63_0x4d;
    undefined field64_0x4e;
    undefined field65_0x4f;
    undefined field66_0x50;
    undefined field67_0x51;
    undefined field68_0x52;
    undefined field69_0x53;
} Layer;

extern Layer bgLayers[3];

extern u_char layoutWidth;
extern u_char layoutHeight;
extern u_char layoutSize;
#endif
#ifndef COMMON_H
#define COMMON_H
#include <sys/types.h>
#include <stdbool.h>
#include <object.h>

#define WriteShort(addr, value) (*(short*)(addr) = (value))
#define WriteInt(addr, value) (*(int*)(addr) = (value))
#define WriteByte(addr, value) (*(char*)(addr) = (value))

enum PadButtons{
    PAD_L1 = 4,
    PAD_R1 = 8,
    PAD_L2 = 1,
    PAD_R2 = 2,
    PAD_SELECT = 0x100,
    PAD_START = 0x800,
    PAD_UP = 0x1000,
    PAD_RIGHT = 0x2000,
    PAD_DOWN = 0x4000,
    PAD_LEFT = 0x8000,
    PAD_TRIANGLE = 0x10,
    PAD_CIRCLE = 0x20,
    PAD_CROSS = 0x40,
    PAD_SQUARE = 0x80
};

extern ushort buttonsHeld;
extern ushort buttonsPressed;
extern u_char cursor;
extern char fadeDirection; //0 = done
extern int frameCount;
extern void * freeArcP;

typedef struct {
    byte mode;
    byte mode2;
    byte mode3;
    byte mode4;
    undefined field4_0x4;
    undefined field5_0x5;
    undefined field6_0x6;
    undefined field7_0x7;
    undefined field8_0x8;
    undefined field9_0x9;
    undefined field10_0xa;
    undefined field11_0xb;
    byte stageid;
    byte mid;
    byte movie;
    byte clear;
    bool rideArmorEnable; /* AI */
    bool disableWepaonObjects;
    bool disableMainObjects;
    bool disableShotObjects;
    bool disableVisualObjects;
    bool disableEffectObjects;
    bool disableItemObjects;
    bool disableMiscObjects;
    bool disableQuadObjects;
    bool disableForeObjects;
    undefined field26_0x1a;
    undefined field27_0x1b;
    undefined field28_0x1c;
    char point;
    byte specialStart;
    bool enableBars;
    struct objStruct * bossP;
    bool enableBossBar;
    byte bossBarType;
    undefined field35_0x26;
    undefined field36_0x27;
    undefined field37_0x28;
    undefined field38_0x29;
    undefined field39_0x2a;
    undefined field40_0x2b;
    undefined field41_0x2c;
    undefined field42_0x2d;
    byte seenTextFlag; /* so that you dont see the boss dialog twice */
    undefined field44_0x2f;
    undefined field45_0x30;
    undefined field46_0x31;
    undefined field47_0x32;
    undefined field48_0x33;
    undefined field49_0x34;
    undefined field50_0x35;
    undefined field51_0x36;
    byte cheatCodeFlag; /* Ultimate Armor/Black Zero */
    undefined field53_0x38;
    undefined field54_0x39;
    undefined field55_0x3a;
    undefined field56_0x3b;
    undefined field57_0x3c;
    undefined field58_0x3d;
    undefined field59_0x3e;
    undefined field60_0x3f;
    byte sceneFlags; /* for X/Zero/Double/Iris */
    undefined field62_0x41;
    undefined field63_0x42;
    char player;
    byte lives;
    byte currentMaxHP;
    byte maxHP;
    byte armorParts;
    byte busterType;
    undefined field70_0x49;
    undefined field71_0x4a;
    undefined field72_0x4b;
    undefined field73_0x4c;
    undefined field74_0x4d;
    undefined field75_0x4e;
    undefined field76_0x4f;
    undefined field77_0x50;
    undefined field78_0x51;
    undefined field79_0x52;
    undefined field80_0x53;
    undefined field81_0x54;
    undefined field82_0x55;
    undefined field83_0x56;
    undefined field84_0x57;
    undefined field85_0x58;
    byte clearedStages;
    ushort collectables; /* hearts , tanks , 1UP thing */
    byte tanksAmmo[3]; /* 2 sub tanks then the w tanks */
    byte startMode;
    undefined field90_0x60;
    undefined field91_0x61;
    undefined field92_0x62;
    undefined field93_0x63;
}Game;

extern Game game;

void ArcSeek(ushort id,u_char bufferId,void * bufferP);
void BinSeek(ushort id,void * dest);
void ClearAll(void);
void DrawLoad(bool showName ,bool fade);
void DrawMain();
void DrawMMX4(void);
void EndSong(void);

void FadeIn(u_char speed);
void FadeOut(u_char speed);
void FileCollect();

void PlaySound(int slot,int id,Object *objP);
void PlaySong(byte id,byte vol);

char * strcpy(void * dest,void * src);
void * memcpy(void *dest, void *src,int length);
void * memset(void *dest, char *fillbyte,int length);

int printf(const char *fmt,...);

void SpawnText(ushort id,byte idk,byte flag);

void NewThread(int id,void * func);
void ThreadSleep(ushort frames);
void DeleteThread();
void DeleteThread2(int id);
void NewThread2(void * func);
#endif
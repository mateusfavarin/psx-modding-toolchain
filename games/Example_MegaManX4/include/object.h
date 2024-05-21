#ifndef OBJECT_H
#define OBJECT_H
#include <sys/types.h>
#include <stdbool.h>
typedef unsigned char   undefined;
typedef unsigned char    byte;

typedef struct
{
    char offsetX;
    char offsetY;
    u_char width;
    u_char height;
}hitboxS;


typedef struct {
    byte timer;
    byte flag;
    char nextIndex; /* multiples of 4 */
    byte sprtFrame;
}AnimeFrame;

typedef struct {
    byte spawned;
    byte Id;
    byte var;
    byte type;
    ushort X;
    ushort Y;
}Enemy;

typedef struct {
    byte flags; /* alive */
    byte id;
    byte stageVar;
    bool display;
    byte act;
    byte act2;
    byte act3;
    byte act4;
    int x;
    int y;
    Enemy * enemyP; /* for enemy spawner & other things */
    byte collideLayer; /* witch BG Layer for collision */
    byte flip;
    byte priority;
    byte anime;
    int pastX;
    int pastY;
    int speedX;
    int speedY;
    int accelX;
    int accelY;
    AnimeFrame * animeTableP;
    byte * frameP;
    byte * texP;
    byte * sprtDataP;
    ushort texCord;
    ushort clutCord;
    AnimeFrame animeInfo;
    byte newAnimeF;
    undefined field29_0x49;
    undefined field30_0x4a;
    undefined field31_0x4b;
    undefined field32_0x4c;
    undefined field33_0x4d;
    undefined field34_0x4e;
    undefined field35_0x4f;
    hitboxS * contactP; /* hitbox pointer for ContactO */
    hitboxS * contactP2; /* with other things that damage it */
    int * damageTableP; /* damage table Pointer (when hit) */
    byte hp;
    byte hp_old;
    undefined field41_0x5e;
    undefined field42_0x5f;
    byte damage;
    byte iframes;
    undefined field45_0x62;
    undefined field46_0x63;
    undefined field47_0x64;
    undefined field48_0x65;
    undefined field49_0x66;
    undefined field50_0x67;
    hitboxS * collideP; /* for collison & hitbox */
    ushort innerX;
    ushort innerY;
    byte collideF; /* flags for BTLR */
    undefined field55_0x71;
    undefined field56_0x72;
    undefined field57_0x73;
    undefined field58_0x74;
    undefined field59_0x75;
    undefined field60_0x76;
    undefined field61_0x77;
    undefined field62_0x78;
    undefined field63_0x79;
    byte hitboxDisableF; /* for Contact Weapon */
    undefined field65_0x7b;
    undefined field66_0x7c;
    undefined field67_0x7d;
    undefined field68_0x7e; //Start of Free Vars (does not include Weapons)
    undefined field69_0x7f;
    undefined field70_0x80;
    undefined field71_0x84;
    undefined field72_0x85;
    undefined field73_0x86;
    undefined field74_0x87;
    undefined field75_0x88;
    undefined field76_0x89;
    undefined field77_0x8A;
    undefined field78_0x8b;
    undefined field79_0x8c;
    undefined field80_0x8d;
    undefined field81_0x8e;
    undefined field82_0x8f;
    undefined field83_0x90;
    undefined field84_0x91;
    undefined field85_0x92;
    undefined field86_0x93;
    undefined field87_0x94;
    undefined field88_0x95;
    undefined field89_0x96;
    undefined field90_0x97;
    undefined field91_0x98;
    undefined field92_0x99;
    undefined field93_0x9a;
    undefined field94_0x9b;
}Object;

typedef struct {
    byte flags;
    undefined field1_0x1;
    byte player;
    bool display;
    byte status;
    byte state;
    byte sub;
    undefined field7_0x7;
    int x;
    int y;
    undefined field10_0x10;
    undefined field11_0x11;
    undefined field12_0x12;
    undefined field13_0x13;
    byte collideLayer;
    byte flip;
    byte priority;
    byte anime;
    int pastX;
    int pastY;
    int speedX;
    int speedY;
    int accelX;
    int accelY;
    AnimeFrame * animeTableP;
    AnimeFrame * frameP;
    byte * megaTexP;
    byte * sprtDataP;
    ushort texCord;
    ushort clutCord;
    AnimeFrame animeInfo;
    undefined field31_0x48;
    undefined field32_0x49;
    undefined field33_0x4a;
    undefined field34_0x4b;
    undefined field35_0x4c;
    undefined field36_0x4d;
    undefined field37_0x4e;
    undefined field38_0x4f;
    undefined field39_0x50;
    undefined field40_0x51;
    undefined field41_0x52;
    undefined field42_0x53;
    undefined field43_0x54;
    undefined field44_0x55;
    undefined field45_0x56;
    undefined field46_0x57;
    undefined field47_0x58;
    undefined field48_0x59;
    undefined field49_0x5a;
    undefined field50_0x5b;
    byte hp;
    byte hpPast;
    byte maxHP;
    undefined field54_0x5f;
    byte damage; /* with Mega */
    byte iframes; /* well doesnt have to be */
    undefined field57_0x62;
    undefined field58_0x63;
    undefined field59_0x64;
    undefined field60_0x65;
    undefined field61_0x66;
    undefined field62_0x67;
    struct hitboxS * collideP;
    ushort innerX;
    ushort innerY;
    byte collideF;
    undefined field67_0x71;
    undefined field68_0x72;
    undefined field69_0x73;
    undefined field70_0x74;
    undefined field71_0x75;
    undefined field72_0x76;
    undefined field73_0x77;
    undefined field74_0x78;
    undefined field75_0x79;
    undefined field76_0x7a;
    undefined field77_0x7b;
    ushort held;
    ushort heldPast;
    ushort pressed;
    undefined field81_0x82;
    undefined field82_0x83;
    undefined field83_0x84;
    undefined field84_0x85;
    undefined field85_0x86;
    bool doubleDashFlag;
    undefined field87_0x88;
    undefined field88_0x89;
    undefined field89_0x8a;
    undefined field90_0x8b;
    undefined field91_0x8c;
    undefined field92_0x8d;
    undefined field93_0x8e;
    undefined field94_0x8f;
    undefined field95_0x90;
    undefined field96_0x91;
    undefined field97_0x92;
    byte weapon;
    byte weaponOld;
    undefined field100_0x95;
    undefined field101_0x96;
    undefined field102_0x97;
    undefined field103_0x98;
    undefined field104_0x99;
    undefined field105_0x9a;
    byte glowFlag; /* 1 = Blue , 2 = Pink */
    undefined field107_0x9c;
    byte chargeTimer;
    undefined field109_0x9e;
    undefined field110_0x9f;
    undefined field111_0xa0;
    undefined field112_0xa1;
    undefined field113_0xa2;
    undefined field114_0xa3;
    undefined field115_0xa4;
    undefined field116_0xa5;
    byte multiShotCount;
    byte armorParts;
    byte ammo[16];
    byte busterType;
    byte aquiredWeapons;
    undefined field122_0xba;
    undefined field123_0xbb;
    undefined field124_0xbc;
    undefined field125_0xbd;
    char spawnTimer; /* collison timer */
    undefined field127_0xbf;
    bool lock;
    byte lockType;
    byte lockFlip;
    undefined field131_0xc3;
    undefined field132_0xc4;
    byte rideArmorFlag;
    undefined field134_0xc6;
    undefined field135_0xc7;
    undefined field136_0xc8;
    undefined field137_0xc9;
    undefined field138_0xca;
    undefined field139_0xcb;
    undefined field140_0xcc;
    undefined field141_0xcd;
    undefined field142_0xce;
    undefined field143_0xcf;
    undefined field144_0xd0;
    undefined field145_0xd1;
    undefined field146_0xd2;
    undefined field147_0xd3;
    undefined field148_0xd4;
    undefined field149_0xd5;
    undefined field150_0xd6;
    undefined field151_0xd7;
    undefined field152_0xd8;
    undefined field153_0xd9;
    undefined field154_0xda;
    undefined field155_0xdb;
    undefined field156_0xdc;
    undefined field157_0xdd;
    bool enableControls;
    undefined field159_0xdf;
    undefined field160_0xe0;
    undefined field161_0xe1;
    undefined field162_0xe2;
    undefined field163_0xe3;
    undefined field164_0xe4;
    undefined field165_0xe5;
} Mega;

extern Mega mega;
#define megaX *(ushort*)((int)&mega.x + 2)
#define megaY *(ushort*)((int)&mega.y + 2)

/*Define Functions*/
void AnimeAdvance(Object *objP);

void CollideCheck(Object *objP);
int ContactMega(Object *objP);
bool ContactObject();
bool ContactObject2(); //uses collide property
int ContactWeapon(Object *objP); //returns 0 if no-contact , -1 if dead , id + 1 if contact

void DeleteObject(Object *objP); //clears spawn flag
void DeleteObject2(Object *objP); //sets spawn flag
void DeleteObject3(Object *objP);
void DisplayObject(Object *objP);
void DisplayObject2(Object *objP, short width, short height);
void DisplayObject3(Object *objP);

Object* GetEffectObject();
Object* GetItemObject();
Object* GetMainObject();
Object* GetMiscObject();
int GetRNG();
Object* GetShotObject();
Object* GetVisualObject();

void LockMega(byte lockType, byte flip);

void MoveObject(Object *objP);
void MoveObject2(Object *objP);

bool OffScreenCheck(Object* objP);
bool OffScreenCheck2(Object* objP, short rangeX, short rangeY);

bool PlayBossSong(); //returns 0 when started

void SetAnime(Object *objP, int anime);
void SetAnimeFrame(Object *objP, int anime, int frame);
void SpawnExplosion(Object *objP);
void SpawnJunk(byte junkCount, void *idk, Object *objP);

void UnlockMega();
#endif

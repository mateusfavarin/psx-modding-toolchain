#ifndef GPU_H
#define GPU_H
#include <sys/types.h>
#include <libgte.h>
#include <libgpu.h>
#define GetTPageValue(tp,abr,x,y) (tp << 7) + (abr << 5) + x + (y << 4) //Use w/ SetDrawTPage()
#define GetClutCord(id) (ushort)((id & 0xF) + ((id & 0xF0) << 2) + 0x7800) //Base is X:0 Y:480

void AddPrim(void *ot,void *p);
void AddPrims(void *ot,void *p0,void *p1);
void CatPrim(void *p0,void *p1);

u_long *ClearOTagR(u_long *ot, int n);

void DrawOTag(u_long *p);
int DrawSync(int mode);

int VSync(int mode);

int ClearImage(RECT *rect,u_char  r,u_char g,u_char b);
int ClearImage2(RECT *rect,u_char  r,u_char g,u_char b);
u_long *ClearOTag(u_long *ot, int n);
int LoadImage(RECT *rect,u_long *p);
int StoreImage(RECT *rect,u_long *p);
int MoveImage(RECT * rect,int x,int y);

DISPENV *PutDispEnv(DISPENV *env);
DRAWENV *PutDrawEnv(DRAWENV *env);

DISPENV * SetDefDispEnv(DISPENV *env,int x,int y,int w,int h);
DRAWENV * SetDefDrawEnv(DRAWENV *env,int x,int y,int w,int h);

void SetPolyF4(POLY_F4 *p);
void SetPolyFT4(POLY_FT4 *p);
void SetPolyGT3(POLY_GT3 *p);
void SetPolyG4(POLY_G4 *p);
void SetPolyGT4(POLY_GT4 *p);
void SetSemiTrans(void *p,int abe);
void SetSprt8(SPRT_8 *p);
void SetSprt16(SPRT_16 *p);
void SetSprt(SPRT *p);
void SetTile1(TILE_1 * p);
void SetTile8(TILE_8 * p);
void SetTile16(TILE_16 * p);
void SetTile(TILE * p);
void SetLineF2(LINE_F2 * p);
void SetLineG2(LINE_G2 * p);
void SetLineF3(LINE_F3 * p);
void SetLineG3(LINE_G3 * p);
void SetLineF4(LINE_F4 * p);
void SetLineG4(LINE_G4 * p);
void SetDrawTPage(DR_TPAGE *p,int dfe,int dtd,int tpage);

extern u_char buffer;
typedef struct{
    DISPENV disp;
    DRAWENV draw;
    ulong ot[12];
}DB;
extern DB * drawP;
extern DB drawSettings[2];

extern SPRT_16 rectBuffer[2][1024];
extern int rectCount;

extern int primP;
extern int primCount;

extern int tempPrimP;
#endif

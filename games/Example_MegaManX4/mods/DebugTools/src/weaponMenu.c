#include <common.h>
#include <gpu.h>

#if BUILD == 561
#define menuTPage ((DR_TPAGE *)0x80139580)
#else
#define menuTPage ((DR_TPAGE *)0x801396a0)
#endif

void DrawWeaponMenuBackground()
{
    SetDrawTPage(&menuTPage[buffer], 0, 0, GetTPageValue(0, 0, 13, 1));
    AddPrim(&drawP->ot[10], &menuTPage[buffer]);

    volatile ushort *menuScreenP = ((int *)0x1f800034)[0];
    volatile SPRT_16 *rect = &rectBuffer[buffer];
    int count = 0;
    int baseX = 0;

    for (size_t s = 0; s < 2; s++)
    {
        baseX = s * 256;
        for (size_t y = 0; y < 16; y++)
        {
            for (size_t x = 0; x < 16; x++)
            {
                short drawX = x * 16 + baseX;
                short drawY = y * 16;
                if (drawX < 320)
                {
                    ushort val = *menuScreenP;
                    rect->code = 0x7D;
                    *(char *)((int)&rect->tag + 3) = 3;
                    setXY0(rect, drawX, drawY);
                    setUV0(rect, ((val & 0xF) << 4), (val & 0xF0));
                    rect->clut = val >> 0xC | 0x7900;
                    AddPrim(&menuTPage[buffer], rect);
                    rect++;
                }
                menuScreenP++;
            }
        }
    }

    /********/
}
#undef menuTPage
#undef rectBufferAddress
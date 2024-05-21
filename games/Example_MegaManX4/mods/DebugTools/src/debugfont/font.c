/*
 * Written by PogChampGuy AKA Kuumba (https://www.twitch.tv/kuumba_)
 *
 * this mod Loads in the ASCII texture + clut located in
 * FONT8X8.ARC for easy way to drawing text to the screen (via DrawDebugText function).
 * You are free to use it for all your other projects!
 */

#include <common.h>
#include <gpu.h>
#include <stdio.h>
#include <stdarg.h>
#define _TAB_SIZE_ 2

#if BUILD == 561
#define FONT8X8_FILE_ID 63
#else
#define FONT8X8_FILE_ID 64
#endif

extern int debugTextCount;
extern char hexDigits[];
extern char lowerhexDigits[];
extern DR_TPAGE debugfontTPages[2];

void DrawChar(char letter, ushort destX, ushort destY, byte clut);

void LoadDebugFont()
{
    ArcSeek(FONT8X8_FILE_ID, 0, 0); // FONT8X8.ARC
    printf("Loading FONT8X8.ARC\n");
    FileCollect();
    RECT FONT8X8_TextureRECT = {
        0x100,
        0x1E0,
        0x40,
        0x18};
    RECT FONT8X8_ClutRECT = {
        0x100,
        0x1F8,
        0x40,
        1};
    LoadImage(&FONT8X8_TextureRECT, *((u_long *)0x1f800008));
    LoadImage(&FONT8X8_ClutRECT, *((u_long *)0x1f80000c));
}
void ReverseString(char *str, int length)
{
    for (int j = 0; j < length / 2; ++j)
    {
        char temp = str[j];
        str[j] = str[length - j - 1];
        str[length - j - 1] = temp;
    }
}
int DrawString(int destX, int destY, int clut, char *str)
{
    int i = 0;
    while (str[i] != '\0')
    {
        DrawChar(str[i], destX, destY, clut);
        i++;
        destX += 8;
    }
    return i;
}
void DrawDebugText(ushort x, ushort y, byte clut, char *textP, ...)
{
    va_list args;
    va_start(args, textP);
    char letter;
    int destX = x * 8;
    int destY = y * 8;
    int startX = destX;
    if (debugTextCount == 0)
    {
        SetDrawTPage(&debugfontTPages[buffer], 0, 0, GetTPageValue(0, 0, 4, 1));
        AddPrim(&drawP->ot[0], &debugfontTPages[buffer]);
    }

    while ((letter = *textP) != '\0')
    {
        if (letter == '\n')
        {
            textP++; // Move to the next character
            destX = startX;
            destY += 8;
        }else if (letter == '\t')
        {
            textP++;
            destX += _TAB_SIZE_ * 8;
        }
        else if(letter == '%')
        {
            char str[12];
            int pad;
            if (textP[1] >= '0' && textP[1] <= '9')
            {
                pad = textP[1] - '0';
                textP++;
            }
            else
            {
                pad = 1;
            }
            for (size_t i = 0; i < pad; i++)
            {
                str[i] = '0';
            }
            str[pad] = '\0';

            if (textP[1] == 'x' || textP[1] == 'X')
            {
                int i = 0;
                uint num = va_arg(args, uint);

                if (num != 0)
                {
                    while (num != 0)
                    {
                        uint remainder = num % 16;
                        if (textP[1] == 'X')
                        {
                            str[i] = hexDigits[remainder];
                        }
                        else
                        {
                            str[i] = lowerhexDigits[remainder];
                        }
                        i += 1;
                        num /= 16;
                    }
                }

                int length;
                if (i > pad)
                {
                    str[i] = '\0';
                    length = i;
                }
                else
                {
                    length = pad;
                }

                ReverseString(&str, length);
                destX += DrawString(destX, destY, clut, &str) * 8;
            }
            else if (textP[1] == 'd' || textP[1] == 'i')
            {
                int i = 0;
                int num = va_arg(args, int);

                if (num == -2147483648)
                {
                    DrawString(destX,destY,clut,"-2147483648");
                    destX += 11;
                    goto KeepGoing;
                }
                else if (num < 0)
                {
                    DrawChar('-', destX, destY, clut);
                    destX += 8;
                    num = -num;
                }

                if (num != 0)
                {
                    while (num != 0)
                    {
                        int digit = num % 10;
                        str[i++] = digit + '0';
                        num /= 10;
                    }
                }
                else
                {
                    str[i++] = '0';
                }
                str[i] = '\0';
                int length = i;
                ReverseString(str, length);

                destX += DrawString(destX, destY, clut, &str) * 8;
            }
            else if (textP[1] == 'u')
            {
                int i = 0;
                uint num = va_arg(args, uint);

                if (num != 0)
                {
                    while (num != 0)
                    {
                        unsigned int digit = num % 10;
                        str[i++] = digit + '0';
                        num /= 10;
                    }
                }
                int length;
                if (i > pad)
                {
                    str[i] = '\0';
                    length = i;
                }
                else
                {
                    length = pad;
                }
                ReverseString(&str, length);
                destX += DrawString(destX, destY, clut, &str) * 8;
            }
            else if (textP[1] == 's')
            {
                char *p = va_arg(args, char *);
                while ((letter = *p) != '\0')
                {
                    DrawChar(letter, destX, destY, clut);
                    p += 1;
                    destX += 8;
                }
            }
            else if (textP[1] == '%')
            {
                DrawChar('%', destX, destY, clut);
                destX += 8;
            }
            else if (textP[1] == 'c')
            {
                char c = (char)va_arg(args, int);
                DrawChar(c, destX, destY, clut);
                destX += 8;
            }
        KeepGoing:
            textP += 2;
        }else
        {
            DrawChar(letter, destX, destY, clut);
            textP++; // Move to the next character
            destX += 8;
        }
    }
    va_end(args);
}
#undef _TAB_SIZE_
#undef FONT8X8_FILE_ID
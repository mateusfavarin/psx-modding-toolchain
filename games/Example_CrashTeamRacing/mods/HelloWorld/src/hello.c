#include <common.h>

int Hello_Main()
{
    if ((gameMode & LOADING) == 0)
    {
        DrawText("Hello World", 10, 180, 2, 0xffff0000);
        /*
            BUILD is a variable assigned during compilation time.
            It takes the value build_id defined in config.json
        */
        #if BUILD == NTSC_U
            DrawText("NTSC-U", 10, 200, 2, 0xffff0000);
        #elif BUILD == PAL
            DrawText("PAL", 10, 200, 2, 0xffff0000);
        #elif BUILD == NTSC_J
            DrawText("NTSC-J", 10, 200, 2, 0xffff0000);
        #else
            DrawText("Unknown build", 10, 200, 2, 0xffff0000);
        #endif
    }
}
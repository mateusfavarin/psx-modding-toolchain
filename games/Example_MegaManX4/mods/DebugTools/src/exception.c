#include <gpu.h>
#include <common.h>
static struct Registers
{
    int r[32];
    int returnPC;
    int hi, lo;
    int SR;
    int cause;
};

static struct Thread
{
    int flags, flags2;
    struct Registers registers;
    int unknown[9];
};

void DrawDebugText(ushort x, ushort y, byte clut, char *textP, ...);
void ResetDebugText();

extern int debugTextCount;

extern char *namesOfExceptions[13];
extern char *namesOfRegisters[37];


void Exception()
{
    struct Thread **process = *(int *)0x108;
    struct Thread *thread = *process;

    struct Thread storedThread;

    memcpy(&storedThread, thread, sizeof(struct Thread));

    void (*exitCriticalSection)() = 0x800ede0c;
    exitCriticalSection();
    ClearOTagR(&drawSettings[0].ot, 0xC);
    ClearOTagR(&drawSettings[1].ot, 0xC);

    while (1)
    {
        ResetDebugText();
        VSync(0);
        PutDispEnv(&drawSettings[buffer].disp);
        PutDrawEnv(&drawSettings[buffer].draw);
        DrawOTag(&drawSettings[buffer].ot[11]);
        buffer ^= 1;
        drawP = &drawSettings[buffer];
        ClearOTagR(&drawSettings[buffer].ot, 0xC);

        DrawDebugText(2, 2, 0, "EXCEPTION=%s", namesOfExceptions[(storedThread.registers.cause >> 2) & 0x1F]);

        // Show Register Values
        for (size_t i = 0; i < 37; i++)
        {
            int x = 4;
            int y = 4 + i;
            if (i > 19)
            {
                x = 16;
                y -= 20;
            }

            DrawDebugText(x, y, 1, "%s=%8X", namesOfRegisters[i], storedThread.registers.r[i]);

            // Get around buffer size limitations...
            if (debugTextCount > 33)
            {
                DrawOTag(&drawSettings[buffer].ot[11]);
                ResetDebugText();
                ClearOTagR(&drawSettings[buffer].ot, 0xC);
            }
        }
    }
}
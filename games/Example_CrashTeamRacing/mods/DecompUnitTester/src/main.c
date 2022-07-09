#include <common.h>
#include "math.h"

// MIPS Instructions
#define J(addr) ((((unsigned int) addr & 0xFFFFFF) >> 2) | 0x08000000)
#define JR_RA 0x03E00008
#define NOP   0x00000000

typedef int (*func)(unsigned int);
func newFunc = (func) &MATH_Sin;
int newRes;
func oldFunc = (func) &ND_MATH_Sin;
int ogRes;

unsigned int * hookAddress = (unsigned int *) (&GameplayUpdateLoop - 8);
unsigned int instructions[4];

unsigned int * ram = (unsigned int *) 0x80010000;
unsigned int * ram_4mb = (unsigned int *) 0x80410000;
unsigned int * ram_6mb = (unsigned int *) 0x80610000;
const unsigned int ramSize = (0x1FF800 - 0x10000) / 4;
unsigned int * scratchpad = (unsigned int *) 0x1F800000;
unsigned int * scratchpadBackup_4mb = (unsigned int *) 0x80400000;
unsigned int * scratchpadBackup_6mb = (unsigned int *) 0x80600000;
const unsigned int scratchpadSize = 0x400 / 4;
unsigned int hits = 0;
unsigned int total = 0;

/*
    The credit for the first two functions goes to Nicolas Noble,
    author of the openbios project. I'm calling these functions to
    disable interrupts, so that the PSX RAM is guaranteed to not change
    during all our function calls.
    https://github.com/grumpycoders/pcsx-redux/blob/main/src/mips/common/syscalls/syscalls.h#L39-L57
*/
static __attribute__((always_inline)) int enterCriticalSection() {
    register int n asm("a0") = 1;
    register int r asm("v0");
    __asm__ volatile("syscall\n"
                     : "=r"(n), "=r"(r)
                     : "r"(n)
                     : "at", "v1", "a1", "a2", "a3", "t0", "t1", "t2", "t3", "t4", "t5", "t6", "t7", "t8", "t9",
                       "memory");
    return r;
}

static __attribute__((always_inline)) void leaveCriticalSection() {
    register int n asm("a0") = 2;
    __asm__ volatile("syscall\n"
                     : "=r"(n)
                     : "r"(n)
                     : "at", "v0", "v1", "a1", "a2", "a3", "t0", "t1", "t2", "t3", "t4", "t5", "t6", "t7", "t8", "t9",
                       "memory");
}

void memCopy(unsigned int * dest, unsigned int * src, unsigned int size)
{
    for (unsigned int i = 0; i < size; i++)
        dest[i] = src[i];
}

int isEqual(unsigned int * dest, unsigned int * src, unsigned int size)
{
    int ret = 1;
    for (unsigned int i = 0; i < size; i++)
    {
        if (dest[i] != src[i])
        {
            printf("Diff at %x\n", &dest[i]);
            ret = 0;
        }
    }
    return ret;
}

// The Tester() function takes the same signature as the function you're decompiling
void Tester(unsigned int angle)
{
    enterCriticalSection();
    // Backup the program state before calling the decomp function
    memCopy(ram_4mb, ram, ramSize);
    memCopy(scratchpadBackup_4mb, scratchpad, scratchpadSize);
    // Call the decomp function
    newRes = newFunc(angle);
    // Backup result of decomp function
    memCopy(ram_6mb, ram, ramSize);
    memCopy(scratchpadBackup_6mb, scratchpad, scratchpadSize);
    // Load state
    memCopy(ram, ram_4mb, ramSize);
    memCopy(scratchpad, scratchpadBackup_4mb, scratchpadSize);
    // Call the original function
    func ogFunc = (func) &instructions[0];
    ogRes = ogFunc(angle);
    total++;
    // Comparing the results of the original function and the decomp function
    if ((newRes == ogRes) && (isEqual(scratchpad, scratchpadBackup_6mb, scratchpadSize)) && (isEqual(ram, ram_6mb, ramSize)))
        hits++;
    printf("Hits/totals: %d/%d\n", hits, total);
    leaveCriticalSection();
}

void InstallHook()
{
    unsigned int * oldFuncAddr = (unsigned int *) oldFunc;
    instructions[0] = oldFuncAddr[0];
    instructions[1] = oldFuncAddr[1];
    instructions[2] = J(&oldFuncAddr[2]);
    instructions[3] = NOP;

    oldFuncAddr[0] = J(&Tester);
    oldFuncAddr[1] = NOP;

    *hookAddress = JR_RA;
}
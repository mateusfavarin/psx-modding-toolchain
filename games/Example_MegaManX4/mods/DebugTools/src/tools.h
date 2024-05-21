#ifndef TOOLS_H
#define TOOLS_H
#include <common.h>
typedef struct
{
    bool opended;
    u_char mode;
    u_char mode2;
    u_char mode3;

    //Keep These in exact order
    bool showPlayerPos;
    bool showScroll;
    bool enableCollision;
    bool enableHitbox;
    u_char hitboxType;
    bool showTrigger; //Camera Trigger
    /************/
} DebugTools;
#endif
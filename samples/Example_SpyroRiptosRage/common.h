#ifndef COMMON_H
#define COMMON_H

struct Vec3
{
    int x;
    int z;
    int y;
};

int sprintf(char * str, char * format, ...);
void DrawText(char * text, int x, int y, int colorIndex, int * unk);

extern struct Vec3 speed;
extern int gameMode;

#endif
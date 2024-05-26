#ifndef MISC_H
#define MISC_H
#include <sys/types.h>
#include <stdbool.h>
#include <object.h>
typedef unsigned char   undefined;
typedef unsigned char    byte;
typedef unsigned int    dword;
typedef char    sbyte;
typedef unsigned char    undefined1;
typedef unsigned short    undefined2;
typedef unsigned int    undefined4;
typedef unsigned short    word;

void LoadLevel();

void SetupLayerSettings();
void SetupPriority();
void SetupSpawn();
#endif
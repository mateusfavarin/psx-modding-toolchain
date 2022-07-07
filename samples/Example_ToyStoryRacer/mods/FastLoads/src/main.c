#include <common.h>
#include <cd.h>
#define NUM_EXTENSIONS 4

typedef struct {
    CdlFILE file[NUM_EXTENSIONS];
} SectionLookupTable;

char * extensions[NUM_EXTENSIONS] = {".AXE;1\0", ".DAT;1\0", ".RAW;1\0", ".TER;1\0"};

int tableNotLoaded = 1;
SectionLookupTable sectionTable[NUM_COURSES];

void toUpper(char * str)
{
    while (*str != 0x0)
    {
        if ((unsigned char) (*str - 'a') < 26)
            *str -= 0x20;
        str++;
    }
}

int compare(char * s1, char * s2)
{
    for (int i = 0; ;i++)
    {
        if (s1[i] != s2[i])
            return 0;
        if (s1[i] == '\0')
            break;
    }
    return 1;
}

void LoadSectionTable()
{
    char filename[160];
    char filepath[160];

    for (int i = 0; i < NUM_COURSES; i++)
    {
        strcpy(filename, courseTable[i].filename);
        toUpper(filename);
        for (int j = 0; j < NUM_EXTENSIONS; j++)
        {
            filepath[0] = '\\';
            filepath[1] = '\0';
            strcat(filepath, filename);
            strcat(filepath, extensions[j]);
            CdControl(0xb, 0, 0);
            CdSearchFile(&sectionTable[i].file[j], filepath);
        }
    }
    tableNotLoaded = 0;
}

int GetRAWCachedSize(char * filename)
{
    if (tableNotLoaded)
        return DISC_SearchFile_UnformattedFilepath(filename);

    return sectionTable[levelID].file[2].size;
}

int LoadFileOptimized(char * filepath, char * buffer)
{
    if (tableNotLoaded)
        return DISC_SearchAndReadFile(filepath, buffer);

    CdlFILE * fp;
    int i = 0;
    int fileNotFound = 1;
    while (filepath[i] != '.')
        i++;
    while (filepath[i] != '\\')
        i--;
    i++;
    for (int j = 0; j < NUM_EXTENSIONS; j++)
    {
        if (compare(&filepath[i], sectionTable[levelID].file[j].name))
        {
            fp = &sectionTable[levelID].file[j];
            fileNotFound = 0;
            break;
        }
    }

    if (fileNotFound)
        return DISC_SearchAndReadFile(filepath, buffer);

    if (CdControl_Blocking(0x15, fp, 0)) // seek
    {
        int sectors = fp->size >> 0xb;
        int difference = 0x800 - (fp->size & 0x7FF);
        if (difference > 0)
        {
            sectors++;
            memcpy(&bufferBackup[0], &buffer[fp->size], difference);
        }
        if (CdRead(sectors, buffer, 0x80))
        {
            int reading = 1;
            while (reading)
                reading = CdReadSync(1, 0);
            if (difference > 0)
                memcpy(&buffer[fp->size], &bufferBackup[0], difference);
            return fp->size;
        }
    }
    return 0;
}
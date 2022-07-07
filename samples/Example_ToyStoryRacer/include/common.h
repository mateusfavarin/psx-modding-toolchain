#define NUM_COURSES 20

typedef struct {
    char * filename;
    unsigned int unk1;
    unsigned int unk2;
    unsigned int songID;
} LevelLookupTable;

void strcpy(char * dst, char * src);
void strcat(char * dst, char * src);
void memcpy(char * dst, char * src, int c);
int DISC_SearchAndReadFile(char * filePath, char * buffer);
int DISC_SearchFile_UnformattedFilepath(char * filePath);

extern LevelLookupTable courseTable[NUM_COURSES];
extern int levelID;
extern char bufferBackup[];
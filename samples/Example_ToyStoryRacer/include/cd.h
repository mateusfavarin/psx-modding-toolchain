typedef struct {
    unsigned char minute;
    unsigned char second;
    unsigned char sector;
    unsigned char track;
} CdlLOC;

typedef struct {
    CdlLOC pos;
    int size;
    char name[16];
} CdlFILE;

int CdControl(unsigned char com, CdlFILE * fp, unsigned char * result);
int CdControl_Blocking(unsigned char com, CdlFILE * fp, unsigned char * result);
CdlFILE * CdSearchFile(CdlFILE * fp, char * filename);
int CdRead(int sectors, char * buffer, int mode);
int CdReadSync(int mode, char * result);
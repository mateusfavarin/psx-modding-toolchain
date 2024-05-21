#include <gpu.h>

static int exceptionDescriptor = 0;

long EnableEvent(unsigned long event);

void Exception();

void ExitCriticalSection();

long OpenEvent(unsigned long desc,long spec,long mode,long *func());

void EnableExceptionEvent()
{
    exceptionDescriptor = OpenEvent(0xF0000010,0x1000,0x1000,Exception);
    ExitCriticalSection();

   EnableEvent(exceptionDescriptor);
}
#include <common.h>
#include "math.h"

void DrawSpeedometer()
{
	if (gameMode == 0)
	{
		unsigned int horSpeed = (unsigned int) ((speed.x * speed.x) + (speed.z * speed.z));
		horSpeed = sqrt(horSpeed);
		int verSpeed = speed.y;
		char buffer[64];
		sprintf(buffer, "Hor Speed: %u", horSpeed);
		DrawText(buffer, 0xB0, 0x15, 1, 0);
		sprintf(buffer, "Ver Speed: %d", verSpeed);
		DrawText(buffer, 0xB0, 0x25, 1, 0);
	}
}
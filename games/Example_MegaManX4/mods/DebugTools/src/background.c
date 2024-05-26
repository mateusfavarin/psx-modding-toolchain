#include <common.h>
#include <gpu.h>
#include <layer.h>
#include "tools.h"

void ResetLayerBuffer();
void DrawDebugOverlay();
extern DebugTools tools;
void NewDrawBackground()
{
    tempPrimP = &rectBuffer[buffer][0];
    rectCount = 0;
    if(!tools.enableCollision)
    {
        ResetLayerBuffer();
        
        for (size_t i = 0; i < 3; i++)
        {
            if(bgLayers[i].update){
                DumpLayerScreens(i);
            }
        }
        DumpActiveScreens();
        /*
        * TODO: maybe add back Intro Blue Rect effect...
        */
        for (size_t i = 0; i < 3; i++)
        {
            if(bgLayers[i].display)
            {
                ResetLayerPointers(i);
                DrawLayer(i);
                AssignLayer(i);
            }
        }
    }else
    {
        DrawDebugOverlay();
    }

}
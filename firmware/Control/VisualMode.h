#ifndef VISUAL_MODE_H
#define VISUAL_MODE_H

#include <stdint.h>

typedef struct
{
    float x;
    float y;
    float z;
    uint64_t qr_id;
} VisualInfo;

void Visual_SetTarget(VisualInfo *vinfo);
void Visual_Poll();

#endif
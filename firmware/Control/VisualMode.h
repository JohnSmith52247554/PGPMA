#ifndef VISUAL_MODE_H
#define VISUAL_MODE_H

#include <stdint.h>

#include "kinematics.h"

typedef struct
{
    float x;
    float y;
    float z;
    float rot;
    uint64_t qr_id;
} VisualInfo;

typedef struct
{
    VisualInfo vinfo;
    MotorAngle angle;
    uint8_t active;
    uint8_t state;
} VisualHandleTypeDef;

#define VISUAL_OFF 0
#define VISUAL_ON 1

#define VISUAL_STATE_IDLE 1
#define VISUAL_STATE_FETCHING 2
#define VISUAL_STATE_PLACING 3

#define VISUAL_GRIP_OK 1
#define VISUAL_GRIP_NG 0

extern VisualHandleTypeDef visual_handle;

void Visual_Init(VisualHandleTypeDef *vhandle);
void Visual_Active(VisualHandleTypeDef *vhandle);
void Visual_Deactive(VisualHandleTypeDef *vhandle);
void Visual_SetTarget(VisualHandleTypeDef *vhandle, VisualInfo *vinfo);
uint8_t Visual_GripPoll(VisualHandleTypeDef *vhandle);

#endif
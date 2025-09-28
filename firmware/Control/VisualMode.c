#include "VisualMode.h"

#include <math.h>

#include "trigonometric.h"
#include "kinematics.h"
#include "AllJoint.h"

#include "OLED.h"

uint64_t vcnt = 0;

#define VISUAL_TOLERANCE_ANGLE 5.f
#define VISUAL_M1_ANGLE 3.f

// #define arm_to_camera_X 52.0f
// #define arm_to_camera_Z -8.0f
// #define arm_rotation 270.0f
// #define arm_position_Y 15.0f

#define KINE_GRIP_ALPHA_MIN -90.f
#define KINE_GRIP_ALPHA_MAX 0.f

#define VISUAL_GRIP_Y_BASE -6.3142f
#define VISUAL_GRIP_Y_SLOT 0.4707f
#define VISUAL_GRIP_Y_MIN 5.f

VisualHandleTypeDef visual_handle = {0};

void Visual_Init(VisualHandleTypeDef *vhandle)
{
    vhandle->active = VISUAL_OFF;
    vhandle->state = VISUAL_STATE_IDLE;
    vhandle->vinfo.x = 0.f;
    vhandle->vinfo.y = VISUAL_GRIP_Y_MIN;
    vhandle->vinfo.z = 0.f;
    vhandle->vinfo.qr_id = 0;
}

void Visual_Active(VisualHandleTypeDef *vhandle)
{
    vhandle->active = VISUAL_ON;
    vhandle->state = VISUAL_STATE_IDLE;
    vhandle->vinfo.qr_id = 0;
}

void Visual_Deactive(VisualHandleTypeDef *vhandle)
{
    vhandle->active = VISUAL_OFF;
    vhandle->state = VISUAL_STATE_IDLE;
    vhandle->vinfo.qr_id = 0;
    vhandle->vinfo.x = 0.f;
    vhandle->vinfo.y = 0.f;
    vhandle->vinfo.z = 0.f;
}

void Visual_SetTarget(VisualHandleTypeDef *vhandle, VisualInfo *vinfo)
{
    if (vhandle->active == VISUAL_OFF)
    {
        OLED_ShowString(2, 1, "off");
        return;
    }

    if (vhandle->state == VISUAL_STATE_IDLE
    || vhandle->state == VISUAL_STATE_FETCHING)
    {
        vcnt += 1;
        OLED_ShowNum(2, 9, vcnt, 5);

        uint64_t last_qr_id = vhandle->vinfo.qr_id;
        vhandle->vinfo = *vinfo;

        KineHandle kine = {0};

        kine.x = vinfo->x + 0 * (sqrtf(kine.x * kine.x + kine.z * kine.z) / 40.f - 1);
        kine.z = vinfo->z + 0 * (sqrtf(kine.x * kine.x + kine.z * kine.z) / 40.f - 1);
        kine.y = VISUAL_GRIP_Y_BASE + VISUAL_GRIP_Y_SLOT * sqrtf(kine.x * kine.x + kine.z * kine.z);
        if (kine.y < VISUAL_GRIP_Y_MIN)
            kine.y = VISUAL_GRIP_Y_MIN;

        kine.alpha = degree2radian(KINE_GRIP_ALPHA_MIN);
        if (kine_reverse_range(&kine, KINE_GRIP_ALPHA_MIN, KINE_GRIP_ALPHA_MAX, 1.f) != KINE_OK)
        {
            if (vhandle->vinfo.qr_id == last_qr_id && vhandle->state == VISUAL_STATE_FETCHING)
            {
                vhandle->state = VISUAL_STATE_FETCHING;
            }
            else
            {
                vhandle->state = VISUAL_STATE_IDLE; 
            }
            OLED_ShowString(2, 1, "err     ");
            return;
        }
        vhandle->angle = kine_get_motor_angle(&kine);
        OLED_ShowString(2, 1, "ok     ");
        // OLED_Clear();
        // OLED_ShowNum(1, 0, vhandle->angle.m1a, 2);
        // OLED_ShowNum(1, 4, vhandle->angle.m2a, 2);
        // OLED_ShowNum(2, 0, vhandle->angle.m3a, 2);
        // OLED_ShowNum(2, 4, vhandle->angle.m4a, 2);
        vhandle->state = VISUAL_STATE_FETCHING;
        // if (vhandle->angle.m1a > 0)
        //     vhandle->angle.m1a += VISUAL_M1_ANGLE;
        Joint_SetTarget(&m1h, vhandle->angle.m1a);
        Joint_SetTarget(&m2h, vhandle->angle.m2a);
        Joint_SetTarget(&m3h, vhandle->angle.m3a);
        Joint_SetTarget(&m4h, vhandle->angle.m4a);
    }
   
}

uint8_t Visual_GripPoll(VisualHandleTypeDef *vhandle)
{
    if (vhandle->active == VISUAL_OFF || vhandle->state != VISUAL_STATE_FETCHING)
        return VISUAL_GRIP_NG;

    if ( (fabsf(Joint_GetAngle(&m1h, joint_info + 0) - vhandle->angle.m1a) < VISUAL_TOLERANCE_ANGLE) &&
         (fabsf(Joint_GetAngle(&m2h, joint_info + 1) - vhandle->angle.m2a) < VISUAL_TOLERANCE_ANGLE) &&
         (fabsf(Joint_GetAngle(&m3h, joint_info + 2) - vhandle->angle.m3a) < VISUAL_TOLERANCE_ANGLE) &&
         (fabsf(Joint_GetAngle(&m4h, joint_info + 3) - vhandle->angle.m4a) < VISUAL_TOLERANCE_ANGLE) )
    {
        vhandle->state = VISUAL_STATE_PLACING;
        OLED_ShowString(2, 1, "GRIPOK");
        return VISUAL_GRIP_OK;
    }
    return VISUAL_GRIP_NG;

}

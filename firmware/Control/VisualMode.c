#include "VisualMode.h"

#include "trigonometric.h"
#include "kinematics.h"
#include "AllJoint.h"

#include "OLED.h"

#define VISUAL_ACHIEVED 0
#define VISUAL_HAVEN_ACHIEVED 1

#define VISUAL_TOLERANCE_ANGLE 5.f

uint8_t has_achieved_target = VISUAL_ACHIEVED;

#define VISUAL_MODE_OFF 0
#define VISUAL_MODE_ON 1

uint8_t visual_mode_state = VISUAL_MODE_OFF;

uint64_t current_qr_id = 0;

float camera_x = 0.f;
float camera_y = 0.f;
float camera_z = 0.f;

float arm_x = 0.f;
float arm_y = 0.f;
float arm_z = 0.f;

#define arm_to_camera_X 52.0f
#define arm_to_camera_Z -8.0f
#define arm_rotation 270.0f
#define arm_position_Y 15.0f

#define KINE_GRIP_ALPHA -60.f
KineHandle kine = {0};
MotorAngle angle;

void Visual_CameraCoord2ArmCoord();

void Visual_SetTarget(VisualInfo *vinfo)
{
    if (has_achieved_target == VISUAL_HAVEN_ACHIEVED && vinfo->qr_id != current_qr_id)
        return;
    
    visual_mode_state = VISUAL_MODE_ON;
    
    current_qr_id = vinfo->qr_id;
    camera_x = vinfo->x;
    camera_y = vinfo->y;
    camera_z = vinfo->z;
    has_achieved_target = VISUAL_HAVEN_ACHIEVED;
    Visual_CameraCoord2ArmCoord();
    kine.x = arm_x;
    kine.y = arm_y;
    kine.z = arm_z;
    kine.alpha = degree2radian(KINE_GRIP_ALPHA);

    OLED_ShowNum(4, 1, arm_x, 2);
    OLED_ShowNum(4, 3, arm_y, 2);
    OLED_ShowNum(4, 5, arm_z, 2);
    OLED_ShowNum(4, 7, kine.alpha, 2);

    if (kine_reverse_resolve(&kine) != KINE_OK)
    {
        visual_mode_state = VISUAL_MODE_OFF;
        has_achieved_target = VISUAL_ACHIEVED;
        // OLED_ShowString(4, 1, "err");
        return;
    }
    angle = get_motor_angle(&kine);
    // OLED_ShowString(4, 1, "ok");

    Joint_SetTarget(&m1h, angle.m1a);
    Joint_SetTarget(&m2h, angle.m2a);
    Joint_SetTarget(&m3h, angle.m3a);
    Joint_SetTarget(&m4h, angle.m4a);
}

void Visual_CameraCoord2ArmCoord()
{
    float theta = arm_rotation * 3.14159265 / 180.0;
    arm_x = arm_to_camera_X + camera_x/10.0f * t_cos_radian(theta) - camera_y/10.0f * t_sin_radian(theta);
    arm_z = -(arm_to_camera_Z + camera_x/10.0f * t_sin_radian(theta) + camera_y/10.0f * t_cos_radian(theta));
    arm_y = arm_position_Y;
}

void Visual_Poll()
{
    if (visual_mode_state == VISUAL_MODE_OFF || has_achieved_target == VISUAL_ACHIEVED)
        return;

    if ( (fabsf(Joint_GetAngle(&m1h, joint_info + 0) - angle.m1a) < VISUAL_TOLERANCE_ANGLE) &&
         (fabsf(Joint_GetAngle(&m2h, joint_info + 1) - angle.m2a) < VISUAL_TOLERANCE_ANGLE) &&
         (fabsf(Joint_GetAngle(&m3h, joint_info + 2) - angle.m3a) < VISUAL_TOLERANCE_ANGLE) &&
         (fabsf(Joint_GetAngle(&m4h, joint_info + 3) - angle.m4a) < VISUAL_TOLERANCE_ANGLE) )
    {
        has_achieved_target = VISUAL_ACHIEVED;
        OLED_ShowString(4, 1, "ok");
    }
}
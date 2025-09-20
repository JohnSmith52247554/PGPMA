#ifndef TEST_H
#define TEST_H

#include <stdint.h>

#define PI 3.1415926f

typedef struct
{
    float x;
    float y;
    float z;
    float alpha;

    // 此处全为弧度
    float theta_1;
    float theta_2;
    float theta_3;
    float theta_4;
} KineHandle;

typedef struct
{
    // 此处全为角度
    float m1a, m2a, m3a, m4a;
} MotorAngle;

#define KINE_OK 0
#define KINE_INVALIDE 1
#define KINE_UNREACHABLE 2
#define KINE_JOINT_LIMIT 3
#define KINE_ARM_COLLISION 4

uint8_t kine_reverse_resolve(KineHandle *handle);
MotorAngle get_motor_angle(KineHandle *handle);

#endif
#ifndef JOINT_H
#define JOINT_H

#include "main.h"
#include "MS42D.h"

#define REDUCTION_510   51.0f
#define REDUCTION_192   19.2f

#define MS42D_RESET_SPEED 5.f

typedef struct {
    float reduction_ratio;
    float target_angle;
    uint8_t has_achieved_target;
    float err;
    float i_err;
    float last_err;
    uint32_t can_id;
    float start_up_counter;
    float max_speed;
    float ref_offset;   // 参考点（即关节复位点）相较于电机自身的零点的偏移量
    uint8_t reset_flag; // 复位时使用
    float reset_begin_point;    // 复位时首先移动到此点，然后找霍尔元件
    MS42DDirRot reset_dir;
    float reset_offset; // 通过霍尔元件复位后，移动此角度
} Joint_HandleTypeDef;

typedef struct 
{
    uint32_t can_id;
    float reduction_ratio;
    float max_speed;
    float reset_begin_point;
    MS42DDirRot reset_dir;
    float reset_offset;
    uint16_t current; // 运行时的电流，0-1200mA
} Joint_InitTypeDef;

void Hall_EXTICallBack(uint32_t GPIO_Pin);
void Joint_Init(Joint_HandleTypeDef *hjoint, Joint_InitTypeDef *jinit);
void Joint_MakeZero(Joint_HandleTypeDef *hjoint, float cur_angle);
void Joint_ResetStart(Joint_HandleTypeDef *hjoint);
void Joint_ResetEnd(Joint_HandleTypeDef *hjoint, MS42D_Info *info);
void Joint_SetTarget(Joint_HandleTypeDef *hjoint, float angle);
void Joint_SetMaxSpeed(Joint_HandleTypeDef *hjoint, float max_speed);
void Joint_SetMaxSpeedPercentage(Joint_HandleTypeDef *hjoint, float percentage);
void Joint_Poll(Joint_HandleTypeDef *hjoint, MS42D_Info *info);
float Joint_GetAngle(Joint_HandleTypeDef *hjoint, MS42D_Info *info);

#endif
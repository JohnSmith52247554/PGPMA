#include "Joint.h"

#include "MS42D.h"
#include "OLED.h"

#include <stdlib.h>

#define ACHIEVE_THRESHLOD 10.f
#define START_UP_SLOPE 0.5f
#define MIN(A, B) (A) > (B) ? (B) : (A)

#define KP 0.06f
#define KI 0.f
#define KD 0.2f

float regulation(float num, float max);

// 中断回调函数
void hall_0_itcallback();
void hall_1_itcallback();
void hall_2_itcallback();
void hall_3_itcallback();

void Hall_EXTICallBack(uint32_t GPIO_Pin)
{
    switch (GPIO_Pin)
    {
    case HALL_0_Pin:
        hall_0_itcallback();
        break;
    case HALL_1_Pin:
        hall_1_itcallback();
        break;
    case HALL_2_Pin:
        hall_2_itcallback();
        break;
    case HALL_3_Pin:
        hall_3_itcallback();
        break;
    default:
        break;
    }
}


void Joint_Init(Joint_HandleTypeDef *hjoint, Joint_InitTypeDef *jinit)
{
    hjoint->can_id = jinit->can_id;
    hjoint->reduction_ratio = jinit->reduction_ratio;
    hjoint->target_angle = 0;
    hjoint->has_achieved_target = 1;
    hjoint->i_err = 0;
    hjoint->last_err = 0;
    hjoint->start_up_counter = 0;
    hjoint->max_speed = jinit->max_speed;
    hjoint->ref_offset = 0.f;
    hjoint->reset_begin_point = jinit->reset_begin_point;
    hjoint->reset_dir = jinit->reset_dir;
    hjoint->reset_offset = jinit->reset_offset;

    MS42D_SetMoment(hjoint->can_id, MS42D_DIR_ROT_ANTICLOCKWISE, 0, jinit->current);
}

void Joint_ResetStart(Joint_HandleTypeDef *hjoint)
{
    // 开始以低速旋转
    hjoint->reset_flag = 0;

    MS42D_SetSpeed(hjoint->can_id, hjoint->reset_dir, MS42D_RESET_SPEED);
}

void Joint_ResetEnd(Joint_HandleTypeDef *hjoint, MS42D_Info *info)
{
    hjoint->reset_flag = 0;
    // 停止旋转
    MS42D_SetSpeed(hjoint->can_id, MS42D_DIR_ROT_ANTICLOCKWISE, 0);

    // 记录当前角度
    // MS42D_RequestData(hjoint->can_id);

    // MS42D_Info info;

    // if (MS42D_GetFeedback(&info) == 0)
    //     Error_Handler();

    hjoint->ref_offset = info->angle + hjoint->reset_offset * hjoint->reduction_ratio;

    // if (hjoint->can_id == 3)
    //     OLED_ShowFloatNum(4, 1, info.angle, 8, 2);
}

void Joint_SetTarget(Joint_HandleTypeDef *hjoint, float angle)
{
    hjoint->has_achieved_target = 0;
    hjoint->start_up_counter = 5.f;
    hjoint->target_angle = angle * hjoint->reduction_ratio + hjoint->ref_offset;
}

void Joint_SetMaxSpeed(Joint_HandleTypeDef *hjoint, float max_speed)
{
    hjoint->max_speed = MIN(max_speed, MS42D_MAX_SPEED);
}

void Joint_SetMaxSpeedPercentage(Joint_HandleTypeDef *hjoint, float percentage)
{
    if (percentage < 0)
        percentage = 0;
    else if (percentage > 100)
        percentage = 100;
    hjoint->max_speed = percentage * 0.01f * MS42D_MAX_SPEED;
}


void Joint_Poll(Joint_HandleTypeDef *hjoint, MS42D_Info *info)
{
    if (hjoint->has_achieved_target)
        return;

    // MS42D_RequestData(hjoint->can_id);
    // uint8_t id;
    // uint8_t has_achieved;
    // float speed;
    // float angle;
    // MS42D_GetFeedback(&id, &has_achieved, &speed, &angle);


    // OLED_ShowFloatNum(3, 1, hjoint->ref_offset, 8, 1);
    hjoint->last_err = hjoint->err;
    hjoint->err = hjoint->target_angle - info->angle;

    if (hjoint->err < ACHIEVE_THRESHLOD && hjoint->err > -ACHIEVE_THRESHLOD)
    {
        hjoint->has_achieved_target = 1;
        hjoint->err = 0;
        hjoint->i_err = 0;
        hjoint->last_err = 0;

        MS42D_SetSpeed2(hjoint->can_id, 0);
        // OLED_ShowFloatNum(3, 1, 0, 8, 1);
        return;
    }

    hjoint->i_err += hjoint->err;
    float d_err = hjoint->err - hjoint->last_err;

    float new_speed = KP * hjoint->err + KI * hjoint->i_err + KD * d_err;

    if (hjoint->start_up_counter < info->speed)
        hjoint->start_up_counter = info->speed;
    if (hjoint->start_up_counter <  hjoint->max_speed)
        hjoint->start_up_counter += START_UP_SLOPE;

    // regulation(new_speed, MIN(MIN(MS42D_MAX_SPEED, hjoint->max_speed), hjoint->start_up_counter));
    // new_speed = MIN(new_speed, MIN(hjoint->max_speed, hjoint->start_up_counter));
    float regulated_speed = regulation(new_speed, MIN(hjoint->max_speed, hjoint->start_up_counter));

    // if (hjoint->can_id == 1)
    // {
    //     OLED_ShowFloatNum(3, 1, hjoint->err, 8, 1);
    //     OLED_ShowFloatNum(4, 1, new_speed, 8, 1);   
    // }

    MS42D_SetSpeed2(hjoint->can_id, regulated_speed);

    // 避免总线繁忙
    for (uint8_t i = 0; i < 100; i++)
        ;
}

/**
 * @brief 回到电机的内置零点
 * 
 */
void Joint_MakeZero(Joint_HandleTypeDef *hjoint, float cur_angle)
{
    OLED_ShowFloatNum(4, 1, cur_angle, 8, 2);

    MS42DDirRot direction;
    if (cur_angle < 0)
    {
        direction = MS42D_DIR_ROT_ANTICLOCKWISE;
        OLED_ShowString(4, 13, "a");
    }
    else
    {
        direction = MS42D_DIR_ROT_CLOCKWISE;
        OLED_ShowString(4, 13, "c");
    }

    MS42D_SetRelativePos(hjoint->can_id, direction, MS42D_RESET_SPEED, cur_angle);
}

float Joint_GetAngle(Joint_HandleTypeDef *hjoint, MS42D_Info *info)
{
    return (info->angle - hjoint->ref_offset) / hjoint->reduction_ratio;
}

float regulation(float num, float max)
{
    float abs_max = max > 0 ? max : -max;
    if (num > 0 && num > abs_max)
        return abs_max;
    else if (num < 0 && num < -abs_max)
        return -abs_max;
    else
        return num;
}
#include "AllJoint.h"

#include "Joint.h"
#include "JointCtrl.h"
#include "MS42D.h"
#include "OLED.h"

Joint_HandleTypeDef m1h;
Joint_HandleTypeDef m2h;
Joint_HandleTypeDef m3h;
Joint_HandleTypeDef m4h;

// TIM中断标志位
uint8_t joint_timit_state = JOINT_TIMIT_OK;

// 存储读取到的电机的信息
MS42D_Info joint_info[4];

void AllJoint_RequestData();
void AllJoint_PowerUpReset();

// 中断回调函数
void hall_0_itcallback()
{
    m1h.reset_flag = 1;
}

void hall_1_itcallback()
{
    m2h.reset_flag = 1;
}

void hall_2_itcallback()
{
    m3h.reset_flag = 1;
}

void hall_3_itcallback()
{
    m4h.reset_flag = 1;
}

void AllJoint_Init()
{
    Joint_InitTypeDef Joint_InitStruct;
    Joint_InitStruct.can_id = 1;
    Joint_InitStruct.max_speed = MS42D_MAX_SPEED * 0.5f;
    Joint_InitStruct.reduction_ratio = REDUCTION_510;
    Joint_InitStruct.reset_begin_point = 60;
    Joint_InitStruct.reset_dir = MS42D_DIR_ROT_ANTICLOCKWISE;
    Joint_InitStruct.reset_offset = 0;
    Joint_InitStruct.current = 800;
    Joint_Init(&m1h, &Joint_InitStruct);

    Joint_InitStruct.can_id = 2;
    Joint_InitStruct.reduction_ratio = REDUCTION_510;
    Joint_InitStruct.reset_begin_point = 60;
    Joint_InitStruct.reset_offset = 5;
    Joint_InitStruct.current = 1200;
    Joint_Init(&m2h, &Joint_InitStruct);

    Joint_InitStruct.can_id = 3;
    Joint_InitStruct.reduction_ratio = REDUCTION_192;
    Joint_InitStruct.reset_begin_point = 60;
    Joint_InitStruct.reset_offset = -8.5;
    Joint_InitStruct.current = 800;
    Joint_Init(&m3h, &Joint_InitStruct);

    Joint_InitStruct.can_id = 4;
    Joint_InitStruct.reduction_ratio = REDUCTION_192;
    Joint_InitStruct.reset_begin_point = -60;
    Joint_InitStruct.reset_dir = MS42D_DIR_ROT_CLOCKWISE;
    Joint_InitStruct.reset_offset = 15;
    Joint_InitStruct.current = 800;
    Joint_Init(&m4h, &Joint_InitStruct);

    AllJoint_PowerUpReset();
}

/**
 * @brief 
 * 
 * @warning 此函数假设上电时所有关节均处于恰当位置
 * 
 */
void AllJoint_PowerUpReset()
{
    joint_ctrl_status = JC_STATUS_RESET;
    rst_pending_joint_num = 0;

    if (HAL_GPIO_ReadPin(GPIOB, HALL_0_Pin) == GPIO_PIN_SET)
    {
        Joint_ResetStart(&m1h);
        rst_pending_joint_num += 1;
    }
    if (HAL_GPIO_ReadPin(GPIOB, HALL_1_Pin) == GPIO_PIN_SET)
    {
        Joint_ResetStart(&m2h);
        rst_pending_joint_num += 1;
    }
    if (HAL_GPIO_ReadPin(GPIOE, HALL_2_Pin) == GPIO_PIN_SET)
    {
        Joint_ResetStart(&m3h);
        rst_pending_joint_num += 1;
    }
    if (HAL_GPIO_ReadPin(GPIOE, HALL_3_Pin) == GPIO_PIN_SET)
    {
        Joint_ResetStart(&m4h);
        rst_pending_joint_num += 1;
    }
}

void AllJoint_Reset()
{
    // 回到电机内置零点
    joint_ctrl_status = JC_STATUS_RESET_POLL;
    Joint_SetTarget(&m1h, m1h.reset_begin_point);
    Joint_SetTarget(&m2h, m2h.reset_begin_point);
    Joint_SetTarget(&m3h, m3h.reset_begin_point);
    Joint_SetTarget(&m4h, m4h.reset_begin_point);
}

void AllJoint_Stop()
{
    joint_ctrl_status = JC_STATUS_POLL;
    MS42D_SetSpeed(m1h.can_id, MS42D_DIR_ROT_ANTICLOCKWISE, 0);
    m1h.has_achieved_target = 1;
    MS42D_SetSpeed(m2h.can_id, MS42D_DIR_ROT_ANTICLOCKWISE, 0);
    m2h.has_achieved_target = 1;
    MS42D_SetSpeed(m3h.can_id, MS42D_DIR_ROT_ANTICLOCKWISE, 0);
    m3h.has_achieved_target = 1;
    MS42D_SetSpeed(m4h.can_id, MS42D_DIR_ROT_ANTICLOCKWISE, 0);
    m4h.has_achieved_target = 1;
}

void Joint_TimItHandler()
{
    if (joint_timit_state == JOINT_TIMIT_OK)
        return;

    AllJoint_RequestData();

    Joint_Poll(&m1h, &joint_info[m1h.can_id - 1]);
    Joint_Poll(&m2h, &joint_info[m2h.can_id - 1]);
    Joint_Poll(&m3h, &joint_info[m3h.can_id - 1]);
    Joint_Poll(&m4h, &joint_info[m4h.can_id - 1]);

    joint_timit_state = JOINT_TIMIT_OK;
}

void AllJoint_StoreData(uint8_t can_id)
{
    MS42D_RequestData(can_id);
    MS42D_Info info;
    if (MS42D_GetFeedback(&info) == 0)
    {
        periph_error = PE_CAN2_RX_ERROR;
        hardware_error = HE_MS42D_ERROR;
        return;
    }
    joint_info[info.can_id - 1] = info;
}

void AllJoint_RequestData()
{
    AllJoint_StoreData(m1h.can_id);
    AllJoint_StoreData(m2h.can_id);
    AllJoint_StoreData(m3h.can_id);
    AllJoint_StoreData(m4h.can_id);

    // OLED_ShowFloatNum(3, 1, joint_info[0].angle, 5, 2);
    // OLED_ShowFloatNum(4, 1, joint_info[1].angle, 5, 2);
}
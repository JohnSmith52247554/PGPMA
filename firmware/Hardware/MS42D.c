#include "MS42D.h"

#include "can.h"

typedef enum
{
    MS42D_CMD_MODE_SPEED = 0x01,
    MS42D_CMD_MODE_RELATIVE_POSITION = 0x02,
    MS42D_CMD_MODE_MOMENT = 0x03,
    MS42D_CMD_MODE_ABSOLUTE_POSITION = 0x04
} MS42DCmdMode;

/**
 * @brief 将一个float放大10倍后转化为一个uint16_t，用于提供CAN命令的参数
 * 
 * @note f需要是一个正数
 */
static uint16_t floatToUint16_t(float f)
{
    return (uint16_t)myabs((int)(f * 10));
}

/**
 * @brief 初始化MS42D
 * 
 * @note 由于目前还没有校准，所以相当于没有作用
 */
void MS42D_Init()
{
    // MX_CAN2_Init();
    MS42D_SetAbsolutePos(1, 1, 0);
}

/**
 * @brief 使MS42D以一定的速度转动
 *
 * @param id MS42D的ID
 * @param direction 转动方向 @ref MS42DDirRot
 * @param speed 转动速度，单位为rad/s，最大为43.9（电机的极限转速），精确到0.1
 */
void MS42D_SetSpeed(uint32_t id, MS42DDirRot direction, float speed)
{
    uint16_t speed_16 = floatToUint16_t(speed);
    uint8_t cmd[] = {MS42D_CMD_MODE_SPEED,
                     (uint8_t)direction,
                     0x20,
                     0x00,
                     0x00,
                     ((speed_16 & 0xFF00) >> 8),
                     (speed_16 & 0x00FF)};
    CAN_Send(id, cmd, 7);
}

void MS42D_SetSpeed2(uint32_t id, float speed)
{
    if (speed <= 0)
    {
        MS42D_SetSpeed(id, MS42D_DIR_ROT_ANTICLOCKWISE, speed);
    }
    else
    {
        MS42D_SetSpeed(id, MS42D_DIR_ROT_CLOCKWISE, -speed);
    }
}

/**
 * @brief 以当前位置为原点，以一定速度，转动一定角度
 *
 * @param id MS42D的ID
 * @param direction 转动方向 @ref MS42DDirRot
 * @param speed 转动速度，单位为rad/s，最大为43.9（电机的极限转速），精确到0.1
 * @param angle 转动的相对角度，单位为度，最大为6553.5，精确到0.1
 * @note speed和angle不能决定转动的方向，转动方向由direction决定
 */
void MS42D_SetRelativePos(uint32_t id, MS42DDirRot direction, float speed, float angle)
{
    uint16_t speed_16 = floatToUint16_t(speed);
    uint16_t angle_16 = floatToUint16_t(angle);
    uint8_t cmd[] = {MS42D_CMD_MODE_RELATIVE_POSITION,
                     (uint8_t)direction,
                     0x20,
                     ((angle_16 & 0xFF00) >> 8),
                     (angle_16 & 0x00FF),
                     ((speed_16 & 0xFF00) >> 8),
                     (speed_16 & 0x00FF)};
    CAN_Send(id, cmd, 7);
}

/**
 * @brief 以一定力矩和速度转动
 *
 * @param id MS42D的ID
 * @param direction 转动方向 @ref MS42DDirRot
 * @param speed 转动速度，单位为rad/s，最大为43.9（电机的极限转速），精确到0.1
 * @param current 流过电机的电流，单位为毫安，最大为1200（电机的极限电流），精确到1
 * @note speed和current不能决定转动的方向，转动方向由direction决定
 */
void MS42D_SetMoment(uint32_t id, MS42DDirRot direction, float speed, uint16_t current)
{
    uint16_t speed_16 = floatToUint16_t(speed);
    uint8_t cmd[] = {MS42D_CMD_MODE_MOMENT,
                     (uint8_t)direction,
                     0x20,
                     ((current & 0xFF00) >> 8),
                     (current & 0x00FF),
                     ((speed_16 & 0xFF00) >> 8),
                     (speed_16 & 0x00FF)};
    CAN_Send(id, cmd, 7);
}

/**
 * @brief 以一定速度，转动到相对原点一定角度的位置
 *
 * @param id MS42D的ID
 * @param speed 转动速度，单位为rad/s，最大为43.9（电机的极限转速），精确到0.1
 * @param angle 相对原点的角度，单位为度
 *
 * @note 此模式下不需要设置direction，电机会自动判断往哪边转动会更快到达目标位置，然后往哪边转动
 * @note 在此模式下，电机最多只会转动一圈，可以认为实际转到的位置为angle % 360
 */
void MS42D_SetAbsolutePos(uint32_t id, float speed, float angle)
{
    uint16_t speed_16 = floatToUint16_t(speed);
    uint16_t angle_16 = floatToUint16_t(angle);
    uint8_t cmd[] = {MS42D_CMD_MODE_ABSOLUTE_POSITION,
                     (uint8_t)MS42D_DIR_ROT_CLOCKWISE,
                     0x20,
                     ((angle_16 & 0xFF00) >> 8),
                     (angle_16 & 0x00FF),
                     ((speed_16 & 0xFF00) >> 8),
                     (speed_16 & 0x00FF)};
    CAN_Send(id, cmd, 7);
}

/**
 * @brief 请求电机发送反馈
 * 
 * @param id 电机的ID
 */
void MS42D_RequestData(uint32_t id)
{
    uint8_t cmd[] = {
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
    };

    CAN_Send(id, cmd, 7);
}

/**
 * @brief 读取电机的反馈
 *
 * @param motor_id 电机的ID
 * @param has_achieved 电机是否到达了指定位置，到达目标位置为1，还未到达为0，仅在位置模式和绝对位置模式下有效
 * @param speed 电机的当前速度，单位为rad/s，精度0.1
 * @param angle 电机当前的绝对角度，单位为度，带符号，精度0.1
 * @return uint8_t 是否成功得到了反馈，成功为1，失败为0
 *
 * @note 当电机设置为申请方式时，必须在MS42D_RequestData后调用
 */
uint8_t MS42D_GetFeedback(MS42D_Info *info)
{
    uint64_t timeout = 999999;
    while (CAN_RxFlag() == 0)
    {
        --timeout;
        if (timeout == 0)
            return 0;
    }

    uint32_t id;
    uint8_t len;
    uint8_t data[8];
    if (CAN_Receive(&id, &len, data) != HAL_OK)
        return 0;

    if (len != 8)
        return 0;

    info->can_id = data[0];
    info->has_achieved = data[1];

    info->speed = (float)((data[2] << 8) + data[3]) / 10;

    int32_t raw_angle = ((int32_t)data[4] << 24) |
                        ((int32_t)data[5] << 16) |
                        ((int32_t)data[6] << 8) |
                        (int32_t)data[7];

    info->angle = (float)raw_angle / 10;

    return 1;
}


// uint8_t MS42D_GetFeedback(uint8_t *motor_id, uint8_t *has_achieved, float *speed, float *angle)
// {
//     uint64_t timeout = 1000;
//     while (CAN_RxFlag() == 0)
//     {
//         --timeout;
//         if (timeout == 0)
//             return 0;
//     }

//     uint32_t id;
//     uint8_t len;
//     uint8_t data[8];
//     if (CAN_Receive(&id, &len, data) != HAL_OK)
//         return 0;

//     if (len != 8)
//        return 0;

//     *motor_id = data[0];
//     *has_achieved = data[1];

//     *speed = (float)((data[2] << 8) + data[3]) / 10;

// 	int32_t raw_angle = ((int32_t)data[4] << 24) |
// 						((int32_t)data[5] << 16) |
// 						((int32_t)data[6] << 8) |
// 						(int32_t)data[7];

// 	*angle = (float)raw_angle / 10;

// 	return 1;
// }
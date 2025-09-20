#include "Servo.h"
#include "OLED.h"
#include "usart.h"

#include <string.h>

/**
 * @brief 初始化所有舵机。将舵机设置为顺时针270度，并归中（135度）
 * 
 * @return HAL_StatusTypeDef 
 */
HAL_StatusTypeDef Servo_Init()
{
    HAL_StatusTypeDef state;
    state = USART_SendStr("#255PMOD1!");

    if (state != HAL_OK)
        return state;
    return USART_SendStr("#255P1500T1000!");
}

/**
 * @brief 设置舵机的占空比
 * 
 * @param id 舵机id，0-255
 * @param duty 占空比，500-2500
 * @param time 从当前占空比线性过度到设置占空比所需的时间，0-9999，单位为ms
 * @return HAL_StatusTypeDef 
 */
HAL_StatusTypeDef Servo_SetDuty(uint8_t id, uint16_t duty, uint16_t time)
{
    static char cmd[] = "#000P0000T0000!";

    Servo_NumToStr(cmd + 1, 3, id);
    Servo_NumToStr(cmd + 5, 4, duty);
    Servo_NumToStr(cmd + 10, 4, time);

    return USART_SendStr(cmd);
}

/**
 * @brief 获得指定id的舵机的当前占空比
 * 
 * @param id 指定舵机的id，0-254
 * @return int16_t 指定id的占空比，-1代表读取错误
 * 
 * @note id不能为255（广播id），因为这样没有回传
 */
int16_t Servo_GetDuty(uint8_t id)
{
    static char cmd[] = "#000PRAD!";
    Servo_NumToStr(cmd + 1, 3, id);

    if (USART_SendStr(cmd) != HAL_OK)
    {
        OLED_ShowString(1, 1, "SEND ERR");
        return -1;
    }
    char recv[] = "#000PEEEE!";
    char mask[] = "#000";
    Servo_NumToStr(mask + 1, 3, id);
    HAL_Delay(1);
    if (USART_RecieveStr(recv, 10) != HAL_OK || Servo_StrCmp(recv, mask, 4) == 0)
    {
        // OLED_ShowString(1, 1, "RECV ERR");
        // OLED_ShowString(2, 1, recv);
        return -1;
    }
    // OLED_ShowString(1, 1, "NO ERR  ");

    return Servo_StrToNum(recv + 5, 4);
}

/**
 * @brief 设置舵机转到的角度
 *
 * @param id 舵机id，0-255
 * @param angle 设置的角度，0-270
 * @param time 从当前角度线性过度到设置角度所需的时间，0-9999，单位为ms
 * @return HAL_StatusTypeDef
 */
HAL_StatusTypeDef Servo_SetAngle(uint8_t id, float angle, uint16_t time)
{
    return Servo_SetDuty(id, angle / 270 * 2000 + 500, time);
}

/**
 * @brief 获得指定id的舵机的当前角度
 *
 * @param id 指定舵机的id，0-254
 * @return float 指定id的角度，-1代表读取错误
 *
 * @note id不能为255（广播id），因为这样没有回传
 */
float Servo_GetAngle(uint8_t id)
{
    int16_t duty = Servo_GetDuty(id);
    if (duty < 0)
        return -1.f;
    return (float)(duty - 500) / 2000.f * 270.f;
}

/**
 * @brief 恢复扭力，以舵机当前的位置恢复扭力
 *
 * @param id 指定舵机的id，0-255
 * @return HAL_StatusTypeDef
 */
HAL_StatusTypeDef Servo_TorqueEnable(uint8_t id)
{
    static char cmd[] = "#000PULR!";
    Servo_NumToStr(cmd + 1, 3, id);
    return USART_SendStr(cmd);
}

/**
 * @brief 释放扭力，调用后可以用外力掰动舵机
 *
 * @param id 指定舵机的id，0-255
 * @return HAL_StatusTypeDef
 * 
 * @warning 具体效果待测试
 */
HAL_StatusTypeDef Servo_TorqueDisable(uint8_t id)
{
    static char cmd[] = "#000PULK!";
    Servo_NumToStr(cmd + 1, 3, id);
    return USART_SendStr(cmd);
}

/**
 * @brief 暂停当前任务，调用Servo_Continue后，会继续被暂停的指令
 *
 * @param id 指定舵机的id，0-255
 * @return HAL_StatusTypeDef
 */
HAL_StatusTypeDef Servo_Pause(uint8_t id)
{
    static char cmd[] = "#000PDPT!";
    Servo_NumToStr(cmd + 1, 3, id);
    return USART_SendStr(cmd);
}

/**
 * @brief 继续被暂停的指令，需要配合Servo_Pause使用
 *
 * @param id 指定舵机的id，0-255
 * @return HAL_StatusTypeDef
 */
HAL_StatusTypeDef Servo_Continue(uint8_t id)
{
    static char cmd[] = "#000PDCT!";
    Servo_NumToStr(cmd + 1, 3, id);
    return USART_SendStr(cmd);
}

/**
 * @brief 舵机停止在当前位置
 *
 * @param id 指定舵机的id，0-255
 * @return HAL_StatusTypeDef
 *
 * @note 与Servo_Pause不同，即使调用Servo_Continue也不会继续
 */
HAL_StatusTypeDef Servo_Stop(uint8_t id)
{
    static char cmd[] = "#000PDST!";
    Servo_NumToStr(cmd + 1, 3, id);
    return USART_SendStr(cmd);
}

/**
 * @brief 将舵机的当前位置设置为中值（1500）
 *
 * @param id 指定舵机的id，0-255
 * @return HAL_StatusTypeDef
 */
HAL_StatusTypeDef Servo_AdjustMiddle(uint8_t id)
{
    static char cmd[] = "#000PSCK!";
    Servo_NumToStr(cmd + 1, 3, id);
    return USART_SendStr(cmd);
}


uint16_t Servo_Pow(uint16_t base, uint16_t exp)
{
    if (exp == 0)
        return 1;
    uint16_t result = base;
    exp--;
    for (; exp > 0; exp--)
    {
        result *= base;
    }
    return result;
}

void Servo_NumToStr(char *beg, uint8_t len, uint16_t num)
{
    beg += len - 1;

    for (uint8_t digit = 0; digit < len; digit++)
    {
        *beg = (num / Servo_Pow(10, digit)) % 10 + '0';
        beg--;
    }
}

uint16_t Servo_StrToNum(char *beg, uint8_t len)
{
    uint16_t output = 0;

    beg += len - 1;

    for (uint8_t digit = 0; digit < len; digit++)
    {
        output += (*beg - '0') * Servo_Pow(10, digit);
        beg--;
    }

    return output;
}

// HAL_StatusTypeDef Servo_GetReturn(const char *cmd)
// {
//     HAL_StatusTypeDef state = USART_SendStr(cmd);
//     if (state != HAL_OK)
//         return state;

//     // HAL_Delay(100);
//     char recv[] = "#EE!";
//     state = USART_RecieveStr(recv, 5);
//     if (strcmp(recv, "#OK!") != 0)
//         return HAL_ERROR;
//     return state;
// }

// HAL_StatusTypeDef Servo_AutoRetry(const char *cmd)
// {
//     HAL_StatusTypeDef state = HAL_ERROR;
//     for (int retry_time = 0; retry_time < SERVO_AUTO_RETRY_TIME && state != HAL_OK; retry_time++)
//         state = Servo_GetReturn(cmd);
//     return state;
// }

uint8_t Servo_StrCmp(const char *str1, const char *str2, uint8_t len)
{
    for (; len > 0; len--, str1++, str2++)
    {
        if (*str1 != *str2)
            return 0;
    }
    return 1;
}
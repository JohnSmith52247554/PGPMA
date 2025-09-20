#include "Gripper.h"

#include <math.h>

#include "Servo.h"
#include "ADS1115.h"
#include "OLED.h"
#include "usart.h"

#define GRIPPER_SERVO_ID 1

#define GRIPPER_MAX_ANGLE   143.f
#define GRIPPER_MIN_ANGLE   0.f

#define PRESSUER_THRESHOLD  800

#define GRIPPER_SPEED_FACTOR    9999.f
#define GRIPPER_MAX_SPEED   100.f
#define GRIPPER_MIN_SPEED   1.f

float gripper_speed = 10.f;
uint8_t gripper_close_poll_flag = 0;

float gripper_angle = -1;

uint8_t gripper_timit_flag = GRIPPER_TIMIT_OK;

float gripper_target;
uint8_t gripper_has_achieve_target = 1;

#define S1_MIDDLE_OFFSET 117.f

float servo_speed = 10.f;
uint8_t s1_timit_flag = S1_TIMIT_OK;
float s1_angle = -1;

#define SERVO_SPEED_FACTOR 9999.f
#define SERVO_MAX_SPEED 100.f
#define SERVO_MIN_SPEED 1.f
#define SERVO_MAX_ANGLE 90.f
#define SERVO_MIN_ANGLE -90.f

uint8_t s1_has_achieve_target = 1;
float s1_target;

void Gripper_Init()
{
    static char *cmd = "#001PMOD1!";
    Servo_NumToStr(cmd + 1, 3, GRIPPER_SERVO_ID);
    USART_SendStr(cmd);
    Servo_SetAngle(GRIPPER_SERVO_ID, 0, GRIPPER_SPEED_FACTOR / gripper_angle);

    ADS1115_Config();
}

void Gripper_SetSpeed(float speed)
{
    if (speed > GRIPPER_MAX_SPEED)
        gripper_speed = GRIPPER_MAX_SPEED;
    else if (speed < GRIPPER_MIN_SPEED)
        gripper_speed = GRIPPER_MIN_SPEED;
    else
        gripper_speed = speed;
}

void Gripper_SetSpeedPercentage(float per)
{
    Gripper_SetSpeed(per * 0.01f * GRIPPER_MAX_SPEED);
}

void Gripper_SetAngle(float angle)
{
    if (angle >= GRIPPER_MIN_ANGLE && angle < GRIPPER_MAX_ANGLE)
    {
        Servo_SetAngle(GRIPPER_SERVO_ID, angle, GRIPPER_SPEED_FACTOR / gripper_speed);
        gripper_has_achieve_target = 0;
        gripper_target = angle;
    }
}

void Gripper_Open()
{
    Servo_SetAngle(GRIPPER_SERVO_ID, GRIPPER_MIN_ANGLE, GRIPPER_SPEED_FACTOR / gripper_speed);
    gripper_has_achieve_target = 0;
    gripper_target = GRIPPER_MIN_ANGLE;
}

void Gripper_CloseStart()
{
    Servo_SetAngle(GRIPPER_SERVO_ID, GRIPPER_MAX_ANGLE, GRIPPER_SPEED_FACTOR / gripper_speed);
    gripper_close_poll_flag = 1;
    gripper_has_achieve_target = 0;
    gripper_target = GRIPPER_MAX_ANGLE;
}

void Gripper_StoreAngle()
{
    float angle = Servo_GetAngle(GRIPPER_SERVO_ID);
    if (angle >= 0)
        gripper_angle = angle;
}

void Gripper_Poll()
{
    if (gripper_timit_flag == GRIPPER_TIMIT_OK)
        return;
    gripper_timit_flag = GRIPPER_TIMIT_OK;

    Gripper_StoreAngle();

    if (fabsf(gripper_target - gripper_angle) < 3.f)
    {
        gripper_has_achieve_target = 1;
    }

    if (!gripper_close_poll_flag)
        return;

    uint16_t pressure;
    if (ADS1115_ReadContinuous(&pressure) != HAL_OK)
    {
        periph_error = PE_I2C2_RX_ERROR;
        hardware_error = HE_ADS1115_ERROR;
        // Servo_Stop(GRIPPER_SERVO_ID);
        return;
    }

    // OLED_ShowNum(4, 1, pressure, 8);

    if (pressure > PRESSUER_THRESHOLD)
    {
        if (Servo_Stop(GRIPPER_SERVO_ID) != HAL_OK)
        {
            periph_error = PE_USART3_RX_ERROR;
            hardware_error = HE_SERVO_ERROR;
            Servo_Stop(GRIPPER_SERVO_ID);
        }
        gripper_close_poll_flag = 0;
        gripper_has_achieve_target = 1;
        return;
    }

    if (GRIPPER_MAX_ANGLE - gripper_angle < 3.f)
    {
        gripper_close_poll_flag = 0;
        Servo_Stop(GRIPPER_SERVO_ID);
        gripper_has_achieve_target = 1;
    }
}

float Gripper_GetAngle()
{
    return gripper_angle;
}

void Gripper_Stop()
{
    gripper_close_poll_flag = 0;
    Servo_Stop(GRIPPER_SERVO_ID);
}

uint8_t Gripper_HasAchieveTarget()
{
    return gripper_has_achieve_target;
}

void S1_Init()
{
    S1_SetAngle(0);
}

void S1_SetSpeed(float speed)
{
    if (speed > SERVO_MAX_SPEED)
        servo_speed = SERVO_MAX_SPEED;
    else if (speed < SERVO_MIN_SPEED)
        servo_speed = SERVO_MIN_SPEED;
    else
        servo_speed = speed;
}

void S1_SetSpeedPercentage(float per)
{
    S1_SetSpeed(per * 0.01f * SERVO_MAX_SPEED);
}

void S1_SetAngle(float angle)
{
    if (angle >= SERVO_MIN_ANGLE && angle <= SERVO_MAX_ANGLE)
    {
        angle += S1_MIDDLE_OFFSET;
        Servo_SetAngle(S1_ID, angle, SERVO_SPEED_FACTOR / servo_speed);
        s1_has_achieve_target = 0;
    }
}

void S1_Stop()
{
    Servo_Stop(S1_ID);
}

void S1_Poll()
{
    if (s1_timit_flag == S1_TIMIT_OK)
        return;
    s1_timit_flag = S1_TIMIT_OK;

    if (fabsf(s1_target - s1_angle) < 3)
        s1_has_achieve_target = 1;

    float angle = Servo_GetAngle(S1_ID);
    if (angle >= 0)
        s1_angle = angle;
}

float S1_GetAngle()
{
    return s1_angle - S1_MIDDLE_OFFSET;
}

uint8_t S1_HasAchieveTarget()
{
    return s1_has_achieve_target;
}
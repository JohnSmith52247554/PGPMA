#ifndef SERVO_H
#define SERVO_H

#include "main.h"
#include <stdint.h>

#define SERVO_BROADCAST_ID 0xFF
#define S1_ID 0

#define S1_TIMIT_OK 0
#define S1_TIMIT_UNHANDLED 1

extern uint8_t s1_timit_flag;

void Servo_NumToStr(char *beg, uint8_t len, uint16_t num);
uint16_t Servo_StrToNum(char *beg, uint8_t len);
uint8_t Servo_StrCmp(const char *str1, const char *str2, uint8_t len);

HAL_StatusTypeDef Servo_Init();
HAL_StatusTypeDef Servo_SetDuty(uint8_t id, uint16_t duty, uint16_t time);
int16_t Servo_GetDuty(uint8_t id);
HAL_StatusTypeDef Servo_TorqueEnable(uint8_t id);
HAL_StatusTypeDef Servo_TorqueDisable(uint8_t id);
HAL_StatusTypeDef Servo_Pause(uint8_t id);
HAL_StatusTypeDef Servo_Continue(uint8_t id);
HAL_StatusTypeDef Servo_Stop(uint8_t id);
HAL_StatusTypeDef Servo_SetAngle(uint8_t id, float angle, uint16_t time);
float Servo_GetAngle(uint8_t id);
HAL_StatusTypeDef Servo_AdjustMiddle(uint8_t id);

#endif
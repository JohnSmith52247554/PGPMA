#ifndef GRIPPER_H
#define GRIPPER_H

#include "main.h"

#define GRIPPER_TIMIT_OK 0
#define GRIPPER_TIMIT_UNHANDLED 1
extern uint8_t gripper_timit_flag;

void Gripper_Init();
void Gripper_SetSpeedPercentage(float per);
void Gripper_SetSpeed(float speed);
void Gripper_SetAngle(float angle);
void Gripper_Open();
void Gripper_CloseStart();
void Gripper_Poll();
float Gripper_GetAngle();
void Gripper_Stop();
uint8_t Gripper_HasAchieveTarget();

void S1_Init();
void S1_SetSpeed(float speed);
void S1_SetSpeedPercentage(float per);
void S1_SetAngle(float angle);
void S1_Stop();
void S1_Poll();
float S1_GetAngle();
uint8_t S1_HasAchieveTarget();

#endif
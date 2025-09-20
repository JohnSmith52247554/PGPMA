#ifndef ALL_JOINT_H
#define ALL_JOINT_H

#include "Joint.h"

#define JOINT_TIMIT_OK 0
#define JOINT_TIMIT_UNHANDLED 1
extern uint8_t joint_timit_state;

extern Joint_HandleTypeDef m1h;
extern Joint_HandleTypeDef m2h;
extern Joint_HandleTypeDef m3h;
extern Joint_HandleTypeDef m4h;

extern MS42D_Info joint_info[4];

void AllJoint_Init();
void AllJoint_Reset();
void AllJoint_Stop();
void Joint_TimItHandler();
void AllJoint_RequestData();

#endif
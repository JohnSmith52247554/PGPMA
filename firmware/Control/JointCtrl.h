#ifndef JOINT_CTRL_H
#define JOINT_CTRL_H

#include "main.h"

#define JC_STATUS_POLL 0
#define JC_STATUS_RESET_POLL 1
#define JC_STATUS_RESET 2

extern uint8_t joint_ctrl_status;
extern uint8_t rst_pending_joint_num;

void JointCtrl_Poll();

#endif
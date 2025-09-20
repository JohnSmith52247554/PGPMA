#ifndef USBD_CTRL_H
#define USBD_CTRL_H

#include "main.h"

#define USBD_WORK_IDLE 0
#define USBD_WORK_BUSY 1
extern volatile uint8_t usbd_work_state;

// 指令
#define CMD_IMMEDIATE_STOP          0x55 // 立即停止当前动作
#define CMD_IMMEDIATE_ORTHOGONAL    0x58 // 立即移动到某个坐标（正交坐标系）
#define CMD_IMMEDIATE_JOINT         0x5B // 立即移动到某个坐标（关节坐标系）
#define CMD_OPEN_GRIPPER            0x5E // 打开爪子
#define CMD_CLOSE_GRIPPER           0x61 // 合上爪子
#define CMD_GET_STATE               0x64 // 发送各个关节的状态
#define CMD_VISUAL                  0x67 // 视觉识别模式
#define CMD_WRITE_FLASH             0x6A // 写Flash
#define CMD_READ_FLASH              0x6D // 读Flash
#define CMD_RESET                   0x70 // 复位
#define CMD_END_WRITE_FLASH         0x73
#define CMD_SET_SPEED               0x76

#define CMD_CLEAN_FLASH_A           0xAB
#define CMD_CLEAN_FLASH_B           0xCD
#define CMD_CLEAN_FLASH_C           0xEF
#define CMD_CLEAN_FLASH_D           0x01

// 回复
#define RESPOND_OK      0xAA
#define RESPOND_BUSY    0xAD
#define RESPOND_ERROR   0xB0
#define RESPOND_TIMEOUT 0xB3

void USBD_Enable();
void USBD_Disable();
void USBD_Poll();

#endif
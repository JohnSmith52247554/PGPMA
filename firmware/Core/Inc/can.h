/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file    can.h
  * @brief   This file contains all the function prototypes for
  *          the can.c file
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2025 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __CAN_H__
#define __CAN_H__

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "main.h"

/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

extern CAN_HandleTypeDef hcan2;

/* USER CODE BEGIN Private defines */

/* USER CODE END Private defines */

void MX_CAN2_Init(void);

/* USER CODE BEGIN Prototypes */
void CAN_Send(uint32_t id, uint8_t *data, uint8_t length);
HAL_StatusTypeDef CAN_Send_Nonblocking(uint32_t id, uint8_t *data, uint8_t length);
uint8_t CAN_RxFlag();
uint8_t CAN_Receive(uint32_t *id, uint8_t *len, uint8_t *data);
/* USER CODE END Prototypes */

#ifdef __cplusplus
}
#endif

#endif /* __CAN_H__ */


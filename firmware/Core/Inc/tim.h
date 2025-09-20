/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file    tim.h
  * @brief   This file contains all the function prototypes for
  *          the tim.c file
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
#ifndef __TIM_H__
#define __TIM_H__

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "main.h"

/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

extern TIM_HandleTypeDef htim2;

extern TIM_HandleTypeDef htim3;

extern TIM_HandleTypeDef htim4;

/* USER CODE BEGIN Private defines */
#define TIM_DELAY_OK 0
#define TIM_DELAY_PENDING 1
extern volatile uint8_t tim_delay_flag;

// extern uint64_t tim3_it_counter;
/* USER CODE END Private defines */

void MX_TIM2_Init(void);
void MX_TIM3_Init(void);
void MX_TIM4_Init(void);

/* USER CODE BEGIN Prototypes */
HAL_StatusTypeDef TIM2_IT_Start();
HAL_StatusTypeDef TIM2_IT_Stop();
void TIM_DelayStart(uint16_t ms);
void TIM_Wait();
/* USER CODE END Prototypes */

#ifdef __cplusplus
}
#endif

#endif /* __TIM_H__ */


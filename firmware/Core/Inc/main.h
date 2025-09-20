/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.h
  * @brief          : Header for main.c file.
  *                   This file contains the common defines of the application.
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
#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "stm32f4xx_hal.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include <stdint.h>
#include "error.h"
/* USER CODE END Includes */

/* Exported types ------------------------------------------------------------*/
/* USER CODE BEGIN ET */
uint32_t myabs(int32_t num);
/* USER CODE END ET */

/* Exported constants --------------------------------------------------------*/
/* USER CODE BEGIN EC */

/* USER CODE END EC */

/* Exported macro ------------------------------------------------------------*/
/* USER CODE BEGIN EM */

/* USER CODE END EM */

/* Exported functions prototypes ---------------------------------------------*/
void Error_Handler(void);

/* USER CODE BEGIN EFP */

/* USER CODE END EFP */

/* Private defines -----------------------------------------------------------*/
#define KEY_1_Pin GPIO_PIN_5
#define KEY_1_GPIO_Port GPIOC
#define KEY_1_EXTI_IRQn EXTI9_5_IRQn
#define HALL_0_Pin GPIO_PIN_0
#define HALL_0_GPIO_Port GPIOB
#define HALL_0_EXTI_IRQn EXTI0_IRQn
#define HALL_1_Pin GPIO_PIN_1
#define HALL_1_GPIO_Port GPIOB
#define HALL_1_EXTI_IRQn EXTI1_IRQn
#define HALL_2_Pin GPIO_PIN_9
#define HALL_2_GPIO_Port GPIOE
#define HALL_2_EXTI_IRQn EXTI9_5_IRQn
#define HALL_3_Pin GPIO_PIN_10
#define HALL_3_GPIO_Port GPIOE
#define HALL_3_EXTI_IRQn EXTI15_10_IRQn
#define USBD_VBUS_Pin GPIO_PIN_9
#define USBD_VBUS_GPIO_Port GPIOA

/* USER CODE BEGIN Private defines */
/* USER CODE END Private defines */

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */

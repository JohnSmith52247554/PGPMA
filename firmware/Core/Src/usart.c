/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file    usart.c
  * @brief   This file provides code for the configuration
  *          of the USART instances.
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
/* Includes ------------------------------------------------------------------*/
#include "usart.h"

/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

UART_HandleTypeDef huart3;

/* USART3 init function */

void MX_USART3_UART_Init(void)
{

  /* USER CODE BEGIN USART3_Init 0 */

  /* USER CODE END USART3_Init 0 */

  /* USER CODE BEGIN USART3_Init 1 */

  /* USER CODE END USART3_Init 1 */
  huart3.Instance = USART3;
  huart3.Init.BaudRate = 9600;
  huart3.Init.WordLength = UART_WORDLENGTH_8B;
  huart3.Init.StopBits = UART_STOPBITS_1;
  huart3.Init.Parity = UART_PARITY_NONE;
  huart3.Init.Mode = UART_MODE_TX_RX;
  huart3.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart3.Init.OverSampling = UART_OVERSAMPLING_16;
  if (HAL_HalfDuplex_Init(&huart3) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART3_Init 2 */
  HAL_UART_MspInit(&huart3);
  /* USER CODE END USART3_Init 2 */

}

void HAL_UART_MspInit(UART_HandleTypeDef* uartHandle)
{

  GPIO_InitTypeDef GPIO_InitStruct = {0};
  if(uartHandle->Instance==USART3)
  {
  /* USER CODE BEGIN USART3_MspInit 0 */

  /* USER CODE END USART3_MspInit 0 */
    /* USART3 clock enable */
    __HAL_RCC_USART3_CLK_ENABLE();

    __HAL_RCC_GPIOD_CLK_ENABLE();
    /**USART3 GPIO Configuration
    PD8     ------> USART3_TX
    */
    GPIO_InitStruct.Pin = GPIO_PIN_8;
    GPIO_InitStruct.Mode = GPIO_MODE_AF_OD;
    GPIO_InitStruct.Pull = GPIO_PULLUP;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
    GPIO_InitStruct.Alternate = GPIO_AF7_USART3;
    HAL_GPIO_Init(GPIOD, &GPIO_InitStruct);

  /* USER CODE BEGIN USART3_MspInit 1 */

  /* USER CODE END USART3_MspInit 1 */
  }
}

void HAL_UART_MspDeInit(UART_HandleTypeDef* uartHandle)
{

  if(uartHandle->Instance==USART3)
  {
  /* USER CODE BEGIN USART3_MspDeInit 0 */

  /* USER CODE END USART3_MspDeInit 0 */
    /* Peripheral clock disable */
    __HAL_RCC_USART3_CLK_DISABLE();

    /**USART3 GPIO Configuration
    PD8     ------> USART3_TX
    */
    HAL_GPIO_DeInit(GPIOD, GPIO_PIN_8);

  /* USER CODE BEGIN USART3_MspDeInit 1 */

  /* USER CODE END USART3_MspDeInit 1 */
  }
}

/* USER CODE BEGIN 1 */

HAL_StatusTypeDef USART_SendByte(uint8_t byte)
{
  // 设置为发送模式
  huart3.Instance->CR1 &= ~USART_CR1_RE;
  huart3.Instance->CR1 |= USART_CR1_TE;

  HAL_StatusTypeDef state = HAL_UART_Transmit(&huart3, &byte, 1, 10);

  // 设置为接收模式
  huart3.Instance->CR1 &= ~USART_CR1_TE;
  huart3.Instance->CR1 |= USART_CR1_RE;
  return state;
}

HAL_StatusTypeDef USART_SendStr(const char *str)
{
  // 设置为发送模式
  huart3.Instance->CR1 &= ~USART_CR1_RE;
  huart3.Instance->CR1 |= USART_CR1_TE;

  __HAL_UART_CLEAR_FLAG(&huart3, UART_FLAG_TC);

  HAL_StatusTypeDef state = HAL_UART_Transmit(&huart3, (uint8_t *)str, strlen(str), 10);

  while (!__HAL_UART_GET_FLAG(&huart3, UART_FLAG_TC));

  // 设置为接收模式
  huart3.Instance->CR1 &= ~USART_CR1_TE;
  huart3.Instance->CR1 |= USART_CR1_RE;
  return state;
}

HAL_StatusTypeDef USART_RecieveStr(char *str, uint16_t size)
{
  // 确保处于接收模式
  huart3.Instance->CR1 &= ~USART_CR1_TE;
  huart3.Instance->CR1 |= USART_CR1_RE;

  return HAL_UART_Receive(&huart3, (uint8_t *)str, size, 10);
}
/* USER CODE END 1 */

/* USER CODE BEGIN Header */
/**
 ******************************************************************************
 * @file    can.c
 * @brief   This file provides code for the configuration
 *          of the CAN instances.
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
#include "can.h"

/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

CAN_HandleTypeDef hcan2;

/* CAN2 init function */
void MX_CAN2_Init(void)
{

  /* USER CODE BEGIN CAN2_Init 0 */
  /* USER CODE END CAN2_Init 0 */

  /* USER CODE BEGIN CAN2_Init 1 */

  /* USER CODE END CAN2_Init 1 */
  hcan2.Instance = CAN2;
  hcan2.Init.Prescaler = 6;
  hcan2.Init.Mode = CAN_MODE_NORMAL;
  hcan2.Init.SyncJumpWidth = CAN_SJW_1TQ;
  hcan2.Init.TimeSeg1 = CAN_BS1_4TQ;
  hcan2.Init.TimeSeg2 = CAN_BS2_2TQ;
  hcan2.Init.TimeTriggeredMode = DISABLE;
  hcan2.Init.AutoBusOff = DISABLE;
  hcan2.Init.AutoWakeUp = DISABLE;
  hcan2.Init.AutoRetransmission = ENABLE;
  hcan2.Init.ReceiveFifoLocked = DISABLE;
  hcan2.Init.TransmitFifoPriority = DISABLE;
  if (HAL_CAN_Init(&hcan2) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN CAN2_Init 2 */
  HAL_CAN_MspInit(&hcan2);

  if (HAL_CAN_GetState(&hcan2) == HAL_CAN_STATE_ERROR)
  {
	  Error_Handler();
  }

  CAN_FilterTypeDef sFilterConfig;
  sFilterConfig.FilterBank = 0;
  sFilterConfig.FilterMode = CAN_FILTERMODE_IDMASK;
  sFilterConfig.FilterScale = CAN_FILTERSCALE_16BIT;
  sFilterConfig.FilterIdHigh = 0x0000;
//   sFilterConfig.FilterIdLow = 0x0A << 5; // MS42D的反馈ID为0x0A
  sFilterConfig.FilterIdLow = 0x0A;
  sFilterConfig.FilterMaskIdHigh = 0x0000;
//   sFilterConfig.FilterMaskIdLow = 0x7FF << 5;
  sFilterConfig.FilterMaskIdLow = 0x7FF;
  sFilterConfig.FilterFIFOAssignment = CAN_RX_FIFO0;
  sFilterConfig.FilterActivation = ENABLE;
  sFilterConfig.SlaveStartFilterBank = 0;

  if (HAL_CAN_ConfigFilter(&hcan2, &sFilterConfig) != HAL_OK)
  {
	  Error_Handler();
  }

	if (HAL_CAN_Start(&hcan2) != HAL_OK)
	{
		Error_Handler();
	}
  /* USER CODE END CAN2_Init 2 */

}

void HAL_CAN_MspInit(CAN_HandleTypeDef* canHandle)
{

  GPIO_InitTypeDef GPIO_InitStruct = {0};
  if(canHandle->Instance==CAN2)
  {
  /* USER CODE BEGIN CAN2_MspInit 0 */

  /* USER CODE END CAN2_MspInit 0 */
    /* CAN2 clock enable */
    __HAL_RCC_CAN2_CLK_ENABLE();
    __HAL_RCC_CAN1_CLK_ENABLE();

    __HAL_RCC_GPIOB_CLK_ENABLE();
    /**CAN2 GPIO Configuration
    PB12     ------> CAN2_RX
    PB13     ------> CAN2_TX
    */
    GPIO_InitStruct.Pin = GPIO_PIN_12|GPIO_PIN_13;
    GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
    GPIO_InitStruct.Alternate = GPIO_AF9_CAN2;
    HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

  /* USER CODE BEGIN CAN2_MspInit 1 */

  /* USER CODE END CAN2_MspInit 1 */
  }
}

void HAL_CAN_MspDeInit(CAN_HandleTypeDef* canHandle)
{

  if(canHandle->Instance==CAN2)
  {
  /* USER CODE BEGIN CAN2_MspDeInit 0 */

  /* USER CODE END CAN2_MspDeInit 0 */
    /* Peripheral clock disable */
    __HAL_RCC_CAN2_CLK_DISABLE();
    __HAL_RCC_CAN1_CLK_DISABLE();

    /**CAN2 GPIO Configuration
    PB12     ------> CAN2_RX
    PB13     ------> CAN2_TX
    */
    HAL_GPIO_DeInit(GPIOB, GPIO_PIN_12|GPIO_PIN_13);

  /* USER CODE BEGIN CAN2_MspDeInit 1 */

  /* USER CODE END CAN2_MspDeInit 1 */
  }
}

/* USER CODE BEGIN 1 */
void CAN_Send(uint32_t id, uint8_t *data, uint8_t length)
{
	CAN_TxHeaderTypeDef TxHeader;
	uint32_t TxMailbox;

	TxHeader.StdId = id;
	TxHeader.ExtId = 0;
	TxHeader.RTR = CAN_RTR_DATA;
	TxHeader.IDE = CAN_ID_STD;
	TxHeader.DLC = length;
	TxHeader.TransmitGlobalTime = DISABLE;

	if (HAL_CAN_AddTxMessage(&hcan2, &TxHeader, data, &TxMailbox) != HAL_OK)
	{
		periph_error = PE_CAN2_TX_ERROR;
		return;
	}
	
	uint64_t timeout = 0;
	while (HAL_CAN_IsTxMessagePending(&hcan2, TxMailbox) == 1)
	{
		timeout++;
		if (timeout > 1000000)
		{
			periph_error = PE_CAN2_TX_ERROR;
			// Error_Handler();
			break;
		}
	}
}

HAL_StatusTypeDef CAN_Send_Nonblocking(uint32_t id, uint8_t *data, uint8_t length)
{
	CAN_TxHeaderTypeDef TxHeader;
	uint32_t TxMailbox;

	TxHeader.StdId = id;
	TxHeader.ExtId = 0;
	TxHeader.IDE = CAN_ID_STD;
	TxHeader.RTR = CAN_RTR_DATA;
	TxHeader.DLC = length;
	TxHeader.TransmitGlobalTime = DISABLE;

	uint32_t timeout = HAL_GetTick();
	while (HAL_CAN_GetTxMailboxesFreeLevel(&hcan2) == 0)
	{
		if (HAL_GetTick() - timeout > 100)
		{
			periph_error = PE_CAN2_TX_ERROR;
			return HAL_BUSY;	
		}
	}

	return HAL_CAN_AddTxMessage(&hcan2, &TxHeader, data, &TxMailbox);
}

uint8_t CAN_RxFlag()
{
	if (HAL_CAN_GetRxFifoFillLevel(&hcan2, CAN_RX_FIFO0) > 0)
		return 1;
	return 0;
}

HAL_StatusTypeDef CAN_Receive(uint32_t *id, uint8_t *len, uint8_t *data)
{
	CAN_RxHeaderTypeDef CAN_RxHeader;
	HAL_StatusTypeDef state = HAL_CAN_GetRxMessage(&hcan2, CAN_RX_FIFO0, &CAN_RxHeader, data);

	if (state != HAL_OK)
	{
		return state;
	}

	if (CAN_RxHeader.IDE == CAN_ID_STD)
	{
		*id = CAN_RxHeader.StdId;
	}
	else
	{
		*id = CAN_RxHeader.ExtId;
	}

	if (CAN_RxHeader.RTR == CAN_RTR_DATA)
	{
		*len = CAN_RxHeader.DLC;
	}
	else
	{
		*len = 0;
	}

	return state;
}
/* USER CODE END 1 */

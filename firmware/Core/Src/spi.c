/* USER CODE BEGIN Header */
/**
 ******************************************************************************
 * @file    spi.c
 * @brief   This file provides code for the configuration
 *          of the SPI instances.
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
#include "spi.h"

/* USER CODE BEGIN 0 */
#define SPI1_DMA_IDLE 0
#define SPI1_DMA_BUSY 1

uint8_t spi1_rx_dma_state = SPI1_DMA_IDLE;
uint8_t spi1_tx_dma_state = SPI1_DMA_IDLE;

HAL_StatusTypeDef SPI_WaitTx();
HAL_StatusTypeDef SPI_WaitRx();

void (*spi_cplt_cs_callback)() = NULL;

/* USER CODE END 0 */

SPI_HandleTypeDef hspi1;
DMA_HandleTypeDef hdma_spi1_rx;
DMA_HandleTypeDef hdma_spi1_tx;

/* SPI1 init function */
void MX_SPI1_Init(void)
{

  /* USER CODE BEGIN SPI1_Init 0 */

  /* USER CODE END SPI1_Init 0 */

  /* USER CODE BEGIN SPI1_Init 1 */

  /* USER CODE END SPI1_Init 1 */
  hspi1.Instance = SPI1;
  hspi1.Init.Mode = SPI_MODE_MASTER;
  hspi1.Init.Direction = SPI_DIRECTION_2LINES;
  hspi1.Init.DataSize = SPI_DATASIZE_8BIT;
  hspi1.Init.CLKPolarity = SPI_POLARITY_LOW;
  hspi1.Init.CLKPhase = SPI_PHASE_1EDGE;
  hspi1.Init.NSS = SPI_NSS_SOFT;
  hspi1.Init.BaudRatePrescaler = SPI_BAUDRATEPRESCALER_2;
  hspi1.Init.FirstBit = SPI_FIRSTBIT_MSB;
  hspi1.Init.TIMode = SPI_TIMODE_DISABLE;
  hspi1.Init.CRCCalculation = SPI_CRCCALCULATION_DISABLE;
  hspi1.Init.CRCPolynomial = 10;
  if (HAL_SPI_Init(&hspi1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN SPI1_Init 2 */
	HAL_SPI_MspInit(&hspi1);
  /* USER CODE END SPI1_Init 2 */

}

void HAL_SPI_MspInit(SPI_HandleTypeDef* spiHandle)
{

  GPIO_InitTypeDef GPIO_InitStruct = {0};
  if(spiHandle->Instance==SPI1)
  {
  /* USER CODE BEGIN SPI1_MspInit 0 */

  /* USER CODE END SPI1_MspInit 0 */
    /* SPI1 clock enable */
    __HAL_RCC_SPI1_CLK_ENABLE();

    __HAL_RCC_GPIOA_CLK_ENABLE();
    /**SPI1 GPIO Configuration
    PA5     ------> SPI1_SCK
    PA6     ------> SPI1_MISO
    PA7     ------> SPI1_MOSI
    */
    GPIO_InitStruct.Pin = GPIO_PIN_5|GPIO_PIN_6|GPIO_PIN_7;
    GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
    GPIO_InitStruct.Pull = GPIO_PULLUP;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
    GPIO_InitStruct.Alternate = GPIO_AF5_SPI1;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

    /* SPI1 DMA Init */
    /* SPI1_RX Init */
    hdma_spi1_rx.Instance = DMA2_Stream2;
    hdma_spi1_rx.Init.Channel = DMA_CHANNEL_3;
    hdma_spi1_rx.Init.Direction = DMA_PERIPH_TO_MEMORY;
    hdma_spi1_rx.Init.PeriphInc = DMA_PINC_DISABLE;
    hdma_spi1_rx.Init.MemInc = DMA_MINC_ENABLE;
    hdma_spi1_rx.Init.PeriphDataAlignment = DMA_PDATAALIGN_BYTE;
    hdma_spi1_rx.Init.MemDataAlignment = DMA_MDATAALIGN_BYTE;
    hdma_spi1_rx.Init.Mode = DMA_NORMAL;
    hdma_spi1_rx.Init.Priority = DMA_PRIORITY_MEDIUM;
    hdma_spi1_rx.Init.FIFOMode = DMA_FIFOMODE_ENABLE;
    hdma_spi1_rx.Init.FIFOThreshold = DMA_FIFO_THRESHOLD_FULL;
    hdma_spi1_rx.Init.MemBurst = DMA_MBURST_SINGLE;
    hdma_spi1_rx.Init.PeriphBurst = DMA_PBURST_SINGLE;
    if (HAL_DMA_Init(&hdma_spi1_rx) != HAL_OK)
    {
      Error_Handler();
    }

    __HAL_LINKDMA(spiHandle,hdmarx,hdma_spi1_rx);

    /* SPI1_TX Init */
    hdma_spi1_tx.Instance = DMA2_Stream3;
    hdma_spi1_tx.Init.Channel = DMA_CHANNEL_3;
    hdma_spi1_tx.Init.Direction = DMA_MEMORY_TO_PERIPH;
    hdma_spi1_tx.Init.PeriphInc = DMA_PINC_DISABLE;
    hdma_spi1_tx.Init.MemInc = DMA_MINC_ENABLE;
    hdma_spi1_tx.Init.PeriphDataAlignment = DMA_PDATAALIGN_BYTE;
    hdma_spi1_tx.Init.MemDataAlignment = DMA_MDATAALIGN_BYTE;
    hdma_spi1_tx.Init.Mode = DMA_NORMAL;
    hdma_spi1_tx.Init.Priority = DMA_PRIORITY_MEDIUM;
    hdma_spi1_tx.Init.FIFOMode = DMA_FIFOMODE_ENABLE;
    hdma_spi1_tx.Init.FIFOThreshold = DMA_FIFO_THRESHOLD_FULL;
    hdma_spi1_tx.Init.MemBurst = DMA_MBURST_SINGLE;
    hdma_spi1_tx.Init.PeriphBurst = DMA_PBURST_SINGLE;
    if (HAL_DMA_Init(&hdma_spi1_tx) != HAL_OK)
    {
      Error_Handler();
    }

    __HAL_LINKDMA(spiHandle,hdmatx,hdma_spi1_tx);

    /* SPI1 interrupt Init */
    HAL_NVIC_SetPriority(SPI1_IRQn, 2, 0);
    HAL_NVIC_EnableIRQ(SPI1_IRQn);
  /* USER CODE BEGIN SPI1_MspInit 1 */

  /* USER CODE END SPI1_MspInit 1 */
  }
}

void HAL_SPI_MspDeInit(SPI_HandleTypeDef* spiHandle)
{

  if(spiHandle->Instance==SPI1)
  {
  /* USER CODE BEGIN SPI1_MspDeInit 0 */

  /* USER CODE END SPI1_MspDeInit 0 */
    /* Peripheral clock disable */
    __HAL_RCC_SPI1_CLK_DISABLE();

    /**SPI1 GPIO Configuration
    PA5     ------> SPI1_SCK
    PA6     ------> SPI1_MISO
    PA7     ------> SPI1_MOSI
    */
    HAL_GPIO_DeInit(GPIOA, GPIO_PIN_5|GPIO_PIN_6|GPIO_PIN_7);

    /* SPI1 DMA DeInit */
    HAL_DMA_DeInit(spiHandle->hdmarx);
    HAL_DMA_DeInit(spiHandle->hdmatx);

    /* SPI1 interrupt Deinit */
    HAL_NVIC_DisableIRQ(SPI1_IRQn);
  /* USER CODE BEGIN SPI1_MspDeInit 1 */

  /* USER CODE END SPI1_MspDeInit 1 */
  }
}

/* USER CODE BEGIN 1 */
HAL_StatusTypeDef SPI_SwapBytes(uint8_t *sent_bytes, uint8_t *recv_bytes, uint16_t size)
{
	return HAL_SPI_TransmitReceive(&hspi1, sent_bytes, recv_bytes, size, 100);
}

HAL_StatusTypeDef SPI_SendBytes(uint8_t *sent_bytes, uint16_t size)
{
	return HAL_SPI_Transmit(&hspi1, sent_bytes, size, 100);
}

HAL_StatusTypeDef SPI_RecvBytes(uint8_t *recv_bytes, uint16_t size)
{
	return HAL_SPI_Receive(&hspi1, recv_bytes, size, 100);
}

HAL_StatusTypeDef SPI_SendBytes_DMA(uint8_t *sent_bytes, uint16_t size)
{
  if (SPI_WaitTx() != HAL_OK)
    return HAL_BUSY;
  spi1_tx_dma_state = SPI1_DMA_BUSY;
  HAL_StatusTypeDef state = HAL_SPI_Transmit_DMA(&hspi1, sent_bytes, size);
  if (state != HAL_OK)
  {
    spi1_tx_dma_state = SPI1_DMA_IDLE;
    periph_error = PE_SPI1_TX_ERROR;
  }
  return state;
}

HAL_StatusTypeDef SPI_RecvBytes_DMA(uint8_t *recv_bytes, uint16_t size)
{
  if (SPI_WaitRx() != HAL_OK)
    return HAL_BUSY;
  spi1_rx_dma_state = SPI1_DMA_BUSY;
  HAL_StatusTypeDef state = HAL_SPI_Receive_DMA(&hspi1, recv_bytes, size);
  if (state != HAL_OK)
  {
    spi1_rx_dma_state = SPI1_DMA_IDLE;
    periph_error = PE_SPI1_RX_ERROR;
  }
  return state;
}

HAL_StatusTypeDef SPI_SwapBytes_DMA(uint8_t *sent_bytes, uint8_t *recv_bytes, uint16_t size)
{
  if (SPI_WaitTx() != HAL_OK || SPI_WaitRx() != HAL_OK)
    return HAL_BUSY;

  spi1_tx_dma_state = SPI1_DMA_BUSY;
  spi1_rx_dma_state = SPI1_DMA_BUSY;

  HAL_StatusTypeDef state = HAL_SPI_TransmitReceive_DMA(&hspi1, sent_bytes, recv_bytes, size);

  if (state != HAL_OK)
  {
    spi1_tx_dma_state = SPI1_DMA_IDLE;
    spi1_rx_dma_state = SPI1_DMA_IDLE;
    periph_error = PE_SPI1_TXRX_ERROR;
  }

  return state;
}

// PRIVATE
void HAL_SPI_TxCpltCallback(SPI_HandleTypeDef *hspi)
{
  if (hspi->Instance == SPI1)
  {
    spi1_tx_dma_state = SPI1_DMA_IDLE;
    spi_cplt_cs_callback();
  }
}

void HAL_SPI_RxCpltCallback(SPI_HandleTypeDef *hspi)
{
  if (hspi->Instance == SPI1)
  {
    spi1_rx_dma_state = SPI1_DMA_IDLE;
    spi_cplt_cs_callback();
  }
}

HAL_StatusTypeDef SPI_WaitTx()
{
  uint32_t timeout = HAL_GetTick();
  while (spi1_tx_dma_state != SPI1_DMA_IDLE)
  {
    if (HAL_GetTick() - timeout > 500)
      return HAL_BUSY;
  }

  return HAL_OK;
}

HAL_StatusTypeDef SPI_WaitRx()
{
  uint32_t timeout = HAL_GetTick();
  while (spi1_rx_dma_state != SPI1_DMA_IDLE)
  {
    if (HAL_GetTick() - timeout > 500)
      return HAL_BUSY;
  }

  return HAL_OK;
}
/* USER CODE END 1 */

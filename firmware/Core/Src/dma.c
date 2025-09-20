/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file    dma.c
  * @brief   This file provides code for the configuration
  *          of all the requested memory to memory DMA transfers.
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
#include "dma.h"

/* USER CODE BEGIN 0 */
/* USER CODE END 0 */

/*----------------------------------------------------------------------------*/
/* Configure DMA                                                              */
/*----------------------------------------------------------------------------*/

/* USER CODE BEGIN 1 */
#define DMA2_STREAM0_IDLE 0
#define DMA2_STREAM0_BUSY 1
volatile uint8_t dma2_stream0_state = DMA2_STREAM0_IDLE;

void DMA_XferCpltCallback(DMA_HandleTypeDef *hdma);
void DMA_XferErrorCallback(DMA_HandleTypeDef *hdma);

/*
  初始化DMA时，需要额外设置中断函数
  hdma_memtomem_dma2_stream0.XferCpltCallback = DMA_XferCpltCallback;
  hdma_memtomem_dma2_stream0.XferErrorCallback = DMA_XferErrorCallback;
*/

/* USER CODE END 1 */
DMA_HandleTypeDef hdma_memtomem_dma2_stream0 = {0};

/**
  * Enable DMA controller clock
  * Configure DMA for memory to memory transfers
  *   hdma_memtomem_dma2_stream0
  */
void MX_DMA_Init(void)
{

  /* DMA controller clock enable */
  __HAL_RCC_DMA1_CLK_ENABLE();
  __HAL_RCC_DMA2_CLK_ENABLE();

  /* Configure DMA request hdma_memtomem_dma2_stream0 on DMA2_Stream0 */
  hdma_memtomem_dma2_stream0.Instance = DMA2_Stream0;
  hdma_memtomem_dma2_stream0.Init.Channel = DMA_CHANNEL_0;
  hdma_memtomem_dma2_stream0.Init.Direction = DMA_MEMORY_TO_MEMORY;
  hdma_memtomem_dma2_stream0.Init.PeriphInc = DMA_PINC_ENABLE;
  hdma_memtomem_dma2_stream0.Init.MemInc = DMA_MINC_ENABLE;
  hdma_memtomem_dma2_stream0.Init.PeriphDataAlignment = DMA_PDATAALIGN_BYTE;
  hdma_memtomem_dma2_stream0.Init.MemDataAlignment = DMA_MDATAALIGN_BYTE;
  hdma_memtomem_dma2_stream0.Init.Mode = DMA_NORMAL;
  hdma_memtomem_dma2_stream0.Init.Priority = DMA_PRIORITY_LOW;
  hdma_memtomem_dma2_stream0.Init.FIFOMode = DMA_FIFOMODE_ENABLE;
  hdma_memtomem_dma2_stream0.Init.FIFOThreshold = DMA_FIFO_THRESHOLD_FULL;
  hdma_memtomem_dma2_stream0.Init.MemBurst = DMA_MBURST_SINGLE;
  hdma_memtomem_dma2_stream0.Init.PeriphBurst = DMA_PBURST_SINGLE;
  hdma_memtomem_dma2_stream0.XferCpltCallback = DMA_XferCpltCallback;
  hdma_memtomem_dma2_stream0.XferErrorCallback = DMA_XferErrorCallback;
  if (HAL_DMA_Init(&hdma_memtomem_dma2_stream0) != HAL_OK)
  {
    Error_Handler();
  }

  /* DMA interrupt init */
  /* DMA1_Stream4_IRQn interrupt configuration */
  HAL_NVIC_SetPriority(DMA1_Stream4_IRQn, 1, 0);
  HAL_NVIC_EnableIRQ(DMA1_Stream4_IRQn);
  /* DMA2_Stream0_IRQn interrupt configuration */
  HAL_NVIC_SetPriority(DMA2_Stream0_IRQn, 1, 0);
  HAL_NVIC_EnableIRQ(DMA2_Stream0_IRQn);
  /* DMA2_Stream2_IRQn interrupt configuration */
  HAL_NVIC_SetPriority(DMA2_Stream2_IRQn, 1, 0);
  HAL_NVIC_EnableIRQ(DMA2_Stream2_IRQn);
  /* DMA2_Stream3_IRQn interrupt configuration */
  HAL_NVIC_SetPriority(DMA2_Stream3_IRQn, 1, 0);
  HAL_NVIC_EnableIRQ(DMA2_Stream3_IRQn);

}

/* USER CODE BEGIN 2 */
HAL_StatusTypeDef DMA2_Stream0_MemToMem_Start(void *psrc, void *pdst, uint32_t len)
{
  if (DMA2_Stream0_Wait() != HAL_OK)
    return HAL_BUSY;
  HAL_StatusTypeDef state = HAL_DMA_Start_IT(&hdma_memtomem_dma2_stream0, (uint32_t)psrc, (uint32_t)pdst, len);
  if (state == HAL_OK)
  {
    dma2_stream0_state = DMA2_STREAM0_BUSY;
  }
  return state;
}

void DMA_XferCpltCallback(DMA_HandleTypeDef *hdma)
{
  if (hdma->Instance == DMA2_Stream0)
  {
    dma2_stream0_state = DMA2_STREAM0_IDLE;
  }
}

void DMA_XferErrorCallback(DMA_HandleTypeDef *hdma)
{
  if (hdma->Instance == DMA2_Stream0)
  {
    dma2_stream0_state = DMA2_STREAM0_IDLE;
    periph_error = PE_DMA_ERROR;
    HAL_DMA_Abort(hdma);
  }
}

HAL_StatusTypeDef DMA2_Stream0_Wait()
{
  uint32_t timeout = HAL_GetTick();
  while (dma2_stream0_state == DMA2_STREAM0_BUSY)
  {
    if (HAL_GetTick() - timeout > 100)
    {
      return HAL_BUSY;
    }
  }

  return HAL_OK;
}

/* USER CODE END 2 */


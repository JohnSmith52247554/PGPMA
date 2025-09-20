#ifndef W25Q_H
#define W25Q_H

#include "main.h"

/*
    使用W25Q时，需关闭SPI的CRC校验
*/

HAL_StatusTypeDef W25Q_Init();
HAL_StatusTypeDef W25Q_GetId(uint8_t *manufacturer_id, uint16_t *device_id);
HAL_StatusTypeDef W25Q_SectorErase_4ba(uint32_t addr);
HAL_StatusTypeDef W25Q_BlockErase_64kb_4ba(uint32_t addr);
HAL_StatusTypeDef W25Q_ChipErase();
HAL_StatusTypeDef W25Q_PageProgram_4ba(uint32_t addr, uint8_t *data, uint16_t size);
HAL_StatusTypeDef W25Q_ReadData_4ba(uint32_t addr, uint8_t *data, uint16_t size);
HAL_StatusTypeDef W25Q_WriteEnable();
HAL_StatusTypeDef W25Q_WriteDisable();
HAL_StatusTypeDef W25Q_PageProgram_4ba_DMA(uint32_t addr, uint8_t *data, uint16_t size);
HAL_StatusTypeDef W25Q_ReadData_4ba_DMA(uint32_t addr, uint8_t *data, uint16_t size);
HAL_StatusTypeDef W25Q_WaitBusy(uint32_t timeout);

#endif
#include "W25Q.h"

#include "spi.h"

#include <stdlib.h>

#define W25Q_TIMEOUT 100000

#define CS_W25Q_PIN     GPIO_PIN_4
#define CS_W25Q_GPIO    GPIOC

#define W25Q_DUMMY                      0xFF
#define W25Q_WRITE_ENABLE               0x06
#define W25Q_WRITE_DISABLE              0x04
#define W25Q_JEDEC_ID                   0x9F
#define W25Q_SECTOR_ERASE_4BA           0x21
#define W25Q_BLOCK_ERASE_64KB_4BA       0xDC
#define W25Q_CHIP_ERASE                 0xC7
#define W25Q_READ_STATUS_REGISTER_1     0x05
#define W25Q_PAGE_PROGRAM_4BA           0x12
#define W25Q_READ_DATA_4BA              0x13

void W25Q_CS_Enable();
void W25Q_CS_Disable();
HAL_StatusTypeDef W25Q_SendCmd(uint8_t cmd);
HAL_StatusTypeDef W25Q_WaitBusy(uint32_t timeout);

HAL_StatusTypeDef W25Q_Init()
{
    __HAL_RCC_GPIOC_CLK_ENABLE();

    GPIO_InitTypeDef GPIO_InitStruct;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pin = CS_W25Q_PIN;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_VERY_HIGH;

    HAL_GPIO_Init(CS_W25Q_GPIO, &GPIO_InitStruct);

    HAL_GPIO_WritePin(CS_W25Q_GPIO, CS_W25Q_PIN, GPIO_PIN_SET);

    // 设置回调函数
    spi_cplt_cs_callback = W25Q_CS_Disable;

    return HAL_OK;
}

HAL_StatusTypeDef W25Q_GetId(uint8_t *manufacturer_id, uint16_t *device_id)
{
    uint8_t cmd[] = {W25Q_JEDEC_ID, W25Q_DUMMY, W25Q_DUMMY, W25Q_DUMMY};
    uint8_t buffer[4];
    W25Q_CS_Enable();
    HAL_StatusTypeDef state = SPI_SwapBytes(cmd, buffer, 4);
    W25Q_CS_Disable();
    *manufacturer_id = buffer[1];
    *device_id = (buffer[2] << 8);
    *device_id |= buffer[3];
    return state;
}

HAL_StatusTypeDef W25Q_SectorErase_4ba(uint32_t addr)
{
    if (W25Q_WaitBusy(W25Q_TIMEOUT) != HAL_OK)
        return HAL_BUSY;

    HAL_StatusTypeDef state = W25Q_WriteEnable();
    if (state != HAL_OK)
        return state;

    uint8_t cmd[] = {
        W25Q_SECTOR_ERASE_4BA,
        (addr >> 24),
        (addr >> 16),
        (addr >> 8),
        addr};

    W25Q_CS_Enable();
    state = SPI_SendBytes(cmd, 5);
    W25Q_CS_Disable();

    return state;
}

HAL_StatusTypeDef W25Q_BlockErase_64kb_4ba(uint32_t addr)
{
    if (W25Q_WaitBusy(W25Q_TIMEOUT) != HAL_OK)
        return HAL_BUSY;

    HAL_StatusTypeDef state = W25Q_WriteEnable();
    if (state != HAL_OK)
        return state;

    uint8_t cmd[] = {
        W25Q_BLOCK_ERASE_64KB_4BA,
        (addr >> 24),
        (addr >> 16),
        (addr >> 8),
        addr
    };

    W25Q_CS_Enable();
    state = SPI_SendBytes(cmd, 5);
    W25Q_CS_Disable();

    return state;
}

HAL_StatusTypeDef W25Q_ChipErase()
{
    if (W25Q_WaitBusy(W25Q_TIMEOUT) != HAL_OK)
        return HAL_BUSY;
    HAL_StatusTypeDef state = W25Q_WriteEnable();
    if (state != HAL_OK)
        return state;
    return W25Q_SendCmd(W25Q_CHIP_ERASE);
}

HAL_StatusTypeDef W25Q_PageProgram_4ba(uint32_t addr, uint8_t *data, uint16_t size)
{
    if (W25Q_WaitBusy(W25Q_TIMEOUT) != HAL_OK)
        return HAL_BUSY;
        
    HAL_StatusTypeDef state = W25Q_WriteEnable();
    if (state != HAL_OK)
        return state;

    uint8_t cmd[] = {
        W25Q_PAGE_PROGRAM_4BA,
        (addr >> 24),
        (addr >> 16),
        (addr >> 8),
        addr
    };

    W25Q_CS_Enable();
    state = SPI_SendBytes(cmd, 5);
    if (state != HAL_OK)
        return state;
    state = SPI_SendBytes(data, size);
    W25Q_CS_Disable();


    return state;
}

// 此函数使用DMA传输，需要保证data的生命周期
HAL_StatusTypeDef W25Q_PageProgram_4ba_DMA(uint32_t addr, uint8_t *data, uint16_t size)
{
    if (W25Q_WaitBusy(W25Q_TIMEOUT) != HAL_OK)
        return HAL_BUSY;

    HAL_StatusTypeDef state = W25Q_WriteEnable();
    if (state != HAL_OK)
        return state;

    uint8_t cmd[] = {
        W25Q_PAGE_PROGRAM_4BA,
        (addr >> 24),
        (addr >> 16),
        (addr >> 8),
        addr
    };

    W25Q_CS_Enable();
    state = SPI_SendBytes(cmd, 5);
    if (state != HAL_OK)
        return state;
    state = SPI_SendBytes_DMA(data, size);
    // W25Q_CS_Disable();   此函数在回调中调用

    return state;
}

HAL_StatusTypeDef W25Q_ReadData_4ba(uint32_t addr, uint8_t *data, uint16_t size)
{
    if (W25Q_WaitBusy(W25Q_TIMEOUT) != HAL_OK)
        return HAL_BUSY;

    uint8_t cmd[] = {
        W25Q_READ_DATA_4BA,
        (addr >> 24),
        (addr >> 16),
        (addr >> 8),
        addr
    };

    W25Q_CS_Enable();
    HAL_StatusTypeDef state = SPI_SendBytes(cmd, 5);
    if (state != HAL_OK)
        return state;
    // HAL_Delay(10);
    state = SPI_RecvBytes(data, size);
    W25Q_CS_Disable();

    return state;
}

// 此函数使用DMA传输，需要保证data的生命周期
// 需配合SPI_WaitRx使用
HAL_StatusTypeDef W25Q_ReadData_4ba_DMA(uint32_t addr, uint8_t *data, uint16_t size)
{
    if (W25Q_WaitBusy(W25Q_TIMEOUT) != HAL_OK)
        return HAL_BUSY;

    uint8_t cmd[] = {
        W25Q_READ_DATA_4BA,
        (addr >> 24),
        (addr >> 16),
        (addr >> 8),
        addr};

    W25Q_CS_Enable();
    HAL_StatusTypeDef state = SPI_SendBytes(cmd, 5);
    if (state != HAL_OK)
        return state;
    // HAL_Delay(10);

    state = SPI_RecvBytes_DMA(data, size);
    // W25Q_CS_Disable(); 此函数在回调中调用

    return state;
}

HAL_StatusTypeDef W25Q_WriteEnable()
{
    return W25Q_SendCmd(W25Q_WRITE_ENABLE);
}

HAL_StatusTypeDef W25Q_WriteDisable()
{
    return W25Q_SendCmd(W25Q_WRITE_DISABLE);
}


// PRIVATE
void W25Q_CS_Enable()
{
    HAL_GPIO_WritePin(CS_W25Q_GPIO, CS_W25Q_PIN, GPIO_PIN_RESET);
}

void W25Q_CS_Disable()
{
    HAL_GPIO_WritePin(CS_W25Q_GPIO, CS_W25Q_PIN, GPIO_PIN_SET);
}

HAL_StatusTypeDef W25Q_SendCmd(uint8_t cmd)
{
    W25Q_CS_Enable();
    HAL_StatusTypeDef state = SPI_SendBytes(&cmd, 1);
    W25Q_CS_Disable();
    return state;
}

HAL_StatusTypeDef W25Q_WaitBusy(uint32_t timeout)
{
    uint32_t timeout_ = 0;
    uint8_t cmd = W25Q_READ_STATUS_REGISTER_1;
    uint8_t buffer = 0;
    W25Q_CS_Enable();
    SPI_SendBytes(&cmd, 1);

    while (1)
    {
        if (SPI_RecvBytes(&buffer, 1) != HAL_OK)
            return HAL_BUSY;
        timeout_++;
        if ((buffer & 0x01) == 0x00 || timeout_ >= timeout)
            break;
    }

    W25Q_CS_Disable();

    if (timeout_ >= timeout)
        return HAL_BUSY;
    else
        return HAL_OK;
}
#include "ADS1115.h"

#include "i2c.h"

#define ADS1115_ADDR 0x90

#define ADS1115_CONSERSION_REG 0x00
#define ADS1115_CONFIG_REG 0x01

HAL_StatusTypeDef ADS1115_Config()
{
    ADS1115_InitTypeDef ADS1115_InitStruct;
    ADS1115_InitStruct.OS = ADS1115_OS_NO_EFFECT;
    ADS1115_InitStruct.MUX = ADS1115_MUX_CHANNEL_0;
    ADS1115_InitStruct.PGA = ADS1115_PGA_4096;
    ADS1115_InitStruct.MODE = ADS1115_MODE_CONTINUE_CONVERSION;
    ADS1115_InitStruct.DR = ADS1115_DR_64;
    ADS1115_InitStruct.COMP_MODE = ADS1115_COMP_MODE_TRADITIONAL;
    ADS1115_InitStruct.COMP_POL = ADS1115_COMP_POL_LOW;
    ADS1115_InitStruct.COMP_LAT = ADS1115_COMP_LAT_NONLATCHING;
    ADS1115_InitStruct.COMP_QUE = ADS1115_COMP_QUE_DISABLE;

    return ADS1115_Init(&ADS1115_InitStruct);
}

HAL_StatusTypeDef ADS1115_Init(ADS1115_InitTypeDef *ADS1115_Init)
{
    uint16_t config =
        (ADS1115_Init->OS << 15) +
        (ADS1115_Init->MUX << 12) +
        (ADS1115_Init->PGA << 9) +
        (ADS1115_Init->MODE << 8) +
        (ADS1115_Init->DR << 5) +
        (ADS1115_Init->COMP_MODE << 4) +
        (ADS1115_Init->COMP_POL << 3) +
        (ADS1115_Init->COMP_LAT << 2) +
        ADS1115_Init->COMP_QUE;
    uint8_t cmd[] = {ADS1115_CONFIG_REG, (config >> 8) & 0xFF, config & 0xFF};

    return I2C2_Send(ADS1115_ADDR, cmd, 3);
}

HAL_StatusTypeDef ADS1115_ReadContinuous(uint16_t *output)
{
    uint8_t reg = ADS1115_CONSERSION_REG;
    HAL_StatusTypeDef state = I2C2_SendByte(ADS1115_ADDR, &reg);
    if (state != HAL_OK)
        return state;

    uint8_t result[2] = {0, 0};
    state = I2C2_Read(ADS1115_ADDR, result, 2);
    *output = (result[0] << 8) | result[1];

    return state;
}
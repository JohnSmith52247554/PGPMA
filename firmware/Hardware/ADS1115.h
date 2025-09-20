#ifndef ADS1115_H
#define ADS1115_H

#include "main.h"

typedef struct
{
    uint8_t OS;         // bit[15]
    uint8_t MUX;        // bit[14:12]
    uint8_t PGA;        // bit[11:9]
    uint8_t MODE;       // bit[8]
    uint8_t DR;         // bit[7:5]
    uint8_t COMP_MODE;  // bit[4]
    uint8_t COMP_POL;   // bit[3]
    uint8_t COMP_LAT;   // bit[2]
    uint8_t COMP_QUE;   // bit[1:0]
} ADS1115_InitTypeDef;

// ADS1115_InitTypeDef Config
#define ADS1115_OS_NO_EFFECT         0x00
#define ADS1115_OS_SINGLE_CONVERSION 0x01

#define ADS1115_MUX_DIFFER_01 0x00
#define ADS1115_MUX_DIFFER_03 0x01
#define ADS1115_MUX_DIFFER_13 0x02
#define ADS1115_MUX_DIFFER_23 0x03
#define ADS1115_MUX_CHANNEL_0 0x04
#define ADS1115_MUX_CHANNEL_1 0x05
#define ADS1115_MUX_CHANNEL_2 0x06
#define ADS1115_MUX_CHANNEL_3 0x07

#define ADS1115_PGA_6114 0x00
#define ADS1115_PGA_4096 0x01
#define ADS1115_PGA_2048 0x02
#define ADS1115_PGA_1024 0x03
#define ADS1115_PGA_0512 0x04
#define ADS1115_PGA_0256 0x05

#define ADS1115_MODE_CONTINUE_CONVERSION 0x00
#define ADS1115_MODE_SINGLE_CONVERSION   0x01

#define ADS1115_DR_8    0x00
#define ADS1115_DR_16   0x01
#define ADS1115_DR_32   0x02
#define ADS1115_DR_64   0x03
#define ADS1115_DR_128  0x04
#define ADS1115_DR_250  0x05
#define ADS1115_DR_475  0x06
#define ADS1115_DR_860  0x07

#define ADS1115_COMP_MODE_TRADITIONAL 0x00
#define ADS1115_COMP_MODE_WINDOW      0x01

#define ADS1115_COMP_POL_LOW  0x00
#define ADS1115_COMP_POL_HIGH 0x01

#define ADS1115_COMP_LAT_NONLATCHING 0x00
#define ADS1115_COMP_LAT_LATCHING    0x01

#define ADS1115_COMP_QUE_1       0x00
#define ADS1115_COMP_QUE_2       0x01
#define ADS1115_COMP_QUE_3       0x02
#define ADS1115_COMP_QUE_DISABLE 0x03

HAL_StatusTypeDef ADS1115_Config();
HAL_StatusTypeDef ADS1115_Init(ADS1115_InitTypeDef *ADS1115_Init);
HAL_StatusTypeDef ADS1115_ReadContinuous(uint16_t *output);

#endif
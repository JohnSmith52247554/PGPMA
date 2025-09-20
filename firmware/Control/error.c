#include "error.h"

PeripheralErrorTypeDef periph_error = PE_NO_ERROR;
HardwareErrorTypeDef hardware_error = HE_NO_ERROR;

const char *Error_GetPeriphErrorStr(PeripheralErrorTypeDef error_code)
{
    switch (error_code)
    {
    case PE_NO_ERROR:
        return "NO ERROR";
    case PE_DMA_ERROR:
        return "DMA ERROR";
    case PE_CAN2_TX_ERROR:
        return "CAN2 TX ERROR";
    case PE_CAN2_RX_ERROR:
        return "CAN2 RX ERROR";
    case PE_I2C2_TX_ERROR:
        return "I2C2 TX ERROR";
    case PE_I2C2_RX_ERROR:
        return "I2C2 RX ERROR";
    case PE_I2C3_TX_ERROR:
        return "I2C3 TX ERROR";
    case PE_I2C3_RX_ERROR:
        return "I2C3 RX ERROR";
    case PE_SPI1_TX_ERROR:
        return "SPI1 TX ERROR";
    case PE_SPI1_RX_ERROR:
        return "SPI1 RX ERROR";
    case PE_SPI1_TXRX_ERROR:
        return "SPI1 TXRX ERROR";
    case PE_USART3_TX_ERROR:
        return "USART3 TX ERROR";
    case PE_USART3_RX_ERROR:
        return "USART3 RX ERROR";
    case PE_OTG_FS_TX_ERROR:
        return "OTG FS TX ERROR";
    case PE_OTG_FS_RX_ERROR:
        return "OTG FS RX ERROR";
    default:
        return "UNKNOWN ERROR";
    }
}

const char *Error_GetHardwareErrorStr(HardwareErrorTypeDef error_code)
{
    switch (error_code)
    {
    case HE_NO_ERROR:
        return "NO ERROR";
    case HE_ADS1115_ERROR:
        return "ADS1115 ERROR";
    case HE_MS42D_ERROR:
        return "MS42D ERROR";
    case HE_OLED_ERROR:
        return "OLED ERROR";
    case HE_SERVO_ERROR:
        return "SERVO ERROR";
    case HE_W25Q_ERROR:
        return "W25Q256 ERROR";
    default:
        return "UNKNOWN ERROR";
    }
}
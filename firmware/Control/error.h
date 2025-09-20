#ifndef __ERROR_H
#define __ERROR_H

typedef enum
{
    // 无错误
    PE_NO_ERROR = 0,

    // 外设错误
    PE_DMA_ERROR,
    PE_CAN2_TX_ERROR,
    PE_CAN2_RX_ERROR,
    PE_I2C2_TX_ERROR,
    PE_I2C2_RX_ERROR,
    PE_I2C3_TX_ERROR,
    PE_I2C3_RX_ERROR,
    PE_SPI1_TX_ERROR,
    PE_SPI1_RX_ERROR,
    PE_SPI1_TXRX_ERROR,
    PE_USART3_TX_ERROR,
    PE_USART3_RX_ERROR,
    PE_OTG_FS_TX_ERROR,
    PE_OTG_FS_RX_ERROR,
    PE_ADC_ERROR,

} PeripheralErrorTypeDef;

typedef enum
{
    // 无错误
    HE_NO_ERROR = 0,

    // 硬件错误
    HE_ADS1115_ERROR,
    HE_MS42D_ERROR,
    HE_OLED_ERROR,
    HE_SERVO_ERROR,
    HE_W25Q_ERROR,
}
HardwareErrorTypeDef;

extern PeripheralErrorTypeDef periph_error;
extern HardwareErrorTypeDef hardware_error;

const char *Error_GetPeriphErrorStr(PeripheralErrorTypeDef error_code);
const char *Error_GetHardwareErrorStr(HardwareErrorTypeDef error_code);

#endif
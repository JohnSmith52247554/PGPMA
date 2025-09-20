#include "OLED.h"

#include "main.h"

#include "OLED_Font.h"
#include "i2c.h"

#define OLED_ADDR 0x78

void OLED_WriteCommand(uint8_t cmd)
{
    __attribute__((aligned(4))) static uint8_t c[] = {0x00, 0xFF};
    c[1] = cmd;

    if (I2C3_Send_DMA(OLED_ADDR, c, 2) != HAL_OK)
    {
        Error_Handler();
    }
}

void OLED_WriteData(uint8_t data)
{
    __attribute__((aligned(4))) static uint8_t c[] = {0x40, 0xFF};
    c[1] = data;
    if (I2C3_Send_DMA(OLED_ADDR, c, 2) != HAL_OK)
    {
        Error_Handler();
    }
}

void OLED_Init()
{
    OLED_WriteCommand(0xAE); // 关闭显示

    OLED_WriteCommand(0xD5); // 设置显示时钟分频比/振荡器频率
    OLED_WriteCommand(0x80);

    OLED_WriteCommand(0xA8); // 设置多路复用率
    OLED_WriteCommand(0x3F);

    OLED_WriteCommand(0xD3); // 设置显示偏移
    OLED_WriteCommand(0x00);

    OLED_WriteCommand(0x40); // 设置显示开始行

    OLED_WriteCommand(0xA1); // 设置左右方向，0xA1正常 0xA0左右反置

    OLED_WriteCommand(0xC8); // 设置上下方向，0xC8正常 0xC0上下反置

    OLED_WriteCommand(0xDA); // 设置COM引脚硬件配置
    OLED_WriteCommand(0x12);

    OLED_WriteCommand(0x81); // 设置对比度控制
    OLED_WriteCommand(0xCF);

    OLED_WriteCommand(0xD9); // 设置预充电周期
    OLED_WriteCommand(0xF1);

    OLED_WriteCommand(0xDB); // 设置VCOMH取消选择级别
    OLED_WriteCommand(0x30);

    OLED_WriteCommand(0xA4); // 设置整个显示打开/关闭

    OLED_WriteCommand(0xA6); // 设置正常/倒转显示

    OLED_WriteCommand(0x8D); // 设置充电泵
    OLED_WriteCommand(0x14);

    OLED_WriteCommand(0xAF); // 开启显示

    OLED_Clear();
}

void OLED_SetCursor(uint8_t Y, uint8_t X)
{
    __attribute__((aligned(4))) static uint8_t cmd[] = {0x00, 0xFF, 0xFF, 0xFF};
    cmd[1] = 0xB0 | Y;
    cmd[2] = 0x10 | ((X & 0xF0) >> 4);
    cmd[3] = 0x00 | (X & 0x0F);
    if (I2C3_Send_DMA(OLED_ADDR, cmd, 4) != HAL_OK)
        Error_Handler();
        
    // OLED_WriteCommand(0xB0 | Y);                 // 设置Y位置
    // OLED_WriteCommand(0x10 | ((X & 0xF0) >> 4)); // 设置X位置高4位
    // OLED_WriteCommand(0x00 | (X & 0x0F));        // 设置X位置低4位
}

void OLED_Clear(void)
{
    uint8_t i, j;
    __attribute__((aligned(4))) static uint8_t cmd[65] = {0x00};
    cmd[0] = 0x40;

    for (j = 0; j < 8; j++)
    {
        OLED_SetCursor(j, 0);
        for (i = 0; i < 2; i++)
        {
            I2C3_Send_DMA(OLED_ADDR, cmd, 65);
        }
    }
}

void OLED_ShowChar(uint8_t Line, uint8_t Column, char Char)
{
    OLED_SetCursor((Line - 1) * 2, (Column - 1) * 8); // 设置光标位置在上半部分
    static uint8_t cmd[] = {
        0x40, 
        0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    };
    for (uint8_t i = 0; i < 8; i++)
    {
        cmd[i + 1] = OLED_F8x16[Char - ' '][i];
    }
    if (I2C3_Send_DMA(OLED_ADDR, cmd, 9) != HAL_OK)
    {
        // Error_Handler();
        periph_error = PE_I2C3_TX_ERROR;
        hardware_error = HE_OLED_ERROR;
    }
    OLED_SetCursor((Line - 1) * 2 + 1, (Column - 1) * 8); // 设置光标位置在下半部分
    for (uint8_t i = 0; i < 8; i++)
    {
        cmd[i + 1] = OLED_F8x16[Char - ' '][i + 8];
    }
    if (I2C3_Send_DMA(OLED_ADDR, cmd, 9) != HAL_OK)
    {
        // Error_Handler();
        periph_error = PE_I2C3_TX_ERROR;
        hardware_error = HE_OLED_ERROR;
    }
}

void OLED_ShowString(uint8_t Line, uint8_t Column, const char *String)
{
    uint8_t i;
    for (i = 0; String[i] != '\0'; i++)
    {
        OLED_ShowChar(Line, Column + i, String[i]);
    }
}

uint32_t OLED_Pow(uint32_t X, uint32_t Y)
{
    uint32_t Result = 1;
    while (Y--)
    {
        Result *= X;
    }
    return Result;
}

// 幂函数优化
// 查表法
uint32_t pow_10_table[] = {
    1,
    10,
    100,
    1000,
    10000,
    100000,
    1000000,
    10000000,
    100000000
};

uint32_t pow_10(uint32_t exp)
{
    if (exp < 9)
        return pow_10_table[exp];
    else
        return OLED_Pow(10, exp);
}

uint32_t pow_16(uint32_t exp)
{
    return 1 << (exp * 4);
}

uint32_t pow_2(uint32_t exp)
{
    return 1 << (exp - 1);
}

void OLED_ShowNum(uint8_t Line, uint8_t Column, uint32_t Number, uint8_t Length)
{
    uint8_t i;
    for (i = 0; i < Length; i++)
    {
        OLED_ShowChar(Line, Column + i, Number / pow_10(Length - i - 1) % 10 + '0');
    }
}

void OLED_ShowSignedNum(uint8_t Line, uint8_t Column, int32_t Number, uint8_t Length)
{
    uint8_t i;
    uint32_t Number1;
    if (Number >= 0)
    {
        OLED_ShowChar(Line, Column, '+');
        Number1 = Number;
    }
    else
    {
        OLED_ShowChar(Line, Column, '-');
        Number1 = -Number;
    }
    for (i = 0; i < Length; i++)
    {
        OLED_ShowChar(Line, Column + i + 1, Number1 / pow_10(Length - i - 1) % 10 + '0');
    }
}

void OLED_ShowHexNum(uint8_t Line, uint8_t Column, uint32_t Number, uint8_t Length)
{
    uint8_t i, SingleNumber;
    for (i = 0; i < Length; i++)
    {
        SingleNumber = Number / pow_16(Length - i - 1) % 16;
        if (SingleNumber < 10)
        {
            OLED_ShowChar(Line, Column + i, SingleNumber + '0');
        }
        else
        {
            OLED_ShowChar(Line, Column + i, SingleNumber - 10 + 'A');
        }
    }
}

void OLED_ShowBinNum(uint8_t Line, uint8_t Column, uint32_t Number, uint8_t Length)
{
    uint8_t i;
    for (i = 0; i < Length; i++)
    {
        OLED_ShowChar(Line, Column + i, Number / pow_2(Length - i - 1) % 2 + '0');
    }
}

void OLED_ShowFloatNum(uint8_t Line, uint8_t Column, float Number, uint8_t IntLength, uint8_t FracLength)
{
    uint8_t i;
    int32_t IntPart;
    uint32_t FracPart;

    // 处理符号
    if (Number >= 0)
    {
        OLED_ShowChar(Line, Column, '+');
    }
    else
    {
        OLED_ShowChar(Line, Column, '-');
        Number = -Number;
    }

    // 分离整数和小数部分
    IntPart = (int32_t)Number;
    FracPart = (uint32_t)((Number - IntPart) * pow_10(FracLength));

    // 显示整数部分
    for (i = 0; i < IntLength; i++)
    {
        OLED_ShowChar(Line, Column + 1 + i, IntPart / pow_10(IntLength - i - 1) % 10 + '0');
    }

    // 显示小数点
    OLED_ShowChar(Line, Column + 1 + IntLength, '.');

    // 显示小数部分
    for (i = 0; i < FracLength; i++)
    {
        OLED_ShowChar(Line, Column + 2 + IntLength + i, FracPart / pow_10(FracLength - i - 1) % 10 + '0');
    }
}
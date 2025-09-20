#ifndef OLED_H
#define OLED_H

#include <stdint.h>

#ifdef __cplusplus
extern "C"
{
#endif
    void OLED_Init();
    void OLED_Clear(void);
    void OLED_ShowChar(uint8_t Line, uint8_t Column, char Char);
    void OLED_ShowString(uint8_t Line, uint8_t Column, const char *String);
    void OLED_ShowNum(uint8_t Line, uint8_t Column, uint32_t Number, uint8_t Length);
    void OLED_ShowSignedNum(uint8_t Line, uint8_t Column, int32_t Number, uint8_t Length);
    void OLED_ShowBinNum(uint8_t Line, uint8_t Column, uint32_t Number, uint8_t Length);
    void OLED_ShowHexNum(uint8_t Line, uint8_t Column, uint32_t Number, uint8_t Length);
    void OLED_ShowFloatNum(uint8_t Line, uint8_t Column, float Number, uint8_t IntLength, uint8_t FracLength);
#ifdef __cplusplus
}
#endif

#endif
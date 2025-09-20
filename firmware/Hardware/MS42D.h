#ifndef MS42D_H
#define MS42D_H

#include <stdint.h>

#ifdef __cplusplus
extern "C"
{
#endif
    /**
     * @brief 控制电机转动的方向，逆时针为正方向
     *
     */
    typedef enum
    {
        MS42D_DIR_ROT_CLOCKWISE = 0x00,
        MS42D_DIR_ROT_ANTICLOCKWISE = 0x01
    } MS42DDirRot;

    typedef struct 
    {
        uint8_t can_id;
        uint8_t has_achieved;
        float speed;
        float angle;
    } MS42D_Info;
    

#define MS42D_MAX_SPEED 43.9f

    void MS42D_Init();
    void MS42D_SetSpeed(uint32_t id, MS42DDirRot direction, float speed);
    void MS42D_SetSpeed2(uint32_t id, float speed);
    void MS42D_SetRelativePos(uint32_t id, MS42DDirRot direction, float speed, float angle);
    void MS42D_SetMoment(uint32_t id, MS42DDirRot direction, float speed, uint16_t current);
    void MS42D_SetAbsolutePos(uint32_t id, float speed, float angle);
    void MS42D_RequestData(uint32_t id);
    // uint8_t MS42D_GetFeedback(uint8_t *motor_id, uint8_t *has_achieved, float *speed, float *angle);
    uint8_t MS42D_GetFeedback(MS42D_Info *info);
#ifdef __cplusplus
}
#endif


#endif
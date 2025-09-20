#ifndef MD5_H
#define MD5_H

#include <stdint.h>

void md5_compute(const uint8_t *data, uint32_t len, uint8_t out16[16]);
uint8_t byteArrCmp(uint8_t *arr_a, uint8_t *arr_b, uint32_t len);

#endif
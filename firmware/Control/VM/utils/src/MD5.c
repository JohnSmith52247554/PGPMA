#include "MD5.h"

#include <stdlib.h>
#include <string.h>
#include <stdint.h>

/* MD5 context structure */
typedef struct
{
    uint32_t state[4];  /* A, B, C, D */
    uint64_t count;     /* number of bits, modulo 2^64 */
    uint8_t buffer[64]; /* input buffer */
} MD5_CTX;

/* Left-rotate a 32-bit value by n bits */
#define LEFTROTATE(x, c) (((x) << (c)) | ((x) >> (32 - (c))))

/* Forward declarations */
void MD5_Init(MD5_CTX *ctx);
void MD5_Update(MD5_CTX *ctx, const uint8_t *data, size_t len);
void MD5_Final(uint8_t digest[16], MD5_CTX *ctx);
void MD5_Transform(uint32_t state[4], const uint8_t block[64]);

/* Constants for MD5Transform (s specifies the per-round shift amounts) */
static const uint32_t T[64] = {
    0xd76aa478ul, 0xe8c7b756ul, 0x242070dbul, 0xc1bdceeeul,
    0xf57c0faful, 0x4787c62aul, 0xa8304613ul, 0xfd469501ul,
    0x698098d8ul, 0x8b44f7aful, 0xffff5bb1ul, 0x895cd7beul,
    0x6b901122ul, 0xfd987193ul, 0xa679438eul, 0x49b40821ul,
    0xf61e2562ul, 0xc040b340ul, 0x265e5a51ul, 0xe9b6c7aaul,
    0xd62f105dul, 0x02441453ul, 0xd8a1e681ul, 0xe7d3fbc8ul,
    0x21e1cde6ul, 0xc33707d6ul, 0xf4d50d87ul, 0x455a14edul,
    0xa9e3e905ul, 0xfcefa3f8ul, 0x676f02d9ul, 0x8d2a4c8aul,
    0xfffa3942ul, 0x8771f681ul, 0x6d9d6122ul, 0xfde5380cul,
    0xa4beea44ul, 0x4bdecfa9ul, 0xf6bb4b60ul, 0xbebfbc70ul,
    0x289b7ec6ul, 0xeaa127faul, 0xd4ef3085ul, 0x04881d05ul,
    0xd9d4d039ul, 0xe6db99e5ul, 0x1fa27cf8ul, 0xc4ac5665ul,
    0xf4292244ul, 0x432aff97ul, 0xab9423a7ul, 0xfc93a039ul,
    0x655b59c3ul, 0x8f0ccc92ul, 0xffeff47dul, 0x85845dd1ul,
    0x6fa87e4ful, 0xfe2ce6e0ul, 0xa3014314ul, 0x4e0811a1ul,
    0xf7537e82ul, 0xbd3af235ul, 0x2ad7d2bbul, 0xeb86d391ul};

/* Initialize MD5 context */
void MD5_Init(MD5_CTX *ctx)
{
    ctx->count = 0;
    /* Load magic initialization constants (RFC 1321) */
    ctx->state[0] = 0x67452301ul;
    ctx->state[1] = 0xefcdab89ul;
    ctx->state[2] = 0x98badcfeul;
    ctx->state[3] = 0x10325476ul;
    memset(ctx->buffer, 0, sizeof(ctx->buffer));
}

/* Process data in blocks of 64 bytes */
void MD5_Update(MD5_CTX *ctx, const uint8_t *data, size_t len)
{
    size_t index = (size_t)((ctx->count / 8) % 64);
    ctx->count += (uint64_t)len * 8;

    size_t partLen = 64 - index;
    size_t i = 0;

    if (len >= partLen)
    {
        memcpy(&ctx->buffer[index], data, partLen);
        MD5_Transform(ctx->state, ctx->buffer);

        for (i = partLen; i + 63 < len; i += 64)
        {
            MD5_Transform(ctx->state, &data[i]);
        }
        index = 0;
    }
    else
    {
        i = 0;
    }

    /* Buffer remaining input */
    if (i < len)
    {
        memcpy(&ctx->buffer[index], &data[i], len - i);
    }
}

/* Finalize and output digest (16 bytes) */
void MD5_Final(uint8_t digest[16], MD5_CTX *ctx)
{
    uint8_t padding[64] = {0x80}; /* 0x80 followed by zeros */
    uint8_t bits[8];
    /* Save number of bits as little-endian 64-bit */
    uint64_t count = ctx->count;
    for (int i = 0; i < 8; i++)
    {
        bits[i] = (uint8_t)(count & 0xFF);
        count >>= 8;
    }

    /* Pad out to 56 mod 64 */
    size_t index = (size_t)((ctx->count / 8) % 64);
    size_t padLen = (index < 56) ? (56 - index) : (120 - index);
    MD5_Update(ctx, padding, padLen);

    /* Append length (before padding) */
    MD5_Update(ctx, bits, 8);

    /* Output state in little-endian */
    for (int i = 0; i < 4; i++)
    {
        uint32_t s = ctx->state[i];
        digest[i * 4 + 0] = (uint8_t)(s & 0xFF);
        digest[i * 4 + 1] = (uint8_t)((s >> 8) & 0xFF);
        digest[i * 4 + 2] = (uint8_t)((s >> 16) & 0xFF);
        digest[i * 4 + 3] = (uint8_t)((s >> 24) & 0xFF);
    }

    /* Zeroize sensitive info */
    memset(ctx, 0, sizeof(*ctx));
}

/* Basic MD5 transformation. Transforms state based on block. */
void MD5_Transform(uint32_t state[4], const uint8_t block[64])
{
    uint32_t a = state[0], b = state[1], c = state[2], d = state[3];
    uint32_t M[16];

    /* Decode block into 16 32-bit words (little-endian) */
    for (int i = 0; i < 16; ++i)
    {
        M[i] = (uint32_t)block[i * 4] |
               ((uint32_t)block[i * 4 + 1] << 8) |
               ((uint32_t)block[i * 4 + 2] << 16) |
               ((uint32_t)block[i * 4 + 3] << 24);
    }

    /* Round shift amounts */
    static const int s[] = {
        7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
        5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20,
        4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
        6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21};

    /* Main loop */
    for (int i = 0; i < 64; ++i)
    {
        uint32_t F, g;
        if (i < 16)
        {
            F = (b & c) | ((~b) & d);
            g = i;
        }
        else if (i < 32)
        {
            F = (d & b) | ((~d) & c);
            g = (5 * i + 1) % 16;
        }
        else if (i < 48)
        {
            F = b ^ c ^ d;
            g = (3 * i + 5) % 16;
        }
        else
        {
            F = c ^ (b | (~d));
            g = (7 * i) % 16;
        }
        uint32_t temp = d;
        d = c;
        c = b;
        uint32_t add = a + F + T[i] + M[g];
        b = b + LEFTROTATE(add, s[i]);
        a = temp;
    }

    state[0] += a;
    state[1] += b;
    state[2] += c;
    state[3] += d;

    /* Clear sensitive data */
    memset(M, 0, sizeof(M));
}

/* Helper: compute MD5 of a memory block */
void md5_compute(const uint8_t *data, size_t len, uint8_t out[16])
{
    MD5_CTX ctx;
    MD5_Init(&ctx);
    MD5_Update(&ctx, (const uint8_t *)data, len);
    MD5_Final(out, &ctx);
}
/**
 * @brief 比较两个字节数组是否相同
 *
 * @return uint8_t 相同返回1，不同返回0
 */
uint8_t byteArrCmp(uint8_t *arr_a, uint8_t *arr_b, uint32_t len)
{
    for (uint32_t i = 0; i < len; i++)
    {
        if (*(arr_a + i) != *(arr_b + i))
            return 0;
    }
    return 1;
}
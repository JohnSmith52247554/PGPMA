#ifndef VM_TYPES_H
#define VM_TYPES_H

#include <stdint.h>

typedef union 
{
    int32_t i32;
    float f32;
} VmSlot;

extern VmSlot slot_zero;
extern VmSlot slot_one;

#define slot_true slot_one
#define slot_false slot_zero

#endif
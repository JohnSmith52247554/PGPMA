#ifndef VM_MEMORY_H
#define VM_MEMORY_H

#include "vm_types.h"

typedef struct 
{
    const uint8_t *program;
    uint16_t program_size;

    const VmSlot *const_variable_area;
    uint16_t const_size;

    VmSlot *global_variable_area;
    uint16_t global_size;

    VmSlot *stack_area;
    uint16_t stack_size;

} VmMemory;





#endif
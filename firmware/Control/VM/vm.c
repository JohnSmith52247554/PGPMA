#include "vm.h"

#include <stdint.h>
#include <stdlib.h>
// #include <memory.h>
#include <string.h>

#include "vm_types.h"
#include "vm_dispatch.h"
#include "vm_memory.h"
#include "vm_stack.h"
#include "vm_status.h"

#include "MD5.h"

#include "W25Q.h"
#include "OLED.h"

#define VM_CONST_MAX_SIZE 4096  // 常量区的最大大小 byte
#define VM_GLOBAL_MAX_SIZE 4096 // 全局变量区的最大大小 byte
#define VM_STACK_MAX_SIZE 4096  // 栈的最大大小 byte

#define PROGRAM_AREA_ADDR 0x01FF3000

int vm_init(Vm *vm, uint8_t *byte_code)
{
    vm->program_counter = 0;
    vm->stack_offset = 0;
    vm->frame_header.return_addr = 0;
    vm->frame_header.frame_offset = 0;
    vm->frame_header.local_size = 0;
    vm->status_code = VM_RUNNING;
    vm->split_op = 0;

    uint8_t *byte_code_begin = byte_code;

    // uint32_t total_size = *(uint32_t *)byte_code;
    uint32_t total_size;
    memcpy(&total_size, byte_code, sizeof(uint32_t));
    byte_code += 4;

    // 检查MD5
    uint8_t *md5_read = byte_code_begin + total_size - 16;
    uint8_t md5_result[16];
    // MD5Run(byte_code_begin, total_size - 16, md5_result);
    md5_compute(byte_code_begin, total_size - 16, md5_result);
    if (byteArrCmp(md5_read, md5_result, 16) == 0)
    {
        return VM_INIT_FILE_DAMAGE;
    }

    // vm->memory.const_size = *(uint16_t *)byte_code;
    memcpy(&vm->memory.const_size, byte_code, sizeof(uint16_t));
    byte_code += 2;
    if (vm->memory.const_size * sizeof(VmSlot) > VM_CONST_MAX_SIZE)
    {
        return VM_INIT_CONST_AREA_TOO_LARGE;
    }
    if (vm->memory.const_size + 6 > total_size)
    {
        return VM_INIT_INVALID_CONST_AREA_SIZE;
    }

    vm->memory.const_variable_area = (VmSlot *)byte_code;

    byte_code += vm->memory.const_size * sizeof(VmSlot);
    // vm->memory.global_size = *(uint16_t *)byte_code;
    memcpy(&vm->memory.global_size, byte_code, sizeof(uint16_t));
    byte_code += 2;
    if (vm->memory.global_size > VM_GLOBAL_MAX_SIZE)
    {
        return VM_INIT_GLOBAL_AREA_TOO_LARGE;
    }

    vm->memory.global_variable_area = (VmSlot *)malloc(vm->memory.global_size * sizeof(VmSlot));
    if (vm->memory.global_variable_area == NULL)
    {
        return VM_INIT_ALLOC_GLOBAL_AREA_FAILED;
    }

    vm->memory.program_size = byte_code_begin + total_size - byte_code - 16;
    vm->memory.program = byte_code;

    vm->memory.stack_area = (VmSlot *)malloc(VM_STACK_MAX_SIZE);
    if (vm->memory.stack_area == NULL)
    {
        return VM_INIT_ALLOC_STACK_FAILED;
    }
    vm->memory.stack_size = VM_STACK_MAX_SIZE / sizeof(VmSlot);

    return VM_INIT_OK;
}

void vm_destory(Vm *vm)
{
    free(vm->memory.global_variable_area);
    free(vm->memory.stack_area);
}

void vm_run(Vm *vm)
{
    while (1)
    {
        vm_dispatch(vm);
        OLED_ShowString(2, 1, VM_GetStatusString(vm->status_code));
        OLED_ShowHexNum(3, 1, vm->program_counter, 8);
        OLED_ShowHexNum(4, 1, vm->stack_offset, 8);
        if (vm->status_code != VM_RUNNING)
        {
            break;
        }
    }
}


int vm_load(Vm *vm, uint8_t *program_ptr)
{
    uint32_t program_size;
    if (W25Q_ReadData_4ba(PROGRAM_AREA_ADDR,(uint8_t *)&program_size, 4) != HAL_OK)
        return VM_INIT_READ_FLASH_FAILED;

    program_ptr = (uint8_t *)malloc(program_size * sizeof(uint8_t));
    if (program_ptr == NULL)
    {
        return VM_INIT_ALLOC_PROGRAM_FAILED;
    }
    if (W25Q_ReadData_4ba(PROGRAM_AREA_ADDR, program_ptr, program_size) != HAL_OK)
        return VM_INIT_READ_FLASH_FAILED;

    return vm_init(vm, program_ptr);
}
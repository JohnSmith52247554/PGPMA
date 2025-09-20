#include "vm_stack.h"

#include <stdlib.h>
// #include <memory.h>
#include <string.h>

#include "vm_types.h"
#include "vm_memory.h"
#include "vm_status.h"

uint8_t readProgram1B(Vm *vm)
{
    if (vm->program_counter >= vm->memory.program_size)
    {
        vm->status_code = VM_READ_INVALID_PROGRAM;
        return 0;
    }

    vm->program_counter += 1;
    return *(vm->memory.program + vm->program_counter - 1);
}

uint16_t readProgram2B(Vm *vm)
{
    if (vm->program_counter + 1 >= vm->memory.program_size)
    {
        vm->status_code = VM_READ_INVALID_PROGRAM;
        return 0;
    }

    vm->program_counter += 2;
    uint16_t result;
    memcpy(&result, vm->memory.program + vm->program_counter - 2, sizeof(uint16_t));
    return result;
    // return *(uint16_t *)(vm->memory.program + vm->program_counter - 2);
}

uint32_t readProgram4B(Vm *vm)
{
    if (vm->program_counter + 3 >= vm->memory.program_size)
    {
        vm->status_code = VM_READ_INVALID_PROGRAM;
        return 0;
    }

    vm->program_counter += 4;
    uint32_t result;
    memcpy(&result, vm->memory.program + vm->program_counter - 4, sizeof(uint32_t));
    return result;
    // return *(uint32_t *)(vm->memory.program + vm->program_counter - 4);
}

/**
 * @brief 将相对于栈底的偏移量转化为真正的指针
 *
 */
VmSlot *stackOff2Ptr(Vm *vm, uint16_t off)
{
    return vm->memory.stack_area + off;
}

void pushSlot(Vm *vm, VmSlot data)
{
    if (vm->stack_offset > vm->memory.stack_size)
    {
        vm->status_code = VM_STACK_OVERFLOW;
        return;
    }
    *stackOff2Ptr(vm, vm->stack_offset) = data;
    vm->stack_offset += 1;
}

VmSlot popSlot(Vm *vm)
{
    if (vm->stack_offset == 0)
    {
        vm->status_code = VM_STACK_UNDERFLOW;
        return slot_zero;
    }
    vm->stack_offset -= 1;
    return *stackOff2Ptr(vm, vm->stack_offset);
}

/**
 * @brief 将常量区的偏移量转化为指针
 */
const VmSlot *constOff2Ptr(Vm *vm, uint16_t off)
{
    return vm->memory.const_variable_area + off;
}

VmSlot readConst(Vm *vm, uint16_t off)
{
    if (off >= vm->memory.const_size)
    {
        vm->status_code = VM_READ_INVALID_CONSTANT_VARIABLE;
        // VmSlot slot;
        // slot.i32 = 0;
        return slot_zero;
    }
    return *constOff2Ptr(vm, off);
}

/**
 * @brief 将全局变量区的偏移量转化为指针
 *
 */
VmSlot *globalOff2Ptr(Vm *vm, uint16_t off)
{
    return vm->memory.global_variable_area + off;
}

VmSlot readGlobal(Vm *vm, uint16_t off)
{
    if (off >= vm->memory.global_size)
    {
        vm->status_code = VM_READ_INVALID_GLOBAL_VARIABLE;
        // VmSlot slot;
        // slot.i32 = 0;
        return slot_zero;
    }
    return *globalOff2Ptr(vm, off);
}

void writeGlobal(Vm *vm, uint16_t off, VmSlot data)
{
    if (off >= vm->memory.global_size)
    {
        vm->status_code = VM_WRITE_INVALID_GLOBAL_VARIABLE;
        return;
    }
    *globalOff2Ptr(vm, off) = data;
}

/**
 * @brief 从局部变量表的索引得到该数据相对栈底的偏移量
 * 
 * @param idx 所需数据在局部变量表中的索引
 * @return uint16_t 该数据相对栈底的偏移量
 */
uint16_t localIdx2Off(Vm *vm, uint8_t idx)
{
    return vm->frame_header.frame_offset + 3 + idx;
}

VmSlot readLocal(Vm *vm, uint8_t idx)
{
    if (idx >= vm->frame_header.local_size)
    {
        vm->status_code = VM_READ_INVALID_LOCAL_VARIABLE;
        // VmSlot slot;
        // slot.i32 = 0;
        return slot_zero;
    }
    return *stackOff2Ptr(vm, localIdx2Off(vm, idx));
}

void writeLocal(Vm *vm, uint8_t idx, VmSlot data)
{
    if (idx >= vm->frame_header.local_size)
    {
        vm->status_code = VM_WRITE_INVALID_LOCAL_VARIABLE;
        return;
    }
    *stackOff2Ptr(vm, localIdx2Off(vm, idx)) = data;
}

/**
 * @brief 创建一个栈帧
 * 
 * @param return_addr 栈帧的返回地址，该指令相对于程序区起始的偏移量
 * @param argc 形参个数
 */
void pushFrame(Vm *vm, uint16_t return_addr, uint8_t argc)
{
    // 缓存形参
    VmSlot *par_buf = (VmSlot *)malloc(argc * sizeof(VmSlot));
    // 弹出形参
    for (int i = 0; i < argc; i++)
    {
        *(par_buf + i) = popSlot(vm);
    }

    // 压入返回地址
    VmSlot slot;
    slot.i32 = return_addr;
    pushSlot(vm, slot);

    // 压入旧的frame_offset
    slot.i32 = vm->frame_header.frame_offset;
    pushSlot(vm, slot);

    // 设置新的frame_offset
    vm->frame_header.frame_offset = vm->stack_offset - 2;

    // 压入旧的local_size
    slot.i32 = vm->frame_header.local_size;
    pushSlot(vm, slot);

    // 新的local_size在ENTER中设置

    // 传入形参，保证顺序不变
    for (int i = argc - 1; i >= 0; i--)
    {
        pushSlot(vm, *(par_buf + i));
    }
    free(par_buf);
}

/**
 * @brief 弹出当前帧并恢复到上一帧
 * 
 * @param vm 
 * @param should_return 
 */
void popFrame(Vm *vm)
{
    // 读取上一帧的帧头偏移量
    uint16_t last_frame_offset = stackOff2Ptr(vm, vm->frame_header.frame_offset + 1)->i32;

    // 读取上一帧局部变量表的大小
    vm->frame_header.local_size = stackOff2Ptr(vm, vm->frame_header.frame_offset + 2)->i32;

    // 读取并跳转到返回地址
    vm->program_counter = stackOff2Ptr(vm, vm->frame_header.frame_offset)->i32;

    // 弹出此帧
    vm->stack_offset = vm->frame_header.frame_offset;
    vm->frame_header.frame_offset = last_frame_offset;
}

VmSlot popOperantStack(Vm *vm)
{
    if (vm->stack_offset == vm->frame_header.frame_offset + 3)
    {
        vm->status_code = VM_OPERANT_STACK_UNDERFLOW;
        return slot_zero;
    }

    return popSlot(vm);
}
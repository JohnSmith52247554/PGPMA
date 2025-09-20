#ifndef VM_STACK_H
#define VM_STACK_H

#include <stdint.h>
#include "vm_memory.h"

typedef struct
{
    uint16_t return_addr; // 帧返回地址相对于代码区的偏移量
    uint8_t frame_offset; // 帧头相对栈底的偏移量 (Slot)
    uint8_t local_size;   // 帧局部变量的数量
} VmFrameHeader;

typedef struct
{
    VmMemory memory;

    uint16_t program_counter;
    uint16_t stack_offset; // 栈顶相对栈底的偏移量 (Slot)
    VmFrameHeader frame_header;

    uint8_t split_op;   // 一些指令需要分为两步执行，例如delay, reset, 包括开始和等待完成两步
    uint32_t temp_info; // 用于在分布执行时存储一些临时变量，具体数据结构由指令类型决定

    int status_code;
} Vm;

uint8_t readProgram1B(Vm *vm);
uint16_t readProgram2B(Vm *vm);
uint32_t readProgram4B(Vm *vm);
VmSlot *stackOff2Ptr(Vm *vm, uint16_t off);
void pushSlot(Vm *vm, VmSlot data);
VmSlot popSlot(Vm *vm);
const VmSlot *constOff2Ptr(Vm *vm, uint16_t off);
VmSlot readConst(Vm *vm, uint16_t off);
VmSlot *globalOff2Ptr(Vm *vm, uint16_t off);
VmSlot readGlobal(Vm *vm, uint16_t off);
void writeGlobal(Vm *vm, uint16_t off, VmSlot data);
uint16_t localIdx2Off(Vm *vm, uint8_t idx);
VmSlot readLocal(Vm *vm, uint8_t idx);
void writeLocal(Vm *vm, uint8_t idx, VmSlot data);
void pushFrame(Vm *vm, uint16_t return_addr, uint8_t argc);
void popFrame(Vm *vm);
VmSlot popOperantStack(Vm *vm);


#endif
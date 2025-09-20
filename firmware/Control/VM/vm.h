#ifndef VM_H
#define VM_H

#include "vm_types.h"
#include "vm_dispatch.h"
#include "vm_memory.h"
#include "vm_stack.h"
#include "vm_status.h"

#define VM_INIT_OK 0
#define VM_INIT_FILE_DAMAGE 1
#define VM_INIT_INVALID_CONST_AREA_SIZE 2
#define VM_INIT_CONST_AREA_TOO_LARGE 3
#define VM_INIT_GLOBAL_AREA_TOO_LARGE 4
#define VM_INIT_ALLOC_GLOBAL_AREA_FAILED 5
#define VM_INIT_ALLOC_STACK_FAILED 6
#define VM_INIT_ALLOC_PROGRAM_FAILED 7
#define VM_INIT_READ_FLASH_FAILED 8

int vm_init(Vm *vm, uint8_t *byte_code);
void vm_destory(Vm *vm);
void vm_run(Vm *vm);
// void vm_lauch();
int vm_load(Vm *vm, uint8_t *program_ptr);

#endif
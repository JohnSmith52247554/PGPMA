#include "vm_status.h"

const char *VM_GetStatusString(int status_code)
{
    switch (status_code)
    {
    case VM_RUNNING:
        return "RUNNING";
    case VM_HALT:
        return "HALT";
    
    case VM_STACK_OVERFLOW:
        return "STACK OVERFLOW";
    case VM_STACK_UNDERFLOW:
        return "STACK UNDERFLOW";
    case VM_OPERANT_STACK_UNDERFLOW:
        return "OPERANT STACK UNDERFLOW";
    
    case VM_READ_INVALID_CONSTANT_VARIABLE:
        return "READ INVALID CONSTANT";
    case VM_READ_INVALID_GLOBAL_VARIABLE:
        return "READ INVALID GLOBAL VARIABLE";
    case VM_WRITE_INVALID_GLOBAL_VARIABLE:
        return "WRITE INVALID GLOBAL VARIABLE";
    case VM_READ_INVALID_LOCAL_VARIABLE:
        return "READ INVALID LOCAL VARIABLE";
    case VM_WRITE_INVALID_LOCAL_VARIABLE:
        return "WRITE INVALID VARIABLE";
    
    case VM_READ_INVALID_PROGRAM:
        return "READ INVALID PROGRAM";
    case VM_PROGRAM_OVERSTEP:
        return "PORGRAM OVERSTEP";
    case VM_INVALID_OPERATOR:
        return "INVALID OPERATOR";

    case VM_INIT_FAILED:
        return "INIT FAILED";

    default:
        return "UNKNOW ERROR";
    }

}
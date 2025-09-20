#include "vm_dispatch.h"

#include <stdint.h>
#include <stdio.h>

#include "vm_types.h"
#include "vm_memory.h"
#include "vm_status.h"

#include "tim.h"

#include "main.h"
#include "OLED.h"

#include "AllJoint.h"
#include "Gripper.h"
#include "Servo.h"
#include "kinematics.h"
#include "trigonometric.h"

// 指令集
// 控制流
#define OP_NOP      0x00
#define OP_HALT     0x01
#define OP_JMP      0x02
#define OP_JZ       0x03
#define OP_JNZ      0x04
#define OP_CALL     0x05
#define OP_ENTER    0x06
#define OP_RET      0x07
#define OP_RET0     0x08

// 栈操作
#define OP_LOADK    0x11
#define OP_LOADG    0x12
#define OP_LOADL    0x13
#define OP_IMMI    0x14
#define OP_IMMF    0x15
#define OP_POP      0x16
#define OP_STORL    0x17
#define OP_STORG    0x18

// 运算
#define OP_IADD     0x21
#define OP_ISUB     0x22
#define OP_IMUL     0x23
#define OP_IDIV     0x24
#define OP_IMOD     0x25
#define OP_INEG     0x26
#define OP_FADD     0x31
#define OP_FSUB     0x32
#define OP_FMUL     0x33
#define OP_FDIV     0x34
#define OP_FNEG     0x35
#define OP_LNOT     0x41
#define OP_LAND     0x42
#define OP_LOR      0x43
#define OP_BAND     0x51
#define OP_BOR      0x52
#define OP_BXOR     0x53
#define OP_BNOT     0x54
#define OP_SHL      0x55
#define OP_SHR      0x56
#define OP_IEQ      0x61
#define OP_INE      0x62
#define OP_IGT      0x63
#define OP_ILT      0x64
#define OP_IGE      0x65
#define OP_ILE      0x66
#define OP_FEQ      0x71
#define OP_FNE      0x72
#define OP_FGT      0x73
#define OP_FLT      0x74
#define OP_FGE      0x75
#define OP_FLE      0x76
#define OP_I2F      0x81
#define OP_F2I      0x82

// 系统调用
#define OP_DELAY    0x91
#define OP_RST      0x92
#define OP_WAIT     0x93
#define OP_WAITJ    0x94
#define OP_MOVJ     0x95
#define OP_SETJ     0x96
#define OP_READJ    0x97
#define OP_MOVOC    0x98
#define OP_SETOC    0x99
#define OP_MOVJC    0x9A
#define OP_SETJC    0x9B
#define OP_GRIP_OPEN    0x9C
#define OP_GRIP_CLOSE   0x9D
#define OP_SETJSPD  0x9E
#define OP_OLEDI    0xA1

// 测试用指令
// 从栈顶弹出一个参数，视为整数，并打印在控制台
#define OP_PRINT 0xB1

void vm_dispatch_single_op(Vm *vm);
void vm_dispatch_splite_op(Vm *vm);

void vm_dispatch(Vm *vm)
{
    if (vm->split_op == 0)
    {
        vm_dispatch_single_op(vm);
    }
    else
    {
        vm_dispatch_splite_op(vm);
    }

}


void vm_dispatch_single_op(Vm *vm)
{
    uint8_t op = readProgram1B(vm);

    switch (op)
    {
    // 控制流
    case OP_NOP:
        break;
    case OP_HALT:
    {
        vm->status_code = VM_HALT;
        return;
    }
    case OP_JMP:
    {
        uint16_t addr = readProgram2B(vm);
        if (addr >= vm->memory.program_size)
        {
            vm->status_code = VM_PROGRAM_OVERSTEP;
            return;
        }
        vm->program_counter = addr;
    }
    break;
    case OP_JZ:
    {
        uint16_t addr = readProgram2B(vm);
        if (addr >= vm->memory.program_size)
        {
            vm->status_code = VM_PROGRAM_OVERSTEP;
            return;
        }
        VmSlot condition = popSlot(vm);
        if (condition.i32 == 0)
        {
            vm->program_counter = addr;
        }
    }
    break;
    case OP_JNZ:
    {
        uint16_t addr = readProgram2B(vm);
        if (addr >= vm->memory.program_size)
        {
            vm->status_code = VM_PROGRAM_OVERSTEP;
            return;
        }
        VmSlot condition = popSlot(vm);
        if (condition.i32 != 0)
        {
            vm->program_counter = addr;
        }
    }
    break;
    case OP_CALL:
    {
        uint16_t addr = readProgram2B(vm);
        if (addr >= vm->memory.program_size)
        {
            vm->status_code = VM_PROGRAM_OVERSTEP;
            return;
        }
        uint8_t argc = readProgram1B(vm);
        pushFrame(vm, vm->program_counter, argc);
        vm->program_counter = addr;
    }
    break;
    case OP_ENTER:
    {
        uint8_t nlocals = readProgram1B(vm);
        vm->frame_header.local_size = nlocals;
        vm->stack_offset = vm->frame_header.frame_offset + 3 + nlocals;
    }
    break;
    case OP_RET:
    {
        VmSlot ret_var = popOperantStack(vm);
        popFrame(vm);
        pushSlot(vm, ret_var);
    }
    break;
    case OP_RET0:
    {
        popFrame(vm);
    }
    break;

    // 栈操作
    case OP_LOADK:
    {
        uint16_t idx = readProgram2B(vm);
        VmSlot val = readConst(vm, idx);
        pushSlot(vm, val);
    }
    break;
    case OP_LOADG:
    {
        uint16_t idx = readProgram2B(vm);
        VmSlot var = readGlobal(vm, idx);
        pushSlot(vm, var);
    }
    break;
    case OP_LOADL:
    {
        uint8_t idx = readProgram1B(vm);
        VmSlot var = readLocal(vm, idx);
        pushSlot(vm, var);
    }
    break;
    case OP_IMMI: // 两者仅在汇编上有区别
    case OP_IMMF: // 实际执行的功能是一致的
    {
        uint32_t val = readProgram4B(vm);
        VmSlot slot;
        slot.i32 = val;
        pushSlot(vm, slot);
    }
    break;
    case OP_POP:
    {
        popSlot(vm);
    }
    break;
    case OP_STORL:
    {
        uint8_t idx = readProgram1B(vm);
        VmSlot slot = popOperantStack(vm);
        writeLocal(vm, idx, slot);
    }
    break;
    case OP_STORG:
    {
        uint16_t idx = readProgram2B(vm);
        VmSlot slot = popOperantStack(vm);
        writeGlobal(vm, idx, slot);
    }
    break;

    // 运算
    case OP_IADD:
    {
        VmSlot b = popOperantStack(vm);
        VmSlot a = popOperantStack(vm);
        VmSlot result;
        result.i32 = a.i32 + b.i32;
        pushSlot(vm, result);
    }
    break;
    case OP_ISUB:
    {
        VmSlot b = popOperantStack(vm);
        VmSlot a = popOperantStack(vm);
        VmSlot result;
        result.i32 = a.i32 - b.i32;
        pushSlot(vm, result);
    }
    break;
    case OP_IMUL:
    {
        VmSlot b = popOperantStack(vm);
        VmSlot a = popOperantStack(vm);
        VmSlot result;
        result.i32 = a.i32 * b.i32;
        pushSlot(vm, result);
    }
    break;
    case OP_IDIV:
    {
        VmSlot b = popOperantStack(vm);
        VmSlot a = popOperantStack(vm);
        VmSlot result;
        result.i32 = a.i32 / b.i32;
        pushSlot(vm, result);
    }
    break;
    case OP_IMOD:
    {
        VmSlot b = popOperantStack(vm);
        VmSlot a = popOperantStack(vm);
        VmSlot result;
        result.i32 = a.i32 % b.i32;
        pushSlot(vm, result);
    }
    break;
    case OP_INEG:
    {
        VmSlot a = popOperantStack(vm);
        VmSlot result;
        result.i32 = -a.i32;
        pushSlot(vm, result);
    }
    break;
    case OP_FADD:
    {
        VmSlot b = popOperantStack(vm);
        VmSlot a = popOperantStack(vm);
        VmSlot result;
        result.f32 = a.f32 + b.f32;
        pushSlot(vm, result);
    }
    break;
    case OP_FSUB:
    {
        VmSlot b = popOperantStack(vm);
        VmSlot a = popOperantStack(vm);
        VmSlot result;
        result.f32 = a.f32 - b.f32;
        pushSlot(vm, result);
    }
    break;
    case OP_FMUL:
    {
        VmSlot b = popOperantStack(vm);
        VmSlot a = popOperantStack(vm);
        VmSlot result;
        result.f32 = a.f32 * b.f32;
        pushSlot(vm, result);
    }
    break;
    case OP_FDIV:
    {
        VmSlot b = popOperantStack(vm);
        VmSlot a = popOperantStack(vm);
        VmSlot result;
        result.f32 = a.f32 / b.f32;
        pushSlot(vm, result);
    }
    break;
    case OP_FNEG:
    {
        VmSlot a = popOperantStack(vm);
        VmSlot result;
        result.f32 = -a.f32;
        pushSlot(vm, result);
    }
    break;
    case OP_LNOT:
    {
        VmSlot a = popOperantStack(vm);
        VmSlot result;
        result.i32 = !a.i32;
        pushSlot(vm, result);
    }
    break;
    case OP_LAND:
    {
        VmSlot b = popOperantStack(vm);
        VmSlot a = popOperantStack(vm);
        VmSlot result;
        result.i32 = a.i32 && b.i32;
        pushSlot(vm, result);
    }
    break;
    case OP_LOR:
    {
        VmSlot b = popOperantStack(vm);
        VmSlot a = popOperantStack(vm);
        VmSlot result;
        result.i32 = a.i32 || b.i32;
        pushSlot(vm, result);
    }
    break;
    case OP_BAND:
    {
        VmSlot b = popOperantStack(vm);
        VmSlot a = popOperantStack(vm);
        VmSlot result;
        result.i32 = a.i32 & b.i32;
        pushSlot(vm, result);
    }
    break;
    case OP_BOR:
    {
        VmSlot b = popOperantStack(vm);
        VmSlot a = popOperantStack(vm);
        VmSlot result;
        result.i32 = a.i32 | b.i32;
        pushSlot(vm, result);
    }
    break;
    case OP_BXOR:
    {
        VmSlot b = popOperantStack(vm);
        VmSlot a = popOperantStack(vm);
        VmSlot result;
        result.i32 = a.i32 ^ b.i32;
        pushSlot(vm, result);
    }
    break;
    case OP_BNOT:
    {
        VmSlot b = popOperantStack(vm);
        VmSlot a = popOperantStack(vm);
        VmSlot result;
        result.i32 = ~b.i32;
        pushSlot(vm, result);
    }
    break;
    case OP_SHL:
    {
        VmSlot b = popOperantStack(vm);
        VmSlot a = popOperantStack(vm);
        VmSlot result;
        result.i32 = a.i32 << b.i32;
        pushSlot(vm, result);
    }
    break;
    case OP_SHR:
    {
        VmSlot b = popOperantStack(vm);
        VmSlot a = popOperantStack(vm);
        VmSlot result;
        result.i32 = a.i32 >> b.i32;
        pushSlot(vm, result);
    }
    break;
    case OP_IEQ:
    {
        VmSlot b = popOperantStack(vm);
        VmSlot a = popOperantStack(vm);
        VmSlot result;
        result.i32 = a.i32 == b.i32;
        pushSlot(vm, result);
    }
    break;
    case OP_INE:
    {
        VmSlot b = popOperantStack(vm);
        VmSlot a = popOperantStack(vm);
        VmSlot result;
        result.i32 = a.i32 != b.i32;
        pushSlot(vm, result);
    }
    break;
    case OP_IGT:
    {
        VmSlot b = popOperantStack(vm);
        VmSlot a = popOperantStack(vm);
        VmSlot result;
        result.i32 = a.i32 > b.i32;
        pushSlot(vm, result);
    }
    break;
    case OP_ILT:
    {
        VmSlot b = popOperantStack(vm);
        VmSlot a = popOperantStack(vm);
        VmSlot result;
        result.i32 = a.i32 < b.i32;
        pushSlot(vm, result);
    }
    break;
    case OP_IGE:
    {
        VmSlot b = popOperantStack(vm);
        VmSlot a = popOperantStack(vm);
        VmSlot result;
        result.i32 = a.i32 >= b.i32;
        pushSlot(vm, result);
    }
    break;
    case OP_ILE:
    {
        VmSlot b = popOperantStack(vm);
        VmSlot a = popOperantStack(vm);
        VmSlot result;
        result.i32 = a.i32 <= b.i32;
        pushSlot(vm, result);
    }
    break;
    case OP_FEQ:
    {
        VmSlot b = popOperantStack(vm);
        VmSlot a = popOperantStack(vm);
        VmSlot result;
        result.f32 = a.f32 == b.f32;
        pushSlot(vm, result);
    }
    break;
    case OP_FNE:
    {
        VmSlot b = popOperantStack(vm);
        VmSlot a = popOperantStack(vm);
        VmSlot result;
        result.i32 = a.i32 != b.i32;
        pushSlot(vm, result);
    }
    break;
    case OP_FGT:
    {
        VmSlot b = popOperantStack(vm);
        VmSlot a = popOperantStack(vm);
        VmSlot result;
        result.i32 = a.i32 > b.i32;
        pushSlot(vm, result);
    }
    break;
    case OP_FLT:
    {
        VmSlot b = popOperantStack(vm);
        VmSlot a = popOperantStack(vm);
        VmSlot result;
        result.i32 = a.i32 < b.i32;
        pushSlot(vm, result);
    }
    break;
    case OP_FGE:
    {
        VmSlot b = popOperantStack(vm);
        VmSlot a = popOperantStack(vm);
        VmSlot result;
        result.i32 = a.i32 >= b.i32;
        pushSlot(vm, result);
    }
    break;
    case OP_FLE:
    {
        VmSlot b = popOperantStack(vm);
        VmSlot a = popOperantStack(vm);
        VmSlot result;
        result.i32 = a.i32 <= b.i32;
        pushSlot(vm, result);
    }
    break;
    case OP_I2F:
    {
        VmSlot a = popOperantStack(vm);
        VmSlot result;
        result.f32 = (float)a.i32;
        pushSlot(vm, result);
    }
    break;
    case OP_F2I:
    {
        VmSlot a = popOperantStack(vm);
        VmSlot result;
        result.i32 = (uint32_t)a.f32;
        pushSlot(vm, result);
    }
    break;

    // 系统调用
    case OP_DELAY:
    {
        VmSlot a = popOperantStack(vm);
        // HAL_Delay(a.i32);
        TIM_DelayStart(a.i32);
        vm->split_op = OP_DELAY;
    }
    break;
    case OP_RST:
    {
        AllJoint_Reset();
    }
    break;
    case OP_WAIT:
    {
        vm->split_op = OP_WAIT;
    }
    break;
    case OP_WAITJ:
    {
        VmSlot joint_id = popOperantStack(vm);
        vm->split_op = OP_WAITJ;
        vm->temp_info = joint_id.i32;
    }
    break;
    case OP_MOVJ:
    {
        VmSlot joint_angle = popOperantStack(vm);
        VmSlot joint_id = popOperantStack(vm);
        switch (joint_id.i32)
        {
        case 1:
            Joint_SetTarget(&m1h, joint_angle.f32);
            break;
        case 2:
            Joint_SetTarget(&m2h, joint_angle.f32);
            break;
        case 3:
            Joint_SetTarget(&m3h, joint_angle.f32);
            break;
        case 4:
            Joint_SetTarget(&m4h, joint_angle.f32);
            break;
        case 5:
            S1_SetAngle(joint_angle.f32);
            break;
        case 6:
            Gripper_SetAngle(joint_angle.f32);
            break;
        default:
            break;
        }
        vm->split_op = OP_WAITJ;
        vm->temp_info = joint_id.i32;
    }
    break;
    case OP_SETJ:
    {
        VmSlot joint_angle = popOperantStack(vm);
        VmSlot joint_id = popOperantStack(vm);
        switch (joint_id.i32)
        {
        case 1:
            Joint_SetTarget(&m1h, joint_angle.f32);
            break;
        case 2:
            Joint_SetTarget(&m2h, joint_angle.f32);
            break;
        case 3:
            Joint_SetTarget(&m3h, joint_angle.f32);
            break;
        case 4:
            Joint_SetTarget(&m4h, joint_angle.f32);
            break;
        case 5:
            S1_SetAngle(joint_angle.f32);
            break;
        case 6:
            Gripper_SetAngle(joint_angle.f32);
            break;
        default:
            break;
        }
    }
    break;
    case OP_READJ:
    {
        VmSlot joint_id = popOperantStack(vm);
        VmSlot joint_angle;
        switch (joint_id.i32)
        {
        case 1:
            joint_angle.f32 = joint_info[m1h.can_id - 1].angle;
            break;
        case 2:
            joint_angle.f32 = joint_info[m2h.can_id - 1].angle;
            break;
        case 3:
            joint_angle.f32 = joint_info[m3h.can_id - 1].angle;
            break;
        case 4:
            joint_angle.f32 = joint_info[m4h.can_id - 1].angle;
            break;
        case 5:
            joint_angle.f32 = S1_GetAngle();
            break;
        case 6:
            joint_angle.f32 = Gripper_GetAngle();
            break;
        default:
            break;
        }
        pushSlot(vm, joint_angle);
    }
    break;
    case OP_MOVOC:
    {
        VmSlot alpha = popOperantStack(vm);
        VmSlot z = popOperantStack(vm);
        VmSlot y = popOperantStack(vm);
        VmSlot x = popOperantStack(vm);
        KineHandle handle;
        handle.x = x.f32;
        handle.y = y.f32;
        handle.z = z.f32;
        handle.alpha = degree2radian(alpha.f32);
        if (kine_reverse_resolve(&handle) == KINE_OK)
        {
            MotorAngle angle = get_motor_angle(&handle);
            Joint_SetTarget(&m1h, angle.m1a);
            Joint_SetTarget(&m2h, angle.m2a);
            Joint_SetTarget(&m3h, angle.m3a);
            Joint_SetTarget(&m4h, angle.m4a);
            vm->split_op = OP_WAIT;
        }   
    }
    break;
    case OP_SETOC:
    {
        VmSlot alpha = popOperantStack(vm);
        VmSlot z = popOperantStack(vm);
        VmSlot y = popOperantStack(vm);
        VmSlot x = popOperantStack(vm);
        KineHandle handle;
        handle.x = x.f32;
        handle.y = y.f32;
        handle.z = z.f32;
        handle.alpha = degree2radian(alpha.f32);
        if (kine_reverse_resolve(&handle) == KINE_OK)
        {
            MotorAngle angle = get_motor_angle(&handle);
            Joint_SetTarget(&m1h, angle.m1a);
            Joint_SetTarget(&m2h, angle.m2a);
            Joint_SetTarget(&m3h, angle.m3a);
            Joint_SetTarget(&m4h, angle.m4a);
        }
    }
    break;
    case OP_MOVJC:
    {
        VmSlot s2 = popOperantStack(vm);
        VmSlot s1 = popOperantStack(vm);
        VmSlot m4 = popOperantStack(vm);
        VmSlot m3 = popOperantStack(vm);
        VmSlot m2 = popOperantStack(vm);
        VmSlot m1 = popOperantStack(vm);

        Joint_SetTarget(&m1h, m1.f32);
        Joint_SetTarget(&m2h, m2.f32);
        Joint_SetTarget(&m3h, m3.f32);
        Joint_SetTarget(&m4h, m4.f32);
        S1_SetAngle(s1.f32);
        Gripper_SetAngle(s2.f32);

        vm->split_op = OP_WAIT;
    }
    break;
    case OP_SETJC:
    {
        VmSlot s2 = popOperantStack(vm);
        VmSlot s1 = popOperantStack(vm);
        VmSlot m4 = popOperantStack(vm);
        VmSlot m3 = popOperantStack(vm);
        VmSlot m2 = popOperantStack(vm);
        VmSlot m1 = popOperantStack(vm);

        Joint_SetTarget(&m1h, m1.f32);
        Joint_SetTarget(&m2h, m2.f32);
        Joint_SetTarget(&m3h, m3.f32);
        Joint_SetTarget(&m4h, m4.f32);
        S1_SetAngle(s1.f32);
        Gripper_SetAngle(s2.f32);
    }
    break;
    case OP_GRIP_OPEN:
    {
        Gripper_Open();
    }
    break;
    case OP_GRIP_CLOSE:
    {
        Gripper_CloseStart();
    }
    break;
    case OP_SETJSPD:
    {
        VmSlot joint_speed = popOperantStack(vm);
        VmSlot joint_id = popOperantStack(vm);
        switch (joint_id.i32)
        {
        case 1:
            Joint_SetMaxSpeedPercentage(&m1h, joint_speed.f32);
            break;
        case 2:
            Joint_SetMaxSpeedPercentage(&m2h, joint_speed.f32);
            break;
        case 3:
            Joint_SetMaxSpeedPercentage(&m3h, joint_speed.f32);
            break;
        case 4:
            Joint_SetMaxSpeedPercentage(&m4h, joint_speed.f32);
            break;
        case 5:
            S1_SetSpeed(joint_speed.f32);
            break;
        case 6:
            Gripper_SetSpeed(joint_speed.f32);
        default:
            break;
        }
    }
    break;
    case OP_OLEDI:
    {
        VmSlot len = popOperantStack(vm);
        VmSlot num = popOperantStack(vm);
        VmSlot col = popOperantStack(vm);
        VmSlot row = popOperantStack(vm);
        OLED_ShowNum(row.i32, col.i32, num.i32, len.i32);
    }
    break;

    // 调试用
    case OP_PRINT:
    {
        VmSlot val = popOperantStack(vm);
        // printf("%d\n", val.i32);
    }
    break;

    default:
        vm->status_code = VM_INVALID_OPERATOR;
        break;
    }
}

void vm_dispatch_splite_op(Vm *vm)
{
    switch (vm->split_op)
    {
    case OP_DELAY:
        if (tim_delay_flag == TIM_DELAY_OK)
            vm->split_op = 0;
        break;
    case OP_WAIT:
        {
            if (m1h.has_achieved_target && m2h.has_achieved_target 
                && m3h.has_achieved_target && m4h.has_achieved_target)
                // && Gripper_HasAchieveTarget() && S1_HasAchieveTarget())
            {
                vm->split_op = 0;
            }
        }
        break;
    case OP_WAITJ:
        {
            switch (vm->temp_info)
            {
            case 1:
                if (m1h.has_achieved_target)
                    vm->split_op = 0;
                break;
            case 2:
                if (m2h.has_achieved_target)
                    vm->split_op = 0;
                break;
            case 3:
                if (m3h.has_achieved_target)
                    vm->split_op = 0;
                break;
            case 4:
                if (m4h.has_achieved_target)
                    vm->split_op = 0;
                break;
            case 5:
                if (S1_HasAchieveTarget())
                    vm->split_op = 0;
                break;
            case 6:
                if (Gripper_HasAchieveTarget())
                    vm->split_op = 0;
                break;
            default:
                vm->split_op = 0;
                break;
            }
        }
        break;
    default:
        break;
    }
}
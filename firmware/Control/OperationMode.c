#include "OperationMode.h"

#include <stdlib.h>

#include "OLED.h"
#include "USBD_ctrl.h"
#include "vm.h"
#include "Joint.h"
#include "AllJoint.h"
#include "JointCtrl.h"
#include "Gripper.h"
#include "Servo.h"
#include "VisualMode.h"

#define OP_SLAVE_MODE   0
#define OP_PROGRAM_MODE 1

uint8_t operation_mode = OP_SLAVE_MODE;
uint8_t op_mode_move_flag = 1;

uint8_t op_should_check_host_connect = 1;

volatile uint32_t last_interrupt_time = 0;

Vm vm;
uint8_t *vm_program_ptr = NULL;

void Operation_CheckHostConnect();

void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
    if (GPIO_Pin == KEY_1_Pin)
    {
        // 消抖
        uint32_t current_time = HAL_GetTick();
        if (current_time - last_interrupt_time > 150)
        {
            last_interrupt_time = current_time;
            operation_mode = (operation_mode + 1) % 2;
            op_mode_move_flag = 1;
            // Error_Handler();
        }

    }
    else if (GPIO_Pin == HALL_0_Pin || GPIO_Pin == HALL_1_Pin || GPIO_Pin == HALL_2_Pin || GPIO_Pin == HALL_3_Pin)
    {
        Hall_EXTICallBack(GPIO_Pin);
    }
}


void Operation_Poll()
{
    switch (operation_mode)
    {
    case OP_SLAVE_MODE:
        {
            if (op_mode_move_flag)
            {
                op_mode_move_flag = 0;
                // 移动到上位机模式
                USBD_Enable();

                vm_destory(&vm);
                free(vm_program_ptr);
                if (vm_program_ptr != NULL)
                    vm_program_ptr = NULL;

                OLED_Clear();
                OLED_ShowString(1, 1, "SLAVE MODE  ");
            }
            Operation_CheckHostConnect();

            USBD_Poll();
        }
        break;
    case OP_PROGRAM_MODE:
        {
            if (op_mode_move_flag)
            {
                op_mode_move_flag = 0;

                // 转移到编程模式
                USBD_Disable();

                OLED_Clear();
                OLED_ShowString(1, 1, "PROGRAM MODE");

                // 启动虚拟器
                int vm_init_status = vm_load(&vm, vm_program_ptr);
                if (vm_init_status != VM_INIT_OK)
                {
                    OLED_ShowNum(2, 1, vm_init_status, 3);
                    vm.status_code = VM_INIT_FAILED;
                }
            }

            if (vm.status_code == VM_RUNNING)
            {
                vm_dispatch(&vm);
                OLED_ShowHexNum(4, 1, vm.program_counter, 8);
            }
            OLED_ShowString(3, 1, VM_GetStatusString(vm.status_code));
        }
        break;

    default:
        break;
    }

    // Gripper_Poll();
    JointCtrl_Poll();
    // S1_Poll();

    Visual_Poll();
}

void Operation_CheckHostConnect()
{
    if (op_should_check_host_connect == 0)
        return;

    op_should_check_host_connect = 0;

    // 检查USB是否连接
    if (HAL_GPIO_ReadPin(GPIOA, GPIO_PIN_9))
    {
        OLED_ShowString(2, 1, "HOST CONNECTED");
    }
    else
    {
        OLED_ShowString(2, 1, "HOST UNCONNECT");
    }
}
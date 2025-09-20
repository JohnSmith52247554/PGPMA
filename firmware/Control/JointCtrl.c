#include "JointCtrl.h"

#include "AllJoint.h"
#include "OLED.h"

uint8_t joint_ctrl_status = JC_STATUS_POLL;

uint8_t rst_pending_joint_num;

void JointCtrl_Poll()
{
    switch (joint_ctrl_status)
    {
        case JC_STATUS_POLL:
        {
            Joint_TimItHandler();
        }
        break;
        case JC_STATUS_RESET_POLL:
        {
            Joint_TimItHandler();
            if (m1h.has_achieved_target && m2h.has_achieved_target
                && m3h.has_achieved_target && m4h.has_achieved_target)
            {
                Joint_ResetStart(&m1h);
                Joint_ResetStart(&m2h);
                Joint_ResetStart(&m3h);
                Joint_ResetStart(&m4h);

                rst_pending_joint_num = 4;
                joint_ctrl_status = JC_STATUS_RESET;
                // joint_ctrl_status = JC_STATUS_POLL;
            }
        }
        break;
        case JC_STATUS_RESET:
        {
            AllJoint_RequestData();
            if (rst_pending_joint_num == 0)
            {
                Joint_SetTarget(&m1h, 0);
                Joint_SetTarget(&m2h, 0);
                Joint_SetTarget(&m3h, 0);
                Joint_SetTarget(&m4h, 0);
                joint_ctrl_status = JC_STATUS_POLL;
            }
            else
            {
                if (m1h.reset_flag == 1)
                {
                    Joint_ResetEnd(&m1h, joint_info + m1h.can_id - 1);
                    rst_pending_joint_num -= 1;
                    OLED_ShowNum(3, 1, 1, 1);
                }
                if (m2h.reset_flag == 1)
                {
                    Joint_ResetEnd(&m2h, joint_info + m2h.can_id - 1);
                    rst_pending_joint_num -= 1;
                    OLED_ShowNum(3, 2, 2, 1);
                }
                if (m3h.reset_flag == 1)
                {
                    Joint_ResetEnd(&m3h, joint_info + m3h.can_id - 1);
                    rst_pending_joint_num -= 1;
                    OLED_ShowNum(3, 3, 3, 1);
                }
                if (m4h.reset_flag == 1)
                {
                    Joint_ResetEnd(&m4h, joint_info + m4h.can_id - 1);
                    rst_pending_joint_num -= 1;
                    OLED_ShowNum(3, 4, 4, 1);
                }
            }
        }
        break;
    }

    // OLED_ShowNum(4, 1, joint_ctrl_status, 2);
    // OLED_ShowNum(4, 4, rst_pending_joint_num, 2);
}
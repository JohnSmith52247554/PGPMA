#include "USBD_ctrl.h"

#include <stdlib.h>

#include "usbd_cdc_if.h"
#include "main.h"
#include "dma.h"
#include "spi.h"

#include "OLED.h"
#include "W25Q.h"
#include "Joint.h"
#include "AllJoint.h"
#include "Gripper.h"
#include "Servo.h"
#include "kinematics.h"
#include "trigonometric.h"
#include "VisualMode.h"

#define _DEBUG

#ifdef _DEBUG
#define DEBUG_CODE(code) \
	do                   \
	{                    \
		code             \
	} while (0)
#else
#define DEBUG_CODE(code)
#endif // _DEBUG

// 状态机
#define USBD_IDLE 0
#define USBD_RECV_PACKET 1
#define USBD_TSMT_PACKET 2
uint8_t usbd_state = USBD_IDLE;

volatile uint8_t usbd_work_state = USBD_WORK_IDLE;

#define DESERIALIZE(src, dst) memcpy(&(dst), (src), sizeof(float))
#define SERIALIZE(src, dst) memcpy((dst), &(src), sizeof(src))

#define W25Q_WRITE_BUFFER_SIZE 256 // 写Flash时所用的缓存大小，one page
#define W25Q_READ_BUFFER_SIZE 1024 // 读Flash时所用的缓存大小，one page
#define USBD_PACKET_SIZE 64

uint8_t *w25q_usb_buffer = NULL; // 双缓存设计
uint8_t *w25q_spi_buffer = NULL; // A用来从USB接收数据，B用来写入Flash

uint32_t w25q_addr_ptr = 0;		  // 用于记录w25q地址指针
int32_t w25q_read_len = 0;		  // 读Flash的长度
uint8_t *w25q_usb_buffer_ptr = 0; // 指向w25q_usb_buffer的顶部

#define W25Q_USB_BUFFER_HAVENT_SENT 0
#define W25Q_USB_BUFFER_SENT 1
uint8_t w25q_usb_buffer_state = W25Q_USB_BUFFER_HAVENT_SENT;

HAL_StatusTypeDef USBD_Respond(uint8_t respond);
void USBD_SwapW25QBuffer();
void USBD_CleanUpRWFlash();

void USBD_Reset()
{
	usbd_state = USBD_IDLE;
	w25q_usb_buffer_state = W25Q_USB_BUFFER_HAVENT_SENT;

	if (w25q_spi_buffer != NULL)
	{
		free(w25q_spi_buffer);
		w25q_spi_buffer = NULL;
	}
	if (w25q_usb_buffer != NULL)
	{
		free(w25q_usb_buffer);
		w25q_usb_buffer = NULL;
	}
}

void USBD_Enable()
{
	USBD_Reset();
	usbd_work_state = USBD_WORK_IDLE;
}

void USBD_Disable()
{
	USBD_Reset();
	usbd_work_state = USBD_WORK_BUSY;
}

void USBD_Poll()
{
	if (Recv_dlen == 0)
		return;

	usbd_work_state = USBD_WORK_BUSY;
	if (DMA2_Stream0_Wait() != HAL_OK)
	{
		periph_error = PE_OTG_FS_RX_ERROR;
		usbd_work_state = USBD_WORK_IDLE;
		// OLED_ShowNum(3, 1, Recv_dlen, 3);
		// OLED_ShowHexNum(4, 1, UserRxBuffer[0], 2);
		// Error_Handler();
		return;
	}
	// OLED_ShowNum(4, 1, Recv_dlen, 4);

	// 处理状态机
	switch (usbd_state)
	{
	case USBD_IDLE:
		switch (UserRxBuffer[0]) // 取指令
		{
		case CMD_IMMEDIATE_STOP:
		{
			DEBUG_CODE(OLED_ShowString(3, 1, "STOP    "););
			AllJoint_Stop();
			Gripper_Stop();
			S1_Stop();
			USBD_Respond(RESPOND_OK);
		}
		break;
		case CMD_IMMEDIATE_ORTHOGONAL:
		{
			/** 即时正交坐标控制
				格式为：58 XXXXXXXX YYYYYYYY ZZZZZZZZ AAAAAAAA
			*/
			float x, y, z, alpha;
			DESERIALIZE(UserRxBuffer + 1, x);
			DESERIALIZE(UserRxBuffer + 5, y);
			DESERIALIZE(UserRxBuffer + 9, z);
			DESERIALIZE(UserRxBuffer + 13, alpha);
			// DESERIALIZE(UserRxBuffer + 17, ry);
			// DESERIALIZE(UserRxBuffer + 21, rz);
			// DESERIALIZE(UserRxBuffer + 25, gripper);

			DEBUG_CODE(
				OLED_ShowString(3, 1, "ImmOr");
				// OLED_ShowFloatNum(4, 1, x, 2, 1);
				// OLED_ShowFloatNum(4, 7, y, 2, 1);
				// OLED_ShowFloatNum(2, 7, z, 2, 1);
				// OLED_ShowFloatNum(3, 1, rx, 2, 1);
				// OLED_ShowFloatNum(3, 7, ry, 2, 1);
				// OLED_ShowFloatNum(4, 1, rz, 2, 1);
				// OLED_ShowFloatNum(4, 7, gripper, 2, 1);
			);

			KineHandle handle;
			handle.x = x;
			handle.y = y;
			handle.z = z;
			handle.alpha = degree2radian(alpha);

			if (kine_reverse_resolve(&handle) != KINE_OK)
			{
				USBD_Respond(0xFF);
			}
			else
			{
				MotorAngle angle = get_motor_angle(&handle);
				OLED_Clear();
				Joint_SetTarget(&m1h, angle.m1a);
				Joint_SetTarget(&m2h, angle.m2a);
				Joint_SetTarget(&m3h, angle.m3a);
				Joint_SetTarget(&m4h, angle.m4a);
				OLED_ShowFloatNum(3, 1, angle.m1a, 3, 1);
				OLED_ShowFloatNum(3, 8, angle.m2a, 3, 1);
				OLED_ShowFloatNum(4, 1, angle.m3a, 3, 1);
				OLED_ShowFloatNum(4, 8, angle.m4a, 3, 1);

				USBD_Respond(RESPOND_OK);
			}
		}
		break;
		case CMD_IMMEDIATE_JOINT:
		{
			/**
			 * 即时关节坐标控制
			 * 格式为 5B M1M1M1M1 M2M2M2M2 M3M3M3M3 M4M4M4M4 S1S1S1S1 S2S2S2S2
			 * 
			 */

			float m1, m2, m3, m4, s1, s2;
			DESERIALIZE(UserRxBuffer + 1, m1);
			DESERIALIZE(UserRxBuffer + 5, m2);
			DESERIALIZE(UserRxBuffer + 9, m3);
			DESERIALIZE(UserRxBuffer + 13, m4);
			DESERIALIZE(UserRxBuffer + 17, s1);
			DESERIALIZE(UserRxBuffer + 21, s2);

			DEBUG_CODE(
				OLED_ShowString(3, 1, "ImmJo");
				// OLED_ShowFloatNum(2, 1, m1, 2, 1);
				// OLED_ShowFloatNum(2, 7, m2, 2, 1);
				// OLED_ShowFloatNum(3, 1, m3, 2, 1);
				// OLED_ShowFloatNum(3, 7, m4, 2, 1);
				// OLED_ShowFloatNum(4, 1, s1, 2, 1);
				// OLED_ShowFloatNum(4, 7, s2, 2, 1);
			);

			Joint_SetTarget(&m1h, m1);
			Joint_SetTarget(&m2h, m2);
			Joint_SetTarget(&m3h, m3);
			Joint_SetTarget(&m4h, m4);
			S1_SetAngle(s1);
			Gripper_SetAngle(s2);

			USBD_Respond(RESPOND_OK);
		}
		break;
		case CMD_OPEN_GRIPPER:
		{
			DEBUG_CODE(OLED_ShowString(3, 1, "Open Gripper"););

			Gripper_Open();

			USBD_Respond(RESPOND_OK);
		}
		break;
		case CMD_CLOSE_GRIPPER:
		{
			DEBUG_CODE(OLED_ShowString(3, 1, "Close Gripper"););

			Gripper_CloseStart();

			USBD_Respond(RESPOND_OK);
		}
		break;
		case CMD_GET_STATE:
		{
			DEBUG_CODE(OLED_ShowString(3, 1, "Get State"););

			/**
			 * 读取当前状态，格式为：
			 * AA M1M1M1M1 M2M2M2M2 M3M3M3M3 M4M4M4M4 S1S1S1S1 S2S2S2S2
			 */
			uint8_t respond[28];
			respond[0] = RESPOND_OK;
			respond[1] = RESPOND_OK;
			respond[2] = RESPOND_OK;
			respond[3] = RESPOND_OK;
			// AllJoint_RequestData();
			float angle_m1 = Joint_GetAngle(&m1h, &joint_info[0]);
			float angle_m2 = Joint_GetAngle(&m2h, &joint_info[1]);
			float angle_m3 = Joint_GetAngle(&m3h, &joint_info[2]);
			float angle_m4 = Joint_GetAngle(&m4h, &joint_info[3]);
			float s1 = S1_GetAngle(), s2 = Gripper_GetAngle();
			SERIALIZE(angle_m1, respond + 4);
			SERIALIZE(angle_m2, respond + 8);
			SERIALIZE(angle_m3, respond + 12);
			SERIALIZE(angle_m4, respond + 16);
			SERIALIZE(s1, respond + 20);
			SERIALIZE(s2, respond + 24);

			CDC_Transmit_FS(respond, 28);
		}
		break;
		case CMD_VISUAL:
		{
			DEBUG_CODE(OLED_ShowString(3, 1, "Visual"););

			VisualInfo info;
			DESERIALIZE(UserRxBuffer + 1, info.x);
			DESERIALIZE(UserRxBuffer + 5, info.y);
			DESERIALIZE(UserRxBuffer + 9, info.z);
			memcpy(&info.qr_id, UserRxBuffer + 13, sizeof(info.qr_id));

			// OLED_ShowFloatNum(4, 1, x, 2, 1);
			// OLED_ShowFloatNum(4, 6, rot, 2, 1);
			// OLED_ShowNum(4, 1, qr_id, 8);

			Visual_SetTarget(&info);

			USBD_Respond(RESPOND_OK);
		}
		break;
		case CMD_RESET:
		{
			DEBUG_CODE(OLED_ShowString(3, 1, "Reset"););
			// Servo_AdjustMiddle(0);
			USBD_Respond(RESPOND_OK);
			AllJoint_Reset();
			S1_SetAngle(0);
			Gripper_Open();
		}
		break;
		case CMD_WRITE_FLASH:
		{
			/*
				写Flash指令格式如下：
					1. 上位机发送指令头，格式为0xAABBBBBBBB（5字节）
					   AA：写Flash指令 (0x6A); BBBBBBBB：32位起始地址（小端序），自动自增，需要与Sector对齐
					2. MCU接收到指令头后，进行传输准备（创建缓存区），
					   完成后进入USBD_RECV_PACKET，并发送RESPOND_OK
					3. 上位机以64字节为一包进行发包，MCU将其储存于w25q_usb_buffer中。
					   存满256bytes后，w25q_usb_buffer与w25q_spi_buffer互换
					   MCU开始写Flash，并发送RESPOND_OK
					4. 上位机接收到RESOND_OK后，发送下一个包，直到全部发完（不足64字节则补全为64字节）
					   MCU回复RESOND_OK后，上位机发送CMD_END_WRITE_FLASH终止写Flash
					   MCU接收到CMD_END_WRITE_FLASH后，清理缓存并置USBD_IDLE
			*/
			// OLED_ShowString(1, 1, "START");
			// 分配缓存区
			if (w25q_usb_buffer != NULL || w25q_spi_buffer != NULL)
			{
				periph_error = PE_OTG_FS_RX_ERROR;
				hardware_error = HE_W25Q_ERROR;
				USBD_Respond(RESPOND_BUSY);
				goto FUNC_END;
			}
			w25q_usb_buffer = (uint8_t *)malloc(sizeof(uint8_t) * W25Q_WRITE_BUFFER_SIZE);
			w25q_spi_buffer = (uint8_t *)malloc(sizeof(uint8_t) * W25Q_WRITE_BUFFER_SIZE);
			w25q_usb_buffer_ptr = w25q_usb_buffer;

			// 记录地址指针（小端序）
			w25q_addr_ptr = (uint32_t)UserRxBuffer[1];
			w25q_addr_ptr |= (UserRxBuffer[2] << 8);
			w25q_addr_ptr |= (UserRxBuffer[3] << 16);
			w25q_addr_ptr |= (UserRxBuffer[4] << 24);

			// OLED_ShowHexNum(2, 1, w25q_addr_ptr, 8);

			// 移动状态
			usbd_state = USBD_RECV_PACKET;

			USBD_Respond(RESPOND_OK);
		}
		break;
		case CMD_READ_FLASH:
		{
			/*
				读Flash指令如下：
					1. 上位机发送指令头：格式为0xAA BBBBBBBB CCCCCCCC
					   AA为读Flash指令(0x6D)；
					   BBBBBBBB为32位起始地址（小端序）；
					   CCCCCCCC为32位长度，代表从起始地址开始读的字节数（小端序）
					   长度需是1024（1kb）的整数倍
					2. MCU接收到后，向w25q_spi_buffer中读入1kb数据
					   读取完成后，交换缓冲区，w25q_spi_buffer继续读取1kb数据
					   向上位机发送w25q_usb_buffer的前64字节
					   状态机转移到USBD_TSMT_PACKET
					3. 上位机接收到64字节后，回复RESPOND_OK
					   MCU接收到回复后，再传输下一个64字节
					   如此往复，直到w25q_usb_buffer被完全发完
					4. w25q_usb_buffer发完后，交换缓存区，w25q_spi_buffer继续读取1kb数据
					   重复发送直到指定长度
					5. 全部传输完成后，MCU发送RESPOND_OK，清理缓冲区，状态机移动到USBD_IDLE
			*/

			// 分配缓冲区
			if (w25q_usb_buffer != NULL || w25q_spi_buffer != NULL)
			{
				periph_error = PE_OTG_FS_RX_ERROR;
				hardware_error = HE_W25Q_ERROR;
				USBD_Respond(RESPOND_BUSY);
				goto FUNC_END;
			}
			w25q_usb_buffer = (uint8_t *)malloc(sizeof(uint8_t) * W25Q_READ_BUFFER_SIZE);
			w25q_spi_buffer = (uint8_t *)malloc(sizeof(uint8_t) * W25Q_READ_BUFFER_SIZE);
			w25q_usb_buffer_ptr = w25q_usb_buffer;

			// 记录地址指针
			w25q_addr_ptr = (uint32_t)UserRxBuffer[1];
			w25q_addr_ptr |= (UserRxBuffer[2] << 8);
			w25q_addr_ptr |= (UserRxBuffer[3] << 16);
			w25q_addr_ptr |= (UserRxBuffer[4] << 24);

			// OLED_ShowHexNum(2, 1, w25q_addr_ptr, 8);

			// 记录读取长度
			w25q_read_len = (uint32_t)UserRxBuffer[5];
			w25q_read_len |= (UserRxBuffer[6] << 8);
			w25q_read_len |= (UserRxBuffer[7] << 16);
			w25q_read_len |= (UserRxBuffer[8] << 24);

			// 读取Flash
			if (W25Q_ReadData_4ba_DMA(w25q_addr_ptr, w25q_spi_buffer, W25Q_READ_BUFFER_SIZE) != HAL_OK)
			{
				periph_error = PE_SPI1_RX_ERROR;
				hardware_error = HE_W25Q_ERROR;
				USBD_CleanUpRWFlash();
				USBD_Respond(RESPOND_BUSY);
				goto FUNC_END;
			}

			// 地址自增
			w25q_addr_ptr += W25Q_READ_BUFFER_SIZE;
			w25q_read_len -= W25Q_READ_BUFFER_SIZE;

			// 等待读取完成
			if (SPI_WaitRx() != HAL_OK)
			{
				periph_error = PE_SPI1_RX_ERROR;
				hardware_error = HE_W25Q_ERROR;
				USBD_CleanUpRWFlash();
				USBD_Respond(RESPOND_BUSY);
				goto FUNC_END;
			}

			USBD_SwapW25QBuffer();
			w25q_usb_buffer_ptr = w25q_usb_buffer;

			// 读取Flash
			if (W25Q_ReadData_4ba_DMA(w25q_addr_ptr, w25q_spi_buffer, W25Q_READ_BUFFER_SIZE) != HAL_OK)
			{
				periph_error = PE_SPI1_RX_ERROR;
				hardware_error = HE_W25Q_ERROR;
				USBD_CleanUpRWFlash();
				USBD_Respond(RESPOND_BUSY);
				goto FUNC_END;
			}

			// 发送64字节
			if (CDC_Transmit_FS(w25q_usb_buffer_ptr, USBD_PACKET_SIZE) != HAL_OK)
			{
				periph_error = PE_OTG_FS_TX_ERROR;
				USBD_CleanUpRWFlash();
				USBD_Respond(RESPOND_BUSY);
				goto FUNC_END;
			}

			// 地址自增
			w25q_usb_buffer_ptr += USBD_PACKET_SIZE;

			// 状态转移
			usbd_state = USBD_TSMT_PACKET;
		}
		break;
		case CMD_CLEAN_FLASH_A:
		{
			DEBUG_CODE(OLED_ShowString(1, 1, "Chip Erase"););
			if (UserRxBuffer[1] == CMD_CLEAN_FLASH_B &&
				UserRxBuffer[2] == CMD_CLEAN_FLASH_C &&
				UserRxBuffer[3] == CMD_CLEAN_FLASH_D)
			{
				USBD_Respond(RESPOND_OK);

				HAL_StatusTypeDef state = W25Q_ChipErase();
				if (state == HAL_OK)
					state = W25Q_WaitBusy(99999999);
				OLED_ShowNum(3, 1, state, 1);
				switch (state)
				{
				case HAL_OK:
					USBD_Respond(RESPOND_OK);
					break;
				case HAL_TIMEOUT:
					USBD_Respond(RESPOND_TIMEOUT);
					break;
				case HAL_BUSY:
					USBD_Respond(RESPOND_BUSY);
					break;
				default:
					USBD_Respond(RESPOND_ERROR);
					break;
				}
			}
		}
		break;
		case CMD_SET_SPEED:
		{
			/* 设置各关节的最大速度
		     * 格式为 76 M1M1M1M1 M2M2M2M2 M3M3M3M3 M4M4M4M4		
			 */
			float m1, m2, m3, m4, s1, s2;
			DESERIALIZE(UserRxBuffer + 1, m1);
			DESERIALIZE(UserRxBuffer + 5, m2);
			DESERIALIZE(UserRxBuffer + 9, m3);
			DESERIALIZE(UserRxBuffer + 13, m4);
			DESERIALIZE(UserRxBuffer + 17, s1);
			DESERIALIZE(UserRxBuffer + 21, s2);

			DEBUG_CODE(
				OLED_ShowString(3, 1, "SetSpd");
			);

			Joint_SetMaxSpeedPercentage(&m1h, m1);
			Joint_SetMaxSpeedPercentage(&m2h, m2);
			Joint_SetMaxSpeedPercentage(&m3h, m3);
			Joint_SetMaxSpeedPercentage(&m4h, m4);
			S1_SetSpeed(s1);
			Gripper_SetSpeedPercentage(s2);

			USBD_Respond(RESPOND_OK);
		}
		break;
		default:
			break;
		}
		break;
	case USBD_RECV_PACKET:
	{
		if (Recv_dlen == 1 && UserRxBuffer[0] == CMD_END_WRITE_FLASH)
		{
			// Error_Handler();
			// 全部写入
			if (w25q_usb_buffer_state == W25Q_USB_BUFFER_HAVENT_SENT)
			{
				// 交换缓存
				USBD_SwapW25QBuffer();
				w25q_usb_buffer_ptr = w25q_usb_buffer;

				// 擦除Sector
				if ((w25q_addr_ptr & 0x0FFF) == 0x0000)
				{
					// OLED_ShowHexNum(4, 2, w25q_addr_ptr, 8);

					if (W25Q_SectorErase_4ba(w25q_addr_ptr) != HAL_OK)
					{
						hardware_error = HE_W25Q_ERROR;
						USBD_CleanUpRWFlash();
						USBD_Respond(RESPOND_ERROR);
						goto FUNC_END;
					}
				}

				// OLED_ShowHexNum(4, 1, w25q_addr_ptr, 8);

				// 启动发送
				if (SPI_WaitTx() != HAL_OK)
				{
					periph_error = PE_SPI1_TX_ERROR;
					hardware_error = HE_W25Q_ERROR;
					USBD_CleanUpRWFlash();
					USBD_Respond(RESPOND_ERROR);
					goto FUNC_END;
				}
				if (W25Q_PageProgram_4ba_DMA(w25q_addr_ptr, w25q_spi_buffer, W25Q_WRITE_BUFFER_SIZE) != HAL_OK)
				{
					periph_error = PE_SPI1_TX_ERROR;
					hardware_error = HE_W25Q_ERROR;
					USBD_CleanUpRWFlash();
					USBD_Respond(RESPOND_ERROR);
					goto FUNC_END;
				}
			}

			// 终止写Flash
			if (SPI_WaitTx() != HAL_OK)
			{
				periph_error = PE_SPI1_TX_ERROR;
				hardware_error = HE_W25Q_ERROR;
			}
			USBD_CleanUpRWFlash();
			USBD_Respond(RESPOND_OK);
		}
		else
		{
			// 将数据转移到w25q_usb_buffer
			// 此时DMA2_Stream0必然空闲，可以使用
			if (DMA2_Stream0_MemToMem_Start(UserRxBuffer, w25q_usb_buffer_ptr, USBD_PACKET_SIZE) != HAL_OK)
			{
				periph_error = PE_DMA_ERROR;
				hardware_error = HE_W25Q_ERROR;
				USBD_CleanUpRWFlash();
				USBD_Respond(RESPOND_ERROR);
				goto FUNC_END;
			}
			w25q_usb_buffer_state = W25Q_USB_BUFFER_HAVENT_SENT;

			w25q_usb_buffer_ptr += USBD_PACKET_SIZE;
			// 写入Flash
			if (w25q_usb_buffer_ptr - w25q_usb_buffer >= W25Q_WRITE_BUFFER_SIZE)
			{
				// 交换缓存
				USBD_SwapW25QBuffer();
				w25q_usb_buffer_ptr = w25q_usb_buffer;

				// 擦除扇区
				if ((w25q_addr_ptr & 0x0FFF) == 0x0000)
				{
					// OLED_ShowString(4, 1, "E");
					// OLED_ShowHexNum(4, 2, w25q_addr_ptr, 8);

					if (W25Q_SectorErase_4ba(w25q_addr_ptr) != HAL_OK)
					{
						hardware_error = HE_W25Q_ERROR;
						USBD_CleanUpRWFlash();
						USBD_Respond(RESPOND_ERROR);
						goto FUNC_END;
					}
				}


				// OLED_ShowHexNum(4, 2, w25q_addr_ptr, 8);

				// 启动发送
				if (SPI_WaitTx() != HAL_OK)
				{
					periph_error = PE_SPI1_TX_ERROR;
					hardware_error = HE_W25Q_ERROR;
					USBD_CleanUpRWFlash();
					USBD_Respond(RESPOND_ERROR);
					goto FUNC_END;
				}
				if (W25Q_PageProgram_4ba_DMA(w25q_addr_ptr, w25q_spi_buffer, W25Q_WRITE_BUFFER_SIZE) != HAL_OK)
				{
					periph_error = PE_SPI1_TX_ERROR;
					hardware_error = HE_W25Q_ERROR;
					USBD_CleanUpRWFlash();
					USBD_Respond(RESPOND_ERROR);
					goto FUNC_END;
				}

				// 地址自增
				w25q_addr_ptr += W25Q_WRITE_BUFFER_SIZE;
				w25q_usb_buffer_state = W25Q_USB_BUFFER_SENT;
			}

			USBD_Respond(RESPOND_OK);
		}
	}
	break;
	case USBD_TSMT_PACKET:
	{
		// OLED_ShowSignedNum(2, 1, w25q_read_len, 5);

		if (Recv_dlen == 1 && UserRxBuffer[0] == RESPOND_OK)
		{
			// 检查w25q_usb_buffer是否传输完成
			if (w25q_usb_buffer_ptr - w25q_usb_buffer == W25Q_READ_BUFFER_SIZE)
			{
				// 检查是否全部传输完毕
				if (w25q_read_len <= 0)
				{
					// 全部传输完成，停止传输
					// 等待读取完成
					if (SPI_WaitRx() != HAL_OK)
					{
						periph_error = PE_SPI1_RX_ERROR;
						hardware_error = HE_W25Q_ERROR;
						USBD_CleanUpRWFlash();
						USBD_Respond(RESPOND_BUSY);
						goto FUNC_END;
					}

					USBD_Respond(RESPOND_OK);
					USBD_CleanUpRWFlash();
					goto FUNC_END;
				}
				else
				{
					// 未全部完成
					// 等待读取完成
					if (SPI_WaitRx() != HAL_OK)
					{
						periph_error = PE_SPI1_RX_ERROR;
						hardware_error = HE_W25Q_ERROR;
						USBD_CleanUpRWFlash();
						USBD_Respond(RESPOND_BUSY);
						goto FUNC_END;
					}

					// 交换缓冲
					USBD_SwapW25QBuffer();
					w25q_usb_buffer_ptr = w25q_usb_buffer;

					// 读取Flash
					if (W25Q_ReadData_4ba_DMA(w25q_addr_ptr, w25q_spi_buffer, W25Q_READ_BUFFER_SIZE) != HAL_OK)
					{
						periph_error = PE_SPI1_RX_ERROR;
						hardware_error = HE_W25Q_ERROR;
						USBD_CleanUpRWFlash();
						USBD_Respond(RESPOND_BUSY);
						goto FUNC_END;
					}

					// 地址自增
					w25q_addr_ptr += W25Q_READ_BUFFER_SIZE;
					w25q_read_len -= W25Q_READ_BUFFER_SIZE;
				}
			}
			
			// 发送64字节
			if (CDC_Transmit_FS(w25q_usb_buffer_ptr, USBD_PACKET_SIZE) != HAL_OK)
			{
				periph_error = PE_OTG_FS_TX_ERROR;
				USBD_CleanUpRWFlash();
				USBD_Respond(RESPOND_BUSY);
				goto FUNC_END;
			}

			// 地址自增
			w25q_usb_buffer_ptr += USBD_PACKET_SIZE;
		}
		else
		{
			USBD_Respond(RESPOND_ERROR);
			USBD_CleanUpRWFlash();
			usbd_state = USBD_IDLE;
		}
	}
	break;
	default:
		break;
	}

FUNC_END:
	Recv_dlen = 0;
	usbd_work_state = USBD_WORK_IDLE;
}

// PRIVATE
HAL_StatusTypeDef USBD_Respond(uint8_t respond)
{
	return (HAL_StatusTypeDef)CDC_Transmit_FS(&respond, 1);
}

void USBD_SwapW25QBuffer()
{
	uint8_t *temp = w25q_usb_buffer;
	w25q_usb_buffer = w25q_spi_buffer;
	w25q_spi_buffer = temp;
}

void USBD_CleanUpRWFlash()
{
	usbd_state = USBD_IDLE;
	free(w25q_usb_buffer);
	free(w25q_spi_buffer);
	w25q_usb_buffer = NULL;
	w25q_spi_buffer = NULL;
}
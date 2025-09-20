/* USER CODE BEGIN Header */
/**
 ******************************************************************************
 * @file           : main.c
 * @brief          : Main program body
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2025 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file
 * in the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *
 ******************************************************************************
 */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "can.h"
#include "dma.h"
#include "i2c.h"
#include "spi.h"
#include "tim.h"
#include "usart.h"
#include "usb_device.h"
#include "gpio.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include <stdlib.h>
#include <math.h>

#include "OLED.h"
#include "MS42D.h"
#include "Servo.h"
#include "W25Q.h"
#include "ADS1115.h"
#include "USBD_ctrl.h"
#include "Joint.h"
#include "vm.h"
#include "OperationMode.h"
#include "AllJoint.h"
#include "error.h"
#include "Gripper.h"
#include "trigonometric.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */
// extern uint8_t joint_timit_state;
// extern Joint_HandleTypeDef m1h;
/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

/**
 * @brief  The application entry point.
 * @retval int
 */
int main(void)
{

	/* USER CODE BEGIN 1 */
	// 上电延迟
	for (uint32_t i = 0; i < 500; i++)
	{
		for (uint32_t j = 0; j < 500; j++)
		{
		}
	}

	/* USER CODE END 1 */

	/* MCU Configuration--------------------------------------------------------*/

	/* Reset of all peripherals, Initializes the Flash interface and the Systick. */
	HAL_Init();

	/* USER CODE BEGIN Init */
	/* USER CODE END Init */

	/* Configure the system clock */
	SystemClock_Config();

	/* USER CODE BEGIN SysInit */
	PE1_Init();
	/* USER CODE END SysInit */

	/* Initialize all configured peripherals */
	MX_GPIO_Init();
	MX_DMA_Init();
	MX_I2C3_Init();
	MX_CAN2_Init();
	MX_USART3_UART_Init();
	MX_SPI1_Init();
	MX_USB_DEVICE_Init();
	MX_I2C2_Init();
	MX_TIM2_Init();
	MX_TIM3_Init();
	MX_TIM4_Init();
	/* USER CODE BEGIN 2 */
	OLED_Init();
	S1_Init();
	Gripper_Init();
	AllJoint_Init();
	W25Q_Init();
	TIM2_IT_Start();

	// USART_SendStr("#255PBD0!");

	/* USER CODE END 2 */

	/* Infinite loop */
	/* USER CODE BEGIN WHILE */
	while (1)
	{
		// if (periph_error != PE_NO_ERROR)
		// 	break;

		Operation_Poll();
		// USART_SendStr("#000PBD0!");
		// HAL_Delay(1000);

		/* USER CODE END WHILE */

		/* USER CODE BEGIN 3 */
	}

	// OLED_Clear();
	// OLED_ShowString(1, 1, Error_GetPeriphErrorStr(periph_error));
	/* USER CODE END 3 */
}

/**
 * @brief System Clock Configuration
 * @retval None
 */
void SystemClock_Config(void)
{
	RCC_OscInitTypeDef RCC_OscInitStruct = {0};
	RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

	/** Configure the main internal regulator output voltage
	 */
	__HAL_RCC_PWR_CLK_ENABLE();
	__HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

	/** Initializes the RCC Oscillators according to the specified parameters
	 * in the RCC_OscInitTypeDef structure.
	 */
	RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
	RCC_OscInitStruct.HSEState = RCC_HSE_ON;
	RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
	RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
	RCC_OscInitStruct.PLL.PLLM = 25;
	RCC_OscInitStruct.PLL.PLLN = 336;
	RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2;
	RCC_OscInitStruct.PLL.PLLQ = 7;
	if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
	{
		Error_Handler();
	}

	/** Initializes the CPU, AHB and APB buses clocks
	 */
	RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK | RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
	RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
	RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
	RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV4;
	RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV2;

	if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_5) != HAL_OK)
	{
		Error_Handler();
	}
}

/* USER CODE BEGIN 4 */
uint32_t myabs(int32_t num)
{
	return num > 0 ? num : -num;
}

void MotorTest()
{
	/* USER CODE BEGIN 1 */
	// 上电延迟
	for (uint32_t i = 0; i < 500; i++)
	{
		for (uint32_t j = 0; j < 500; j++)
		{
		}
	}
	/* USER CODE END 1 */

	/* MCU Configuration--------------------------------------------------------*/

	/* Reset of all peripherals, Initializes the Flash interface and the Systick. */
	HAL_Init();

	/* USER CODE BEGIN Init */
	/* USER CODE END Init */

	/* Configure the system clock */
	SystemClock_Config();

	/* USER CODE BEGIN SysInit */
	PE1_Init();
	/* USER CODE END SysInit */

	/* Initialize all configured peripherals */
	MX_GPIO_Init();
	MX_DMA_Init();
	MX_I2C3_Init();
	MX_CAN2_Init();
	//   MX_USART3_UART_Init();
	//   MX_SPI1_Init();
	//   MX_USB_DEVICE_Init();
	//   MX_I2C2_Init();
	MX_TIM2_Init();
	/* USER CODE BEGIN 2 */
	OLED_Init();
	OLED_ShowString(1, 1, "OLED OK");

	// Joint_Init();
	// HAL_Delay(1000);
	// Joint_SetTarget(2000);

	TIM2_IT_Start();
	/* USER CODE END 2 */

	/* Infinite loop */
	/* USER CODE BEGIN WHILE */
	while (1)
	{
		// Joint_TimItHandler();

		/* USER CODE END WHILE */

		/* USER CODE BEGIN 3 */
	}
	/* USER CODE END 3 */
}

void W25QDMATest()
{
	/* USER CODE BEGIN 1 */
	// 上电延迟
	for (uint32_t i = 0; i < 500; i++)
	{
		for (uint32_t j = 0; j < 500; j++)
		{
		}
	}
	/* USER CODE END 1 */

	/* MCU Configuration--------------------------------------------------------*/

	/* Reset of all peripherals, Initializes the Flash interface and the Systick. */
	HAL_Init();

	/* USER CODE BEGIN Init */
	/* USER CODE END Init */

	/* Configure the system clock */
	SystemClock_Config();

	/* USER CODE BEGIN SysInit */
	PE1_Init();
	/* USER CODE END SysInit */

	/* Initialize all configured peripherals */
	MX_GPIO_Init();
	MX_DMA_Init();
	MX_I2C3_Init();
	//   MX_CAN2_Init();
	//   MX_USART3_UART_Init();
	MX_SPI1_Init();
	//   MX_USB_DEVICE_Init();
	//   MX_I2C2_Init();
	/* USER CODE BEGIN 2 */
	OLED_Init();
	// OLED_ShowString(1, 1, "OLED OK");

	W25Q_Init();

	uint8_t data[256];
	// 	0x00, 0x01, 0x02, 0x03, 0x04,
	// 	0x05, 0x06, 0x07, 0x08, 0x09,
	// 	0x0A, 0x0B, 0x0C, 0x0D, 0x0E,
	// 	0x0F, 0x10, 0x11, 0x12, 0x13
	// };
	uint8_t buffer[256];

	/* USER CODE END 2 */

	/* Infinite loop */
	/* USER CODE BEGIN WHILE */
	while (1)
	{
		uint32_t start = HAL_GetTick();
		if (W25Q_SectorErase_4ba(0x00) != HAL_OK)
		{
			// Error_Handler();
		}
		if (W25Q_PageProgram_4ba_DMA(0x00, data, 256) != HAL_OK)
		{
			// Error_Handler();
		}
		SPI_WaitTx();
		if (W25Q_ReadData_4ba_DMA(0x00, buffer, 256) != HAL_OK)
		{
			// Error_Handler();
		}
		SPI_WaitRx();
		OLED_ShowNum(1, 1, HAL_GetTick() - start, 3);
		// for (int y = 0; y < 4; y++)
		// {
		// 	for (int x = 0; x < 5; x++)
		// 	{
		// 		OLED_ShowHexNum(y + 1, 3 * x + 1, buffer[y * 5 + x], 2);
		// 	}
		// }

		// for (int i = 0; i < 20; i++)
		// {
		// 	data[i]++;
		// }

		// OLED_ShowNum(4, 1, dma2_stream0_state, 1);
		// OLED_ShowString(1, 1, Error_GetPeriphErrorStr(periph_error));
		// USBD_Poll();
		/* USER CODE END WHILE */

		/* USER CODE BEGIN 3 */
	}
	/* USER CODE END 3 */
}

void ADS1115Test()
{
	// HAL_StatusTypeDef state = HAL_I2C_Master_Transmit(&hi2c2, 0x90, &cmd, 1, 100);
	HAL_StatusTypeDef state = ADS1115_Config();

	if (state == HAL_OK)
		OLED_ShowString(2, 1, "ADS1115 OK");
	else if (state == HAL_ERROR)
		OLED_ShowString(2, 1, "ERR");
	else if (state == HAL_BUSY)
		OLED_ShowString(2, 1, "BUSY");
	else if (state == HAL_TIMEOUT)
		OLED_ShowString(2, 1, "TIMEOUT");

	// OLED_ShowNum(3, 1, hi2c2.ErrorCode, 2);

	uint16_t result = 0;
	/* USER CODE END 2 */

	/* Infinite loop */
	/* USER CODE BEGIN WHILE */
	while (1)
	{
		if (ADS1115_ReadContinuous(&result) == HAL_OK)
			OLED_ShowString(3, 1, "OK");
		else
			OLED_ShowString(3, 1, "ER");

		OLED_ShowNum(4, 1, result, 5);

		HAL_Delay(100);

		/* USER CODE END WHILE */

		/* USER CODE BEGIN 3 */
	}
	/* USER CODE END 3 */
}

void W25QTest()
{
	/* USER CODE BEGIN 2 */
	OLED_Init();
	// OLED_ShowString(1, 1, "OLED OK");

	W25Q_Init();

	uint8_t arr_0[] = {0x01, 0x02, 0x03, 0x04};
	uint8_t arr_1[] = {0x00, 0x00, 0x00, 0x00};

	/* USER CODE END 2 */

	/* Infinite loop */
	/* USER CODE BEGIN WHILE */
	while (1)
	{
		uint32_t start = HAL_GetTick();
		W25Q_SectorErase_4ba(0x000000);
		W25Q_PageProgram_4ba(0x000000, arr_0, 4);
		W25Q_ReadData_4ba(0x000000, arr_1, 4);
		uint32_t W25Q_end = HAL_GetTick();

		OLED_ShowHexNum(3, 1, arr_0[0], 2);
		OLED_ShowHexNum(3, 4, arr_0[1], 2);
		OLED_ShowHexNum(3, 7, arr_0[2], 2);
		OLED_ShowHexNum(3, 10, arr_0[3], 2);
		OLED_ShowHexNum(4, 1, arr_1[0], 2);
		OLED_ShowHexNum(4, 4, arr_1[1], 2);
		OLED_ShowHexNum(4, 7, arr_1[2], 2);
		OLED_ShowHexNum(4, 10, arr_1[3], 2);

		uint32_t OLED_end = HAL_GetTick();

		OLED_ShowNum(1, 1, W25Q_end - start, 5);
		OLED_ShowNum(2, 1, OLED_end - W25Q_end, 5);

		++arr_0[0];
		++arr_0[1];
		++arr_0[2];
		++arr_0[3];

		/* USER CODE END WHILE */

		/* USER CODE BEGIN 3 */
	}
	/* USER CODE END 3 */
}

void ServoTest()
{
	/* USER CODE BEGIN 2 */
	OLED_Init();
	OLED_ShowString(1, 1, "OLED OK");

	if (Servo_Init() == HAL_OK)
	{
		OLED_ShowString(2, 1, "SERVO OK");
	}
	else
	{
		OLED_ShowString(1, 1, "SERVO ERROR");
		Error_Handler();
	}

	// MS42D_Init();
	// OLED_ShowString(2, 1, "MS42D OK");
	// HAL_Delay(10);

	// MS42D_SetMoment(1, MS42D_DIR_ROT_CLOCKWISE, 40, 800);
	// OLED_ShowString(2, 1, "MS42D ACTIVE");
	// HAL_Delay(10);
	// uint8_t id;
	// uint8_t has_achieved;
	// float speed;
	// float angle;

	/* USER CODE END 2 */

	/* Infinite loop */
	/* USER CODE BEGIN WHILE */
	while (1)
	{
		int angle = myabs((int)((HAL_GetTick() / 10) % 540) - 270);
		OLED_ShowSignedNum(1, 1, angle, 3);
		if (Servo_SetAngle(0, angle, 10) == HAL_OK)
		{
			OLED_ShowString(3, 1, "SEND SUCCESS");
		}
		else
		{
			OLED_ShowString(3, 1, "SEND FAILED");
		}
		OLED_ShowFloatNum(4, 1, Servo_GetAngle(0), 3, 3);
		HAL_Delay(8);

		// MS42D_RequestData(1);
		// if (MS42D_GetFeedback(&id, &has_achieved, &speed, &angle) != 0)
		// {
		// 	OLED_ShowFloatNum(3, 1, speed, 2, 3);
		// 	OLED_ShowFloatNum(4, 1, angle, 5, 1);
		// }
		// else
		// {
		// 	OLED_ShowString(3, 1, "ERR0R");
		// }

		// HAL_Delay(10);
		/* USER CODE END WHILE */

		/* USER CODE BEGIN 3 */
	}
	/* USER CODE END 3 */
}

/* USER CODE END 4 */

/**
 * @brief  This function is executed in case of error occurrence.
 * @retval None
 */
void Error_Handler(void)
{
	/* USER CODE BEGIN Error_Handler_Debug */
	/* User can add his own implementation to report the HAL error return state */
	HAL_GPIO_WritePin(GPIOE, GPIO_PIN_1, GPIO_PIN_RESET);
	__disable_irq();
	while (1)
	{
	}
	/* USER CODE END Error_Handler_Debug */
}

#ifdef USE_FULL_ASSERT
/**
 * @brief  Reports the name of the source file and the source line number
 *         where the assert_param error has occurred.
 * @param  file: pointer to the source file name
 * @param  line: assert_param error line source number
 * @retval None
 */
void assert_failed(uint8_t *file, uint32_t line)
{
	/* USER CODE BEGIN 6 */
	/* User can add his own implementation to report the file name and line number,
	   ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
	/* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */

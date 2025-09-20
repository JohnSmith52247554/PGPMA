from serial import SerialTimeoutException
from abc import ABC, abstractmethod
import numpy as np
from typing import List
import queue
import os

from .core import SerialCore
from .msg import MsgType, Message

# respond
RESPOND_OK                  = 0xAA
RESPOND_BUSY                = 0xAD
RESPOND_ERROR               = 0xB0
RESPOND_TIMEOUT             = 0xB3

class AbstractCoord(ABC):
    @abstractmethod
    def get_list(self) -> List[float]:
        pass

class OrthogonalCoord(AbstractCoord):
    def __init__(self, x : float, y : float, z : float, alpha : float,s1 : float, s2 : float):
        self.x = x
        self.y = y
        self.z = z
        self.alpha = alpha
        self.s1 = s1
        self.s2 = s2

    def get_list(self) -> List[float]:
        return [self.x, self.y, self.z, self.alpha, self.s1, self.s2]

    @staticmethod
    def get_size() -> int:
        return 7 * 4

class JointCoord(AbstractCoord):
    def __init__(self, m1 : float, m2 : float, m3 : float, m4 : float, s1 : float, s2 : float):
        self.m1 = m1
        self.m2 = m2
        self.m3 = m3
        self.m4 = m4
        self.s1 = s1
        self.s2 = s2

    @classmethod
    def from_list(cls, joint_coord_list: List[float]):
        if len(joint_coord_list) != 6:
            raise ValueError("joint_coord_list must contain exactly 6 elements")
        return cls(*joint_coord_list)

    def get_list(self) -> List[float]:
        return [self.m1, self.m2, self.m3, self.m4, self.s1, self.s2]

    @staticmethod
    def get_size() -> int:
        return 6 * 4

class SerialCtrl:
    # cmd
    CMD_IMMEDIATE_STOP          = 0x55
    CMD_IMMEDIATE_ORTHOGONAL    = 0x58
    CMD_IMMEDIATE_JOINT         = 0x5B
    CMD_OPEN_GRIPPER            = 0x5E
    CMD_CLOSE_GRIPPER           = 0x61
    CMD_GET_STATE               = 0x64
    CMD_VISUAL                  = 0x67
    CMD_WRITE_FLASH             = 0x6A
    CMD_READ_FLASH              = 0x6D
    CMD_RESET                   = 0x70
    CMD_END_WRITE_FLASH         = 0x73
    CMD_SET_SPEED               = 0x76

    CMD_CLEAN_FLASH_A           = 0xAB
    CMD_CLEAN_FLASH_B           = 0xCD
    CMD_CLEAN_FLASH_C           = 0xEF
    CMD_CLEAN_FLASH_D           = 0x01

    USD_CDC_PACKET_SIZE         = 64
    IO_BUFFER_SIZE              = 4096

    def __init__(self, GUI):
        self.GUI = GUI
        self.core = SerialCore(GUI)
        self.task_queue = queue.Queue()

    def open_port(self, port : str, baudrate : int, timeout : float):
        try:
            self.core.open_port(port, baudrate, timeout)
        except:
            self.GUI.add_message(Message(MsgType.OPEN_PORT, "FAILED"))
        else:
            self.GUI.add_message(Message(MsgType.OPEN_PORT, "OK"))

    # private methods
    @staticmethod
    def _serialize(float_list : List[float]) -> bytes:
        float_np = np.array(float_list, dtype='<f4')
        return float_np.astype('<f4').tobytes()

    @staticmethod
    def _deserialize(byte_data : bytes) -> List[float]:
        float_np = np.frombuffer(byte_data, dtype=np.float32)
        return float_np.tolist()

    def _send_byte_cmd(self, cmd : int):
        data = bytes([cmd])
        try:
            self.core.send(data)
            respond = self.core.recv(1)
            if len(respond) == 0:
                return RESPOND_TIMEOUT
            return respond[0]
        except SerialTimeoutException:
            return RESPOND_TIMEOUT
        except:
            return RESPOND_ERROR

    def _send_float_list_cmd(self, cmd : int, float_list : List[float]) -> int:
        data = bytes([cmd]) + self._serialize(float_list)
        try:
            self.core.send(data)
            respond = self.core.recv(1)
            if len(respond) == 0:
                return RESPOND_TIMEOUT
            return respond[0]
        except SerialTimeoutException:
            return RESPOND_TIMEOUT
        except:
            return RESPOND_ERROR

    # public methods
    def immediate_stop(self) -> int:
        #self.GUI.add_message(Msg.SET_PROGRESS_BAR + "0")
        self.GUI.add_message(Message(MsgType.SET_PROGRESS_BAR, 0))
        result = self._send_byte_cmd(self.CMD_IMMEDIATE_STOP)
        #self.GUI.add_message(Msg.SET_PROGRESS_BAR + "100")
        self.GUI.add_message(Message(MsgType.SET_PROGRESS_BAR, 100))
        return result

    def reset(self) -> int:
        #self.GUI.add_message(Msg.SET_PROGRESS_BAR + "0")
        self.GUI.add_message(Message(MsgType.SET_PROGRESS_BAR, 0))
        result = self._send_byte_cmd(self.CMD_RESET)
        #self.GUI.add_message(Msg.SET_PROGRESS_BAR + "100")
        self.GUI.add_message(Message(MsgType.SET_PROGRESS_BAR, 100))
        return result

    def immediate_orthogonal(self, coord : OrthogonalCoord) -> int:
        #self.GUI.add_message(Msg.SET_PROGRESS_BAR + "0")
        self.GUI.add_message(Message(MsgType.SET_PROGRESS_BAR, 0))
        result = self._send_float_list_cmd(self.CMD_IMMEDIATE_ORTHOGONAL, coord.get_list())
        #self.GUI.add_message(Msg.SET_PROGRESS_BAR + "100")
        self.GUI.add_message(Message(MsgType.SET_PROGRESS_BAR, 100))
        return result

    def immediate_joint(self, coord : JointCoord) -> int:
        #self.GUI.add_message(Msg.SET_PROGRESS_BAR + "0")
        self.GUI.add_message(Message(MsgType.SET_PROGRESS_BAR, 0))
        result = self._send_float_list_cmd(self.CMD_IMMEDIATE_JOINT, coord.get_list())
        #self.GUI.add_message(Msg.SET_PROGRESS_BAR + "100")
        self.GUI.add_message(Message(MsgType.SET_PROGRESS_BAR, 100))
        return result

    def visual_mode(self, x : float, y : float, rot : float, qr_id : int) -> int:
        data = bytes([self.CMD_VISUAL]) + self._serialize([x, y, rot]) + bytes([qr_id & 0xFF, (qr_id >> 8) & 0xFF, (qr_id >> 16) & 0xFF, (qr_id >> 24) & 0xFF])
        try:
            self.core.send(data)
            respond = self.core.recv(1)
            if len(respond) == 0:
                return RESPOND_TIMEOUT
            return respond[0]
        except SerialTimeoutException:
            return RESPOND_TIMEOUT
        except:
            return RESPOND_ERROR

    def get_state(self) -> dict:
        self.GUI.add_message(Message(MsgType.SET_PROGRESS_BAR, 0))
        output = {"state" : RESPOND_OK, "joint_coord" : JointCoord(0, 0, 0, 0, 0, 0)}
        try:
            self.core.send(bytes([self.CMD_GET_STATE]))
            float_bytes = self.core.recv(JointCoord.get_size() + 4)
            if len(float_bytes) != JointCoord.get_size() + 4:
                output["state"] = RESPOND_TIMEOUT
                return output
            elif float_bytes[0] != RESPOND_OK:
                output["state"] = RESPOND_ERROR
                return output

            output["state"] = RESPOND_OK
            output["joint_coord"] = JointCoord.from_list(self._deserialize(float_bytes[4:]))
        except SerialTimeoutException:
            output["state"] = RESPOND_TIMEOUT
            return output
        finally:
            self.GUI.add_message(Message(MsgType.SET_PROGRESS_BAR, 100))
        return output

    def open_gripper(self) -> int:
        return self._send_byte_cmd(self.CMD_OPEN_GRIPPER)

    def close_gripper(self) -> int:
        return self._send_byte_cmd(self.CMD_CLOSE_GRIPPER)

    def write_flash(self, addr : int, file_path : str) -> int:
        # 发送指令头
        cmd = bytes([self.CMD_WRITE_FLASH, addr & 0xFF, (addr >> 8) & 0xFF, (addr >> 16) & 0xFF, (addr >> 24) & 0xFF])
        try:
            self.core.send(cmd)
            respond = self.core.recv(1)
            if len(respond) == 0:
                return RESPOND_TIMEOUT
            if respond[0] != RESPOND_OK:
                return respond[0]
        except SerialTimeoutException:
            return RESPOND_TIMEOUT
        except:
            return RESPOND_ERROR

        self.GUI.add_message(Message(MsgType.SET_PROGRESS_BAR, 0))

        # 发送文件
        try:
            with open(file_path, 'rb') as file:
                file_size = os.path.getsize(file_path)
                write_percentage = 0.0

                while True:
                    # 读取文件块
                    chunk = file.read(self.IO_BUFFER_SIZE)
                    if not chunk:
                        break

                    for i in range(0, len(chunk), self.USD_CDC_PACKET_SIZE):
                        sub_chunk = chunk[i:i + self.USD_CDC_PACKET_SIZE]
                        if len(sub_chunk) < self.USD_CDC_PACKET_SIZE:
                            padding = bytes([0xFF] * (self.USD_CDC_PACKET_SIZE - len(sub_chunk)))
                            sub_chunk += padding

                        # 发送文件块
                        try:
                            self.core.send(sub_chunk)
                            respond = self.core.recv(1)
                            write_percentage += float(len(sub_chunk)) / float(file_size) * 100.0
                            write_percentage = min(write_percentage, 100)
                            self.GUI.add_message(Message(MsgType.SET_PROGRESS_BAR, write_percentage))
                            if len(respond) == 0:
                                return RESPOND_TIMEOUT
                            if respond[0] != RESPOND_OK:
                                return respond[0]
                        except SerialTimeoutException:
                            return RESPOND_TIMEOUT
                        except:
                            return RESPOND_ERROR

                    '''
                    if len(chunk) < self.USD_CDC_PACKET_SIZE:
                        padding = bytes([0xFF] * (self.USD_CDC_PACKET_SIZE - len(chunk)))
                        chunk += padding

                    # 发送文件块
                    try:
                        self.core.send(chunk)
                        respond = self.core.recv(1)
                        if len(respond) == 0:
                            return RESPOND_TIMEOUT
                        if respond[0] != RESPOND_OK:
                            return respond[0]
                        write_percentage += float(self.USD_CDC_PACKET_SIZE) / float(file_size) * 100.0
                        write_percentage = min(write_percentage, 100)
                        self.GUI.add_message(Message(MsgType.SET_PROGRESS_BAR, write_percentage))
                    except SerialTimeoutException:
                        return RESPOND_TIMEOUT
                    '''

        except FileNotFoundError:
            self.GUI.add_message(Message(MsgType.CREATE_ERROR_WINDOW, "文件无法打开"))
            return RESPOND_OK

        # 发送结束指令
        try:
            self.core.send(bytes([self.CMD_END_WRITE_FLASH]))
            respond = self.core.recv(1)
            self.GUI.add_message(Message(MsgType.SET_PROGRESS_BAR, 100))
            self.GUI.add_message(Message(MsgType.CREATE_INFO_WINDOW, "写入Flash成功"))
            if len(respond) == 0:
                return RESPOND_TIMEOUT
            return respond[0]
        except SerialTimeoutException:
            return RESPOND_TIMEOUT

    def read_flash(self, addr : int, size : int, file_path : str) -> int:
        # 发送指令头
        cmd = bytes([self.CMD_READ_FLASH, addr & 0xFF, (addr >> 8) & 0xFF, (addr >> 16) & 0xFF, (addr >> 24) & 0xFF, size & 0xFF, (size >> 8) & 0xFF, (size >> 16) & 0xFF, (size >> 24) & 0xFF])
        read_percentage = 0.0
        self.GUI.add_message(Message(MsgType.SET_PROGRESS_BAR, 0))
        try:
            with open(file_path, 'wb') as file:
                self.core.send(cmd)
                while True:
                    respond = self.core.recv(self.USD_CDC_PACKET_SIZE)
                    if len(respond) == self.USD_CDC_PACKET_SIZE:
                        # 成功读取，写入文件
                        file.write(respond)
                        # 发送ACK
                        self.core.send(bytes([RESPOND_OK]))
                        read_percentage += float(self.USD_CDC_PACKET_SIZE) / float(size) * 100.0
                        read_percentage = min(read_percentage, 100)
                        self.GUI.add_message(Message(MsgType.SET_PROGRESS_BAR, read_percentage))
                    elif len(respond) == 1 and respond[0] == RESPOND_OK:
                        # 完成读取
                        self.GUI.add_message(Message(MsgType.SET_PROGRESS_BAR, 100))
                        self.GUI.add_message(Message(MsgType.CREATE_INFO_WINDOW, "读取Flash成功"))
                        break
                    else:
                        # 读取失败
                        return RESPOND_ERROR
        except SerialTimeoutException:
            return RESPOND_TIMEOUT
        except FileNotFoundError:
            self.GUI.add_message(Message(MsgType.CREATE_ERROR_WINDOW, "文件无法打开"))
            return RESPOND_OK
        except:
            return RESPOND_ERROR
        return RESPOND_OK

    def clean_flash(self) -> int:
        try:
            self.GUI.add_message(Message(MsgType.SET_PROGRESS_BAR, 0))
            progress = 0
            self.core.send(bytes([self.CMD_CLEAN_FLASH_A, self.CMD_CLEAN_FLASH_B, self.CMD_CLEAN_FLASH_C, self.CMD_CLEAN_FLASH_D]))
            result = self.core.recv(1)
            if not (len(result) > 0 and result[0] == RESPOND_OK):
                return RESPOND_ERROR
            for i in range(100):
                progress += 1
                self.GUI.add_message(Message(MsgType.SET_PROGRESS_BAR, progress))
                result = self.core.recv(1)
                if len(result) > 0 and result[0] == RESPOND_OK:
                    self.GUI.add_message(Message(MsgType.SET_PROGRESS_BAR, 100))
                    self.GUI.add_message(Message(MsgType.CREATE_INFO_WINDOW, "擦除Flash成功"))
                    return RESPOND_OK
            return RESPOND_TIMEOUT
        except SerialTimeoutException:
            return RESPOND_TIMEOUT
        except:
            return RESPOND_ERROR

    def set_speed(self, m1_speed : float, m2_speed : float, m3_speed : float, m4_speed : float, s1_speed : float, s2_speed : float) -> int:
        speed_list = [m1_speed, m2_speed, m3_speed, m4_speed, s1_speed, s2_speed]
        self.GUI.add_message(Message(MsgType.SET_PROGRESS_BAR, 0))
        result = self._send_float_list_cmd(self.CMD_SET_SPEED, speed_list)
        self.GUI.add_message(Message(MsgType.SET_PROGRESS_BAR, 100))
        return result

    def run(self):
        while True:
            task = self.task_queue.get()
            if task is None:
                continue
            elif task.dict["type"] == MsgType.OPEN_PORT:
                port_name = task.dict["data"]
                self.open_port(port_name, 115200, 1)
            elif task.dict["type"] == MsgType.RESET:
                self._result_handler(self.reset())
            elif task.dict["type"] == MsgType.STOP:
                self._result_handler(self.immediate_stop())
            elif task.dict["type"] == MsgType.OPEN_GRIPPER:
                self._result_handler(self.open_gripper())
            elif task.dict["type"] == MsgType.CLOSE_GRIPPER:
                self._result_handler(self.close_gripper())
            elif task.dict["type"] == MsgType.SEND_ORTHOGONAL_CMD:
                self._result_handler(self.immediate_orthogonal(task.dict["data"]))
            elif task.dict["type"] == MsgType.SEND_JOINT_CMD:
                self._result_handler(self.immediate_joint(task.dict["data"]))
            elif task.dict["type"] == MsgType.READ_STATE:
                result = self.get_state()
                if result["state"] != RESPOND_OK:
                    self.GUI.add_message(Message(MsgType.SET_IMM_CONSOLE_TEXT, "获取状态失败"))
                else:
                    text = ("M1: {:.2f}  M2: {:.2f}  M3: {:.2f}\nM4: {:.2f}  S1: {:.2f}  S2: {:.2f}\n"
                            .format(result["joint_coord"].m1, result["joint_coord"].m2, result["joint_coord"].m3, result["joint_coord"].m4, result["joint_coord"].s1, result["joint_coord"].s2))
                    self.GUI.add_message(Message(MsgType.SET_IMM_CONSOLE_TEXT, text))
            elif task.dict["type"] == MsgType.WRITE_FLASH:
                addr = task.dict["data"]["address"]
                file_path = task.dict["data"]["file_path"]
                self._result_handler(self.write_flash(addr, file_path))
            elif task.dict["type"] == MsgType.READ_FLASH:
                addr = task.dict["data"]["address"]
                length = task.dict["data"]["length"]
                save_path = task.dict["data"]["save_path"]
                self._result_handler(self.read_flash(addr, length, save_path))
            elif task.dict["type"] == MsgType.CLEAN_FLASH:
                self._result_handler(self.clean_flash())
            elif task.dict["type"] == MsgType.SEND_SET_SPEED_CMD:
                self._result_handler(self.set_speed(task.dict["data"]["m1_speed"],
                    task.dict["data"]["m2_speed"], task.dict["data"]["m3_speed"],
                    task.dict["data"]["m4_speed"], task.dict["data"]["s1_speed"],
                    task.dict["data"]["s2_speed"]))
            elif task.dict["type"] == MsgType.VISUAL_MODE:
                self._result_handler(self.visual_mode(task.dict["data"]["x"], task.dict["data"]["y"], task.dict["data"]["rot"], task.dict["data"]["qr_id"]))


    def add_task(self, task : Message):
        self.task_queue.put(task)

    def _result_handler(self, result : int):
        if result == RESPOND_BUSY:
           # self.GUI.add_message(Msg.CREATE_ERROR_WINDOW + "机械臂繁忙")
            self.GUI.add_message(Message(MsgType.CREATE_ERROR_WINDOW, "机械臂繁忙"))
        elif result == RESPOND_ERROR:
            #self.GUI.add_message(Msg.CREATE_ERROR_WINDOW + "出现未知错误")
            self.GUI.add_message(Message(MsgType.CREATE_ERROR_WINDOW, "出现未知错误"))
        elif result == RESPOND_TIMEOUT:
            #self.GUI.add_message(Msg.CREATE_ERROR_WINDOW + "通信超时")
            self.GUI.add_message(Message(MsgType.CREATE_ERROR_WINDOW, "通信超时"))
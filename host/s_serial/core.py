import serial
import serial.tools.list_ports

class SerialCore:
    def __init__(self, GUI):
        self.GUI = GUI
        self.serial = serial.Serial()

        self.enable_monitor = True

    def __del__(self):
        self.serial.close()

    def open_port(self, port : str, baudrate : int, timeout : float):
        if self.serial.is_open:
            self.serial.close()
        self.serial = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            stopbits=serial.STOPBITS_ONE,
            parity=serial.PARITY_NONE,
            timeout=timeout
        )

    @staticmethod
    def enum_serial_ports() -> list:
        ports = serial.tools.list_ports.comports()
        devices = [port.device for port in ports]
        return devices

    def send(self, data : bytes) -> None:
        # print(data.hex())
        # print('-')
        self.serial.write(data)
        if self.enable_monitor:
            self.GUI.add_port_monitor_message(data.hex(' ', 2))

    def recv(self, size : int) -> bytes:
        data = self.serial.read(size)
        if self.enable_monitor:
            self.GUI.add_port_monitor_message(data.hex(' ', 2))
        return data

    def set_enable_monitor(self, enable : bool):
        self.enable_monitor = enable
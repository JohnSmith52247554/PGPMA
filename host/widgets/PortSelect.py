import tkinter as tk
from s_serial import SerialCore, Message, MsgType


class PortSelect(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        self.label = tk.Label(self, text="打开串口")

        self.port_name = tk.StringVar()
        self.port_name.set("     ")
        port_list = SerialCore.enum_serial_ports()
        port_list.append("     ")
        self.select_port = tk.OptionMenu(self, self.port_name, *port_list)
        self.select_port.bind("<Button-1>", lambda event: self._refresh_port())

        self.btn_open_port = tk.Button(self, text="打开串口", command=self._open_port)

        self.label_2 = tk.Label(self, text="尚未打开串口")

        self.label.grid(row=0, column=0, columnspan=4)
        self.select_port.grid(row=1, column=0, columnspan=3)
        self.btn_open_port.grid(row=1, column=3)
        self.label_2.grid(row=2, column=0, columnspan=4)

    def _refresh_port(self):
        self.select_port["menu"].delete(0, "end")

        new_ports = SerialCore.enum_serial_ports()

        self.select_port["menu"].add_command(label="     ", command=lambda p="     ": self.port_name.set(p))
        for port in new_ports:
            self.select_port["menu"].add_command(label=port, command=lambda p=port: self.port_name.set(p))


    def _open_port(self):
        self.master.add_task(Message(MsgType.OPEN_PORT, self.port_name.get()))

    def open_port_failed(self):
        self.label_2.config(text="打开串口失败")

    def open_port_ok(self):
        self.label_2.config(text="串口已打开")
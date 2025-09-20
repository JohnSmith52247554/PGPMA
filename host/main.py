import threading
import queue
import tkinter as tk
from tkinter import ttk, messagebox

from s_serial import SerialCtrl, MsgType, Message
import widgets
from widgets.console import ImmConsole


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("上位机")
        self.geometry("1080x720")

        self.main_frame = ttk.Frame(self)
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        self.message_queue = queue.Queue()

        self.serial_ctrl = SerialCtrl(self)

        self._create_widgets()

        # 启动内核线程
        self.kernel_thread = threading.Thread(
            target=self.serial_ctrl.run,
            daemon = True)
        self.kernel_thread.start()

        # 启动消息轮询
        self.after(10, self._poll_kernel_message)

    def _create_widgets(self):
        self.command_buttons = widgets.CommandButtons(self)
        self.port_monitor = widgets.PortMonitor(self)
        self.port_select = widgets.PortSelect(self)
        self.console = widgets.console.BlankConsole(self)
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(self, orient=tk.HORIZONTAL, length=100, mode='determinate', variable=self.progress_var)

        self.command_buttons.grid(row=0, column=0, rowspan=7, sticky=tk.N, padx=10, pady=10)
        self.port_select.grid(row=0, column=1, rowspan=3, columnspan=4, sticky=tk.N, padx=10, pady=5)
        self.console.grid(row=3, column=1, rowspan=15, columnspan=10, sticky=tk.NSEW, padx=10, pady=10)
        self.port_monitor.grid(row=0, column=11, rowspan=11, sticky=tk.W, padx=10, pady=10)
        self.progress_bar.grid(row=11, column=11, sticky=tk.EW, padx=10, pady=3)

    def _poll_kernel_message(self):
        try:
            while True:
                msg = self.message_queue.get_nowait()
                #self.port_monitor.add_message(msg)

                if msg.dict["type"] == MsgType.OPEN_PORT:
                    # 处理打开串口的消息
                    if msg.dict["data"] == "OK":
                        self.port_select.open_port_ok()
                    elif msg.dict["data"] == "FAILED":
                        self.port_select.open_port_failed()
                elif msg.dict["type"] == MsgType.ENABLE_PORT_MONITOR:
                    self.serial_ctrl.core.set_enable_monitor(True)
                elif msg.dict["type"] == MsgType.DISABLE_PORT_MONITOR:
                    self.serial_ctrl.core.set_enable_monitor(False)
                elif msg.dict["type"] == MsgType.SET_PROGRESS_BAR:
                    # 处理设置进度条的消息
                    value = msg.dict["data"]
                    self.progress_var.set(value)
                elif msg.dict["type"] == MsgType.CREATE_ERROR_WINDOW:
                    # 处理创建错误窗口的消息
                    tk.messagebox.showerror("错误", "错误：" + msg.dict["data"])
                elif msg.dict["type"] == MsgType.CREATE_INFO_WINDOW:
                    # 处理创建信息窗口的消息
                    tk.messagebox.showinfo("信息", msg.dict["data"])
                elif msg.dict["type"] == MsgType.SET_IMM_CONSOLE_TEXT:
                    if type(self.console) == ImmConsole:
                        self.console.set_text(msg.dict["data"])

        except queue.Empty:
            pass
        finally:
            self.after(10, self._poll_kernel_message)

    def add_message(self, msg : Message):
        self.message_queue.put(msg)

    def add_task(self, task : Message):
        self.serial_ctrl.add_task(task)

    def add_port_monitor_message(self, msg : str):
        self.port_monitor.add_message(msg)

    def set_console(self, console : str):
        if console == "ImmConsole":
            self.console.destroy()
            self.console = widgets.console.ImmConsole(self)
            self.console.grid(row=3, column=1, rowspan=10, columnspan=10, sticky=tk.N, padx=10, pady=10)
        elif console == 'RWFlashConsole':
            self.console.destroy()
            self.console = widgets.console.RWFlashConsole(self)
            self.console.grid(row=3, column=1, rowspan=10, columnspan=10, sticky=tk.N, padx=10, pady=10)
        elif console == 'ProgramConsole':
            self.console.destroy()
            self.console = widgets.console.ProgramConsole(self)
            self.console.grid(row=3, column=1, rowspan=10, columnspan=10, sticky=tk.N, padx=10, pady=10)
        elif console == 'VisualConsole':
            self.console.destroy()
            self.console = widgets.console.VisualConsole(self)
            self.console.grid(row=3, column=1, rowspan=10, columnspan=10, sticky=tk.N, padx=10, pady=10)


def main():
    app = Application()
    app.mainloop()

if __name__ == '__main__':
    main()

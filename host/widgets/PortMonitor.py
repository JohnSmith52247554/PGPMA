import tkinter as tk
from datetime import datetime
from s_serial import Message, MsgType

class PortMonitor(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        self.enable_monitoring = True

        self.label = tk.Label(self, text="串口监控器")
        self.btn_enable = tk.Button(self, text="禁用串口监视器", command=self._set_monitoring)
        self.should_show_timestamp = True
        self.btn_cleanup = tk.Button(self, text="清屏", command=self.cleanup)
        self.btn_show_timestamp = tk.Button(self, text="显示时间戳", command=self.show_timestamp)
        self.text = tk.Text(self, height=40, width=40)
        self.text.config(state='disabled')

        self.label.grid(row=0, column=0, rowspan=2, columnspan=2, sticky=tk.NSEW)
        self.btn_enable.grid(row=2, column=0, columnspan=2, sticky=tk.NSEW)
        self.btn_cleanup.grid(row=3, column=0,  sticky=tk.EW)
        self.btn_show_timestamp.grid(row=3, column=1, sticky=tk.EW)
        self.text.grid(row=4, column=0, rowspan=16, columnspan=2, sticky=tk.NSEW)

    def cleanup(self):
        self.text.config(state='normal')
        self.text.delete("1.0", tk.END)
        self.text.config(state='disabled')

    def show_timestamp(self):
        self.should_show_timestamp = not self.should_show_timestamp

    def add_message(self, message : str):
        self.text.config(state='normal')
        if self.should_show_timestamp:
            message = f"[{datetime.now().strftime('%H:%M:%S.%f')[:-4]}] {message}"

        line_count = int(self.text.index('end-1c').split('.')[0])
        max_lines = 100
        if line_count > max_lines:
            self.text.delete("1.0", f'{line_count - max_lines + 1}.0')

        self.text.insert(tk.END, message + "\n")
        self.text.see(tk.END)
        self.text.config(state='disabled')

    def _set_monitoring(self):
        if self.enable_monitoring:
            self.btn_enable.config(text="启用串口监视器")
            self.enable_monitoring = False
            self.master.add_message(Message(MsgType.DISABLE_PORT_MONITOR))
        else:
            self.btn_enable.config(text="禁用串口监视器")
            self.enable_monitoring = True
            self.master.add_message(Message(MsgType.ENABLE_PORT_MONITOR))
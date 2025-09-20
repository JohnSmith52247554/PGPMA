import tkinter as tk
from .console import *

class CommandButtons(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        self.label1 = tk.Label(self, text="选择功能模式")
        self.label1.grid(row=0, column=0, sticky="nsew")

        self.label2 = tk.Label(self, text="当前模式：")
        self.label2.grid(row=1, column=0, sticky="nsew")

        btn_name_list = ["实时控制模式", "视觉识别模式", "编程模式", "读写Flash"]
        self.current_mode_str = tk.StringVar(value='请选择功能')
        self.label3 = tk.Label(self, text=self.current_mode_str.get())
        self.label3.grid(row=2, column=0, sticky="nsew")

        btn_command_list = [self._immediate_control_mode, self._visual_recognition_mode, self._programming_mode, self._read_write_flash]
        self.button_list = []
        for i in range(len(btn_command_list)):
            button = tk.Button(self, text=btn_name_list[i], command=btn_command_list[i])
            button.grid(row=i + 3, column=0, columnspan=2, sticky=tk.EW)

    def _immediate_control_mode(self):
        self.label3.config(text='实时控制模式')
        self.master.set_console('ImmConsole')

    def _visual_recognition_mode(self):
        self.label3.config(text='视觉识别模式')
        self.master.set_console('VisualConsole')

    def _programming_mode(self):
        self.label3.config(text='编程模式')
        self.master.set_console('ProgramConsole')

    def _read_write_flash(self):
        self.label3.config(text='读写Flash')
        self.master.set_console('RWFlashConsole')
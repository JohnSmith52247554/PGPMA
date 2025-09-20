from .AbstractConsole import AbstractConsole

import tkinter as tk

class BlankConsole(AbstractConsole):
    def __init__(self, master):
        super().__init__(master)

        self.label = tk.Label(self, text="请在左侧选择功能", font=("Arial", 16))

        self.label.grid(row=0, column=0, rowspan=10, columnspan=10)
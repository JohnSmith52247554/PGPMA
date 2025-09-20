from .AbstractConsole import AbstractConsole
from compiler import ASCC
from s_serial import Message, MsgType

import tkinter as tk
from tkinter import filedialog
import threading
import os


class ProgramConsole(AbstractConsole):
    def __init__(self, master):
        super().__init__(master)

        self.compiler = ASCC(self)
        self.ascc_thread : threading.Thread | None = None
        self.compile_success = False

        self.label_1 = tk.Label(self, text="编译 ArmScript 源文件")
        self.var_src_path = tk.StringVar()
        self.var_src_path.set("未选择文件")
        self.btn_choose_src = tk.Button(self, text="打开 ArmScript 源文件", command=self._choose_src_file)
        self.label_src_path = tk.Label(self, textvariable=self.var_src_path)
        self.btn_compile_only = tk.Button(self, text="编译", command=self._compile_src)
        self.btn_compile_and_download = tk.Button(self, text="编译并烧录", command=self._compile_and_download)

        self.label_2 = tk.Label(self, text="烧录字节码")
        self.var_byte_path = tk.StringVar()
        self.var_byte_path.set("未选择文件")
        self.btn_choose_byte = tk.Button(self, text="打开字节码文件", command=self._choose_byte_file)
        self.label_byte_path = tk.Label(self, textvariable=self.var_byte_path)
        self.btn_download = tk.Button(self, text="烧录", command=self._download_byte)

        self.text = tk.Text(self, width=50, height=20)
        self.text.config(state='disabled')

        self.label_1.grid(row=0, columnspan=2, padx=5, pady=5, sticky=tk.EW)
        self.btn_choose_src.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=tk.EW)
        self.label_src_path.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=tk.EW)
        self.btn_compile_only.grid(row=3, column=0, padx=5, pady=2, sticky=tk.EW)
        self.btn_compile_and_download.grid(row=3, column=1, padx=2, pady=5, sticky=tk.EW)

        self.label_2.grid(row=4, columnspan=2, padx=5, pady=5, sticky=tk.EW)
        self.btn_choose_byte.grid(row=5, column=0, columnspan=2, padx=5, pady=2, sticky=tk.EW)
        self.label_byte_path.grid(row=6, column=0, columnspan=2, padx=5, pady=2, sticky=tk.EW)
        self.btn_download.grid(row=7, column=0, columnspan=2, padx=5, pady=2, sticky=tk.EW)

        self.text.grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky=tk.NSEW)

    def _choose_src_file(self):
        self.var_src_path.set(tk.filedialog.askopenfilename(title="选择 ArmScript 源文件", filetypes=[("ArmScript", "*.as")]))

    def _choose_byte_file(self):
        self.var_byte_path.set(tk.filedialog.askopenfilename(title="选择字节码文件", filetypes=[("字节码", "*.byte")]))

    def _compile_src(self):
        path = self.var_src_path.get()
        if self.ascc_thread is None or not self.ascc_thread.is_alive():
            self.ascc_thread = threading.Thread(
                target=self.compiler.ascc_compile,
                args=(path,)
            )
        self.ascc_thread.start()

    def _compile_and_download(self):
        path = self.var_src_path.get()
        if self.ascc_thread is None or not self.ascc_thread.is_alive():
            self.ascc_thread = threading.Thread(
                target=self.compiler.ascc_compile_and_download,
                args=(path,)
            )
        self.ascc_thread.start()

    def _download_byte(self):
        byte_path = self.var_byte_path.get()
        data = {
            "file_path" : byte_path,
            "address" : 0x01FF3000
        }
        self.master.add_task(Message(MsgType.WRITE_FLASH, data))


    def add_text(self, text : str):
        self.text.config(state='normal')
        line_count = int(self.text.index('end-1c').split('.')[0])
        max_lines = 100
        if line_count > max_lines:
            self.text.delete("1.0", f'{line_count - max_lines + 1}.0')
        self.text.insert(tk.END, text + "\n")
        self.text.see(tk.END)
        self.text.config(state='disabled')
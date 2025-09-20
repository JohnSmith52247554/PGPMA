from .AbstractConsole import AbstractConsole
from s_serial import MsgType, Message
import tkinter as tk
from tkinter import filedialog, messagebox

class RWFlashConsole(AbstractConsole):
    def __init__(self, master):
        super().__init__(master)

        self.btn_clean_flash = tk.Button(self, text="全片擦除", command=self._clean_flash)

        self.label_write_flash = tk.Label(self, text="写入Flash")
        self.btn_open_write_file = tk.Button(self, text="打开写入文件", command=self._open_write_file)
        self.label_write_file = tk.Label(self, text="文件路径: ")
        self.write_file_path = tk.StringVar()
        self.write_file_path.set("请选择写入文件")
        self.label_write_file_path = tk.Label(self, textvariable=self.write_file_path)
        self.label_write_address = tk.Label(self, text="写入地址(bytes): 0x")
        self.write_address = tk.StringVar()
        self.write_address.set("00000000")
        self.entry_write_address = tk.Entry(self, textvariable=self.write_address)
        self.entry_write_address.bind("<KeyRelease>", lambda event: self._check_write_file_address(event, self.entry_write_address))
        self.label_caution = tk.Label(self, text="写入地址需要与4096bytes对齐")
        self.label_caution_2 = tk.Label(self, text="写入地址最大为0x0200 0000(32MB)")
        self.btn_write_flash = tk.Button(self, text="写入Flash", command=self._write_flash)

        self.label_read_flash = tk.Label(self, text="读取Flash")
        self.btn_open_save_path = tk.Button(self, text="选择保存路径", command=self._open_save_path)
        self.save_path = tk.StringVar()
        self.save_path.set("请选择保存路径")
        self.label_save_read_flash = tk.Label(self, text="保存路径:")
        self.label_save_path = tk.Label(self, textvariable=self.save_path)
        self.label_read_flash_address = tk.Label(self, text="读Flash起始地址(bytes): 0x")
        self.read_flash_address = tk.StringVar()
        self.read_flash_address.set("00000000")
        self.entry_read_flash_address = tk.Entry(self, textvariable=self.read_flash_address)
        self.entry_read_flash_address.bind("<KeyRelease>", lambda event: self._check_read_flash_address(event, self.entry_read_flash_address))
        self.label_read_flash_len = tk.Label(self, text="读Flash长度(bytes): 0x")
        self.read_flash_len = tk.StringVar()
        self.read_flash_len.set("00000000")
        self.entry_read_flash_len = tk.Entry(self, textvariable=self.read_flash_len)
        self.entry_read_flash_len.bind("<KeyRelease>", lambda event: self._check_read_flash_len(event, self.entry_read_flash_len))
        self.label_caution_3 = tk.Label(self, text="读取Flash的长度需要是1024bytes的倍数")
        self.btn_read_flash = tk.Button(self, text="读取Flash", command=self._read_flash)

        self.btn_clean_flash.grid(row=0, column=0, columnspan=2, pady=7, sticky=tk.NSEW)

        self.label_write_flash.grid(row=1, column=0, columnspan=2, pady=7, sticky=tk.NSEW)
        self.btn_open_write_file.grid(row=2, column=0, columnspan=2, pady=2, sticky=tk.NSEW)
        self.label_write_file.grid(row=3, column=0, pady=2)
        self.label_write_file_path.grid(row=3, column=1, pady=2)
        self.label_write_address.grid(row=4, column=0, pady=2)
        self.entry_write_address.grid(row=4, column=1, pady=2)
        self.label_caution.grid(row=5, column=0, columnspan=2, pady=2, sticky=tk.NSEW)
        self.label_caution_2.grid(row=6, column=0, columnspan=2, pady=2, sticky=tk.NSEW)
        self.btn_write_flash.grid(row=7, column=0, columnspan=2, pady=2, sticky=tk.NSEW)

        self.label_read_flash.grid(row=8, column=0, columnspan=2, pady=7, sticky=tk.NSEW)
        self.btn_open_save_path.grid(row=9, column=0, columnspan=2, pady=2, sticky=tk.NSEW)
        self.label_save_read_flash.grid(row=10, column=0, pady=2)
        self.label_save_path.grid(row=10, column=1, pady=2)
        self.label_read_flash_address.grid(row=11, column=0, pady=2)
        self.entry_read_flash_address.grid(row=11, column=1, pady=2)
        self.label_read_flash_len.grid(row=12, column=0, pady=2)
        self.entry_read_flash_len.grid(row=12, column=1, pady=2)
        self.label_caution_3.grid(row=13, column=0, columnspan=2, pady=2, sticky=tk.NSEW)
        self.btn_read_flash.grid(row=14, column=0, columnspan=2, pady=2, sticky=tk.NSEW)

    def _open_write_file(self):
        self.write_file_path.set(tk.filedialog.askopenfilename(title="请选择需要写入的文件", filetypes=[("Binary Files", "*.bin")]))

    def _open_save_path(self):
        file_path = tk.filedialog.asksaveasfilename(title="请选择保存路径", filetypes=[("Binary Files", "*.bin")])
        if file_path and not file_path.endswith('.bin'):
            file_path += ".bin"
        self.save_path.set(file_path)

    @staticmethod
    def is_valid_input_address(str : str, base : int) -> (bool, int):
        try:
            address = int(str, 16)
            if address % base == 0 and 0 <= address <= 0x02000000:
                return True, address
            else:
                return False, 0
        except ValueError:
            return False, 0


    @staticmethod
    def _check_write_file_address(event, entry):
        input_str = entry.get()
        if input_str == "":
            entry.config(bg='white')
            return
        if RWFlashConsole.is_valid_input_address(input_str, 4096)[0]:
            entry.config(bg='white')
        else:
            entry.config(bg='red')

    @staticmethod
    def _check_read_flash_address(event, entry):
        input_str = entry.get()
        if input_str == "":
            entry.config(bg='white')
            return
        if RWFlashConsole.is_valid_input_address(input_str, 1)[0]:
            entry.config(bg='white')
        else:
            entry.config(bg='red')


    @staticmethod
    def _check_read_flash_len(event, entry):
        input_str = entry.get()
        if input_str == "":
            entry.config(bg='white')
            return
        if RWFlashConsole.is_valid_input_address(input_str, 1024)[0]:
            entry.config(bg='white')
        else:
            entry.config(bg='red')

    def _read_flash(self):
        is_valid, address =  RWFlashConsole.is_valid_input_address(self.read_flash_address.get(), 1)
        if not is_valid:
            self.master.add_message(Message(MsgType.CREATE_ERROR_WINDOW, "读Flash起始地址输入错误"))
            return
        is_valid, length =  RWFlashConsole.is_valid_input_address(self.read_flash_len.get(), 1024)
        if not is_valid:
            self.master.add_message(Message(MsgType.CREATE_ERROR_WINDOW, "读Flash长度输入错误"))
            return
        if address + length > 0x02000000:
            self.master.add_message(Message(MsgType.CREATE_ERROR_WINDOW, "读Flash长度超出范围"))
            return
        data = {
            "save_path" : self.save_path.get(),
            "address" : address,
            "length" : length
        }
        self.master.add_task(Message(MsgType.READ_FLASH, data))

    def _write_flash(self):
        is_valid, address =  RWFlashConsole.is_valid_input_address(self.write_address.get(), 256)
        if not is_valid:
            self.master.add_message(Message(MsgType.CREATE_ERROR_WINDOW, "写入地址输入错误"))
            return
        data = {
            "file_path" : self.write_file_path.get(),
            "address" : address
        }
        self.master.add_task(Message(MsgType.WRITE_FLASH, data))

    def _clean_flash(self):
        if tk.messagebox.askokcancel("擦除Flash", "确认要进行全片擦除吗？（这将花费约一分钟）"):
            self.master.add_task(Message(MsgType.CLEAN_FLASH))
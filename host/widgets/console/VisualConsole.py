from visual import set_thread_alive
from .AbstractConsole import AbstractConsole
import cv2
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import tkinter as tk
from PIL import Image, ImageTk

from s_serial import MsgType, Message
from visual import set_loop_flag, visual_detect_2


class MessageChunk(tk.Frame):
    def __init__(self, master):
        self.master = master
        super().__init__(self.master)

        self.text = tk.Text(self.master, width=60, height=7)
        self.text.config(state=tk.DISABLED)

        self.text.grid(row=3, column=0, padx=10, pady=10, sticky=tk.NSEW)

    def add_message(self, message : str):
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, message + "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)


class VisualConsole(AbstractConsole):
    def __init__(self, master):
        super().__init__(master)

        self.visual_detect_thread = None

        self.label_select_cameras = tk.Label(self, text="请选择摄像头:")
        self.var_cameras_index = tk.StringVar()
        self.var_cameras_index.set(' ')
        self.option_select_cameras = tk.OptionMenu(self, self.var_cameras_index, *['0', '1', '2', '3', '4',])
        #self.option_select_cameras.bind("<Button-1>", lambda event: self._refresh_cameras())
        self.btn_start = tk.Button(self, text="开始", command=self._start)
        self.btn_stop = tk.Button(self, text="停止", command=self._stop)

        self.image = Image.open("./NRST.png")
        self.image = self.image.resize((500, 400), Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(self.image)
        self.label_image = tk.Label(self, image=self.photo)
        #self.label_image.image = self.photo

        self.message_chunk = MessageChunk(self)

        self.label_select_cameras.grid(row=0, column=0, pady=2, sticky=tk.NW)
        self.option_select_cameras.grid(row=0, column=1, columnspan=3, pady=2, sticky=tk.E)
        self.label_image.grid(row=1, column=0, columnspan=2, pady=10, sticky=tk.NSEW)
        self.btn_start.grid(row=2, column=0, pady=5, sticky=tk.EW)
        self.btn_stop.grid(row=2, column=1, pady=5, sticky=tk.EW)
        self.message_chunk.grid(row=3, column=0, columnspan=2, pady=2, sticky=tk.S)


    @staticmethod
    def _scan_cameras(max_index=5) -> list:
        available_cameras = []
        lock = threading.Lock()

        def check_camera(index):
            try:
                cap = cv2.VideoCapture(index)
                if cap.isOpened():
                    # 快速检查，不读取帧
                    with lock:
                        available_cameras.append(str(index))
                    cap.release()
                    return index, True
                return index, False
            except:
                return index, False

        # 使用线程池并行检查
        with ThreadPoolExecutor(max_workers=min(max_index, 8)) as executor:
            futures = [executor.submit(check_camera, i) for i in range(max_index)]

            for future in as_completed(futures):
                index, available = future.result()
                status = "✓" if available else "✗"
                print(f"{status} 摄像头索引 {index}: {'可用' if available else '不可用'}")

        return available_cameras

    def _refresh_cameras(self):
        self.label_select_cameras.config(text="正在扫描摄像头...")
        available_cameras =VisualConsole._scan_cameras()
        self.option_select_cameras['menu'].delete(0, 'end')
        for camera in available_cameras:
            self.option_select_cameras['menu'].add_command(label=camera, command=lambda value=camera: self.var_cameras_index.set(value))
        self.label_select_cameras.config(text="请选择摄像头:")

    def _start(self):
        if self.visual_detect_thread is None or not self.visual_detect_thread.is_alive():
            try:
                camera_index = int(self.var_cameras_index.get())
            except ValueError:
                self.master.add_message(Message(MsgType.CREATE_ERROR_WINDOW, "请选择摄像头"))
                return
            set_loop_flag(True)
            self.visual_detect_thread = threading.Thread(target=visual_detect_2, args=(camera_index, self), daemon=True)
            self.visual_detect_thread.start()

    def _stop(self):
        if self.visual_detect_thread is not None:
            #set_thread_alive(False)
            set_loop_flag(False)
            #self.visual_detect_thread.join()
            #self.visual_detect_thread = None

            #self.image = Image.open("./NRST.png")
            #self.image = self.image.resize((500, 400), Image.Resampling.LANCZOS)
            #self.photo = ImageTk.PhotoImage(self.image)
            #self.label_image = tk.Label(self, image=self.photo)
            #self.label_image.image = self.photo

    def set_image(self, image):
        display_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.image = Image.fromarray(display_rgb)
        self.image = self.image.resize((500, 400), Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(self.image)
        self.label_image.config(image=self.photo)

    def add_message(self, message : str):
        self.message_chunk.add_message(message)
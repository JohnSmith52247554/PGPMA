from .AbstractConsole import AbstractConsole
from s_serial import MsgType, Message, OrthogonalCoord, JointCoord

import tkinter as tk

class ImmConsole(AbstractConsole):
    def __init__(self, master):
        super().__init__(master)

        self.label_base_command = tk.Label(self, text="基础指令")
        self.btn_reset = tk.Button(self, text="复位", command=self._reset)
        self.btn_stop = tk.Button(self, text="停止", command=self._stop)
        self.btn_open_gripper = tk.Button(self, text="打开手爪", command=self._open_gripper)
        self.btn_close_gripper = tk.Button(self, text="关闭手爪", command=self._close_gripper)

        self.label_set_speed = tk.Label(self, text="设置最大速度")
        self.label_m1_speed = tk.Label(self, text="M1(%):")
        self.label_m2_speed = tk.Label(self, text="M2(%):")
        self.label_m3_speed = tk.Label(self, text="M3(%):")
        self.label_m4_speed = tk.Label(self, text="M4(%):")
        self.label_s1_speed = tk.Label(self, text="S1(%):")
        self.label_s2_speed = tk.Label(self, text="S2(%):")
        self.var_m1_speed = tk.StringVar()
        self.var_m2_speed = tk.StringVar()
        self.var_m3_speed = tk.StringVar()
        self.var_m4_speed = tk.StringVar()
        self.var_s1_speed = tk.StringVar()
        self.var_s2_speed = tk.StringVar()
        self.var_m1_speed.set("50.0")
        self.var_m2_speed.set("50.0")
        self.var_m3_speed.set("50.0")
        self.var_m4_speed.set("50.0")
        self.var_s1_speed.set("50.0")
        self.var_s2_speed.set("50.0")
        self.entry_m1_speed = tk.Entry(self, textvariable=self.var_m1_speed)
        self.entry_m2_speed = tk.Entry(self, textvariable=self.var_m2_speed)
        self.entry_m3_speed = tk.Entry(self, textvariable=self.var_m3_speed)
        self.entry_m4_speed = tk.Entry(self, textvariable=self.var_m4_speed)
        self.entry_s1_speed = tk.Entry(self, textvariable=self.var_s1_speed)
        self.entry_s2_speed = tk.Entry(self, textvariable=self.var_s2_speed)
        self.btn_set_speed = tk.Button(self, text="设置", command=self._set_speed)
        self.entry_m1_speed.bind("<KeyRelease>", lambda event: self.on_speed_change(event, self.entry_m1_speed))
        self.entry_m2_speed.bind("<KeyRelease>", lambda event: self.on_speed_change(event, self.entry_m2_speed))
        self.entry_m3_speed.bind("<KeyRelease>", lambda event: self.on_speed_change(event, self.entry_m3_speed))
        self.entry_m4_speed.bind("<KeyRelease>", lambda event: self.on_speed_change(event, self.entry_m4_speed))
        self.entry_s1_speed.bind("<KeyRelease>", lambda event: self.on_speed_change(event, self.entry_s1_speed))
        self.entry_s2_speed.bind("<KeyRelease>", lambda event: self.on_speed_change(event, self.entry_s2_speed))

        self.label_orthogonal_control = tk.Label(self, text="正交坐标控制模式")
        self.label_x = tk.Label(self, text="X:")
        self.label_y = tk.Label(self, text="Y:")
        self.label_z = tk.Label(self, text="Z:")
        self.label_alpha = tk.Label(self, text="ALPHA:")
        self.label_s1_orth = tk.Label(self, text="S1:")
        self.label_s2_orth = tk.Label(self, text="S2:")
        #self.label_time = tk.Label(self, text="时间:")
        self.x_var = tk.StringVar()
        self.y_var = tk.StringVar()
        self.z_var = tk.StringVar()
        self.alpha_var = tk.StringVar()
        self.s1_orth_var = tk.StringVar()
        self.s2_orth_var = tk.StringVar()
        self.x_var.set("0")
        self.y_var.set("0")
        self.z_var.set("0")
        self.alpha_var.set("0")
        self.s1_orth_var.set("0")
        self.s2_orth_var.set("0")
        #self.time_var = tk.StringVar()
        self.entry_x = tk.Entry(self, textvariable=self.x_var)
        self.entry_y = tk.Entry(self, textvariable=self.y_var)
        self.entry_z = tk.Entry(self, textvariable=self.z_var)
        self.entry_alpha = tk.Entry(self, textvariable=self.alpha_var)
        self.entry_s1_orth = tk.Entry(self, textvariable=self.s1_orth_var)
        self.entry_s2_orth = tk.Entry(self, textvariable=self.s2_orth_var)
        #self.entry_time = tk.Entry(self, textvariable=self.time_var)
        self.entry_x.bind("<KeyRelease>", lambda event: self.on_entry_change(event, self.entry_x))
        self.entry_y.bind("<KeyRelease>", lambda event: self.on_entry_change(event, self.entry_y))
        self.entry_z.bind("<KeyRelease>", lambda event: self.on_entry_change(event, self.entry_z))
        self.entry_alpha.bind("<KeyRelease>", lambda event: self.on_entry_change(event, self.entry_alpha))
        self.entry_s1_orth.bind("<KeyRelease>", lambda event: self.on_entry_change(event, self.entry_s1_orth))
        self.entry_s2_orth.bind("<KeyRelease>", lambda event: self.on_entry_change(event, self.entry_s2_orth))
        #self.entry_angle.bind("<KeyRelease>", lambda event: self.on_entry_change(event, self.entry_angle))
        #self.entry_time.bind("<KeyRelease>", lambda event: self.on_entry_change(event, self.entry_time))
        self.btn_transmit = tk.Button(self, text="发送", command=self._transmit_orthogonal_control)

        self.label_joint_control = tk.Label(self, text="关节坐标控制模式")
        self.label_m1 = tk.Label(self, text="M1:")
        self.label_m2 = tk.Label(self, text="M2:")
        self.label_m3 = tk.Label(self, text="M3:")
        self.label_m4 = tk.Label(self, text="M4:")
        self.label_s1 = tk.Label(self, text="S1:")
        self.label_s2 = tk.Label(self, text="S2:")
        #self.label_time2 = tk.Label(self, text="时间:")
        self.m1_var = tk.StringVar()
        self.m2_var = tk.StringVar()
        self.m3_var = tk.StringVar()
        self.m4_var = tk.StringVar()
        self.s1_var = tk.StringVar()
        self.s2_var = tk.StringVar()
        self.m1_var.set("0")
        self.m2_var.set("0")
        self.m3_var.set("0")
        self.m4_var.set("0")
        self.s1_var.set("0")
        self.s2_var.set("0")
        #self.time2_var = tk.StringVar()
        self.entry_m1 = tk.Entry(self, textvariable=self.m1_var)
        self.entry_m2 = tk.Entry(self, textvariable=self.m2_var)
        self.entry_m3 = tk.Entry(self, textvariable=self.m3_var)
        self.entry_m4 = tk.Entry(self, textvariable=self.m4_var)
        self.entry_s1 = tk.Entry(self, textvariable=self.s1_var)
        self.entry_s2 = tk.Entry(self, textvariable=self.s2_var)
        #self.entry_time2 = tk.Entry(self, textvariable=self.time2_var)
        self.entry_m1.bind("<KeyRelease>", lambda event: self.on_entry_change(event, self.entry_m1))
        self.entry_m2.bind("<KeyRelease>", lambda event: self.on_entry_change(event, self.entry_m2))
        self.entry_m3.bind("<KeyRelease>", lambda event: self.on_entry_change(event, self.entry_m3))
        self.entry_m4.bind("<KeyRelease>", lambda event: self.on_entry_change(event, self.entry_m4))
        self.entry_s1.bind("<KeyRelease>", lambda event: self.on_entry_change(event, self.entry_s1))
        self.entry_s2.bind("<KeyRelease>", lambda event: self.on_entry_change(event, self.entry_s2))
        #self.entry_time2.bind("<KeyRelease>", lambda event: self.on_entry_change(event, self.entry_time2))
        self.btn_transmit_joint = tk.Button(self, text="发送", command=self._transmit_joint_control)

        self.label_read = tk.Label(self, text="读取当前状态")
        self.btn_read = tk.Button(self, text="读取", command=self._read_state)
        self.text_state = tk.Text(self, width=80, height=6)
        self.text_state.config(state=tk.DISABLED)

        self.label_base_command.grid(row=0, column=0, columnspan=4, sticky=tk.NSEW)
        self.btn_reset.grid(row=1, column=0, pady=2, sticky=tk.NSEW)
        self.btn_stop.grid(row=1, column=1, pady=2, sticky=tk.NSEW)
        self.btn_open_gripper.grid(row=1, column=2, pady=2, sticky=tk.NSEW)
        self.btn_close_gripper.grid(row=1, column=3, pady=2, sticky=tk.NSEW)

        self.label_set_speed.grid(row=2, column=0, columnspan=4, pady=7)
        self.label_m1_speed.grid(row=3, column=0, pady=2, sticky=tk.NSEW)
        self.entry_m1_speed.grid(row=3, column=1, pady=2, sticky=tk.NSEW)
        self.label_m2_speed.grid(row=3, column=2, pady=2, sticky=tk.NSEW)
        self.entry_m2_speed.grid(row=3, column=3, pady=2, sticky=tk.NSEW)
        self.label_m3_speed.grid(row=3, column=4, pady=2, sticky=tk.NSEW)
        self.entry_m3_speed.grid(row=3, column=5, pady=2, sticky=tk.NSEW)
        self.label_m4_speed.grid(row=4, column=0, pady=2, sticky=tk.NSEW)
        self.entry_m4_speed.grid(row=4, column=1, pady=2, sticky=tk.NSEW)
        self.label_s1_speed.grid(row=4, column=2, pady=2, sticky=tk.NSEW)
        self.entry_s1_speed.grid(row=4, column=3, pady=2, sticky=tk.NSEW)
        self.label_s2_speed.grid(row=4, column=4, pady=2, sticky=tk.NSEW)
        self.entry_s2_speed.grid(row=4, column=5, pady=2, sticky=tk.NSEW)
        self.btn_set_speed.grid(row=5, column=0, columnspan=2, pady=2, sticky=tk.NSEW)

        self.label_orthogonal_control.grid(row=6, column=0, columnspan=4, pady=7)
        self.label_x.grid(row=7, column=0, pady=2)
        self.entry_x.grid(row=7, column=1, pady=2)
        self.label_y.grid(row=7, column=2, pady=2)
        self.entry_y.grid(row=7, column=3, pady=2)
        self.label_z.grid(row=7, column=4, pady=2)
        self.entry_z.grid(row=7, column=5, pady=2)
        self.label_alpha.grid(row=8, column=0, pady=2)
        self.entry_alpha.grid(row=8, column=1, pady=2)
        self.label_s1_orth.grid(row=8, column=2, pady=2)
        self.entry_s1_orth.grid(row=8, column=3, pady=2)
        self.label_s2_orth.grid(row=8, column=4, pady=2)
        self.entry_s2_orth.grid(row=8, column=5, pady=2)
        #self.label_angle.grid(row=9, column=0, pady=2)
        #self.entry_angle.grid(row=9, column=1, pady=2)
        #self.label_time.grid(row=5, column=2, pady=2)
        #self.entry_time.grid(row=5, column=3, pady=2)
        self.btn_transmit.grid(row=10, column=0, columnspan=2, pady=2, sticky=tk.NSEW)

        self.label_joint_control.grid(row=11, column=0, columnspan=4, pady=7)
        self.label_m1.grid(row=12, column=0, pady=2)
        self.entry_m1.grid(row=12, column=1, pady=2)
        self.label_m2.grid(row=12, column=2, pady=2)
        self.entry_m2.grid(row=12, column=3, pady=2)
        self.label_m3.grid(row=12, column=4, pady=2)
        self.entry_m3.grid(row=12, column=5, pady=2)
        self.label_m4.grid(row=13, column=0, pady=2)
        self.entry_m4.grid(row=13, column=1, pady=2)
        self.label_s1.grid(row=13, column=2, pady=2)
        self.entry_s1.grid(row=13, column=3, pady=2)
        self.label_s2.grid(row=13, column=4, pady=2)
        self.entry_s2.grid(row=13, column=5, pady=2)
        #self.label_time2.grid(row=10, column=0, pady=2)
        #self.entry_time2.grid(row=10, column=1, pady=2)
        self.btn_transmit_joint.grid(row=14, column=0, columnspan=2, pady=2, sticky=tk.NSEW)

        self.label_read.grid(row=15, column=0, columnspan=4, pady=7)
        self.text_state.grid(row=16, column=0, columnspan=6, pady=2, sticky=tk.EW)
        self.btn_read.grid(row=17, column=0, columnspan=2, pady=2, sticky=tk.NSEW)


    def _reset(self):
        #self.master.add_task(Msg.RESET)
        self.master.add_task(Message(MsgType.RESET))

    def _stop(self):
        #self.master.add_task(Msg.STOP)
        self.master.add_task(Message(MsgType.STOP))

    def _open_gripper(self):
        #self.master.add_task(Msg.OPEN_GRIPPER)
         self.master.add_task(Message(MsgType.OPEN_GRIPPER))

    def _close_gripper(self):
        #self.master.add_task(Msg.CLOSE_GRIPPER)
        self.master.add_task(Message(MsgType.CLOSE_GRIPPER))

    def _transmit_orthogonal_control(self):
        result = self.get_orth_coord()
        if not result["valid"]:
            self.master.add_message(Message(MsgType.CREATE_ERROR_WINDOW, "请输入参数"))
        else:
            self.master.add_task(Message(MsgType.SEND_ORTHOGONAL_CMD, result["coord"]))
        '''
        string_list = [self.x_var.get(), self.y_var.get(), self.z_var.get(), self.rx_var.get(), self.ry_var.get(), self.rz_var.get(), self.angle_var.get(), self.time_var.get()]
        if not ImmConsole.check_num_list(string_list):
            #self.master.add_message(Msg.CREATE_ERROR_WINDOW + "请输入参数")
            self.master.add_message(Message(MsgType.CREATE_ERROR_WINDOW, "请输入参数"))
        else:
            coord = OrthogonalCoord(float(self.x_var.get()), float(self.y_var.get()), float(self.z_var.get()), float(self.rx_var.get()), float(self.ry_var.get()), float(self.rz_var.get()))
            msg = Message(MsgType.ORTHOGONAL_CONTROL)
        '''

    def _transmit_joint_control(self):
        result = self.get_joint_coord()
        if not result["valid"]:
            self.master.add_message(Message(MsgType.CREATE_ERROR_WINDOW, "请输入参数"))
        else:
            self.master.add_task(Message(MsgType.SEND_JOINT_CMD, result["coord"]))

    def _read_state(self):
        self.master.add_task(Message(MsgType.READ_STATE))

    def _set_speed(self):
        result = self.get_speed()
        if result is None:
            self.master.add_message(Message(MsgType.CREATE_ERROR_WINDOW, "请输入速度参数"))
        else:
            self.master.add_task(Message(MsgType.SEND_SET_SPEED_CMD, result))

    @staticmethod
    def on_speed_change(event, entry):
        input_str = entry.get()
        if not ImmConsole.check_speed(input_str):
            entry.config(bg='red')
        else:
            entry.config(bg='white')

    @staticmethod
    def check_speed(input_str) -> bool:
        try:
            speed = float(input_str)
            if speed <= 0 or speed > 100:
                return False
            else:
                return True
        except ValueError:
            return False

    def set_text(self, text : str):
        self.text_state.config(state=tk.NORMAL)
        self.text_state.delete(1.0, tk.END)
        self.text_state.insert(tk.END, text)
        self.text_state.config(state=tk.DISABLED)

    @staticmethod
    def on_entry_change(event, entry):
        input_str = entry.get()
        if input_str == "":
            entry.config(bg='white')
            return
        try:
            float(input_str)
            entry.config(bg='white')
        except ValueError:
            entry.config(bg='red')

    @staticmethod
    def check_num(str : str) -> bool:
        try:
            float(str)
            return True
        except ValueError:
            return False

    @staticmethod
    def check_num_list(str_list : list) -> bool:
        for str in str_list:
            if not ImmConsole.check_num(str):
                return False
        return True

    def get_orth_coord(self) -> dict:
        try:
            x = float(self.x_var.get())
            y = float(self.y_var.get())
            z = float(self.z_var.get())
            alpha = float(self.alpha_var.get())
            s1 = float(self.s1_orth_var.get())
            s2 = float(self.s2_orth_var.get())
            #angle = float(self.angle_var.get())
        except ValueError:
            return {"valid" : False, "coord" : None}
        return {"valid" : True, "coord" : OrthogonalCoord(x, y, z, alpha, s1, s2)}

    def get_joint_coord(self) -> dict:
        try:
            m1 = float(self.m1_var.get())
            m2 = float(self.m2_var.get())
            m3 = float(self.m3_var.get())
            m4 = float(self.m4_var.get())
            s1 = float(self.s1_var.get())
            s2 = float(self.s2_var.get())
        except ValueError:
            return {"valid" : False, "coord" : None}
        return {"valid" : True, "coord" : JointCoord(m1, m2, m3, m4, s1, s2)}

    def get_speed(self) -> dict | None:
        if ImmConsole.check_speed(self.var_m1_speed.get()):
            m1_speed = float(self.var_m1_speed.get())
        else:
            return None
        if ImmConsole.check_speed(self.var_m2_speed.get()):
            m2_speed = float(self.var_m2_speed.get())
        else:
            return None
        if ImmConsole.check_speed(self.var_m3_speed.get()):
            m3_speed = float(self.var_m3_speed.get())
        else:
            return None
        if ImmConsole.check_speed(self.var_m4_speed.get()):
            m4_speed = float(self.var_m4_speed.get())
        else:
            return None
        if ImmConsole.check_speed(self.var_s1_speed.get()):
            s1_speed = float(self.var_s1_speed.get())
        else:
            return None
        if ImmConsole.check_speed(self.var_s2_speed.get()):
            s2_speed = float(self.var_s2_speed.get())
        else:
            return None
        return {"m1_speed" : m1_speed, "m2_speed" : m2_speed, "m3_speed" : m3_speed,
                "m4_speed" : m4_speed, "s1_speed" : s1_speed, "s2_speed" : s2_speed}
import enum
import struct

class OpCode(enum.Enum):
    NOP = 0x00
    HALT = 0x01
    JMP = 0x02
    JZ = 0x03
    JNZ = 0x04
    CALL = 0x05
    ENTER = 0x06
    RET = 0x07
    RET0 = 0x08

    LOADK = 0x11
    LOADG = 0x12
    LOADL = 0x13
    IMMI = 0x14
    IMMF = 0x15
    POP = 0x16
    STORL = 0x17
    STORG = 0x18

    IADD = 0x21
    ISUB = 0x22
    IMUL = 0x23
    IDIV = 0x24
    IMOD = 0x25
    INEG = 0x26
    FADD = 0x31
    FSUB = 0x32
    FMUL = 0x33
    FDIV = 0x34
    FNEG = 0x35
    LNOT = 0x41
    LAND = 0x42
    LOR = 0x43
    BAND = 0x51
    BOR = 0x52
    BXOR = 0x53
    BNOT = 0x54
    SHL = 0x55
    SHR = 0x56
    IEQ = 0x61
    INE = 0x62
    IGT = 0x63
    ILT = 0x64
    IGE = 0x65
    ILE = 0x66
    FEQ = 0x71
    FNE = 0x72
    FGT = 0x73
    FLT = 0x74
    FGE = 0x75
    FLE = 0x76
    I2F = 0x81
    F2I = 0x82

    DELAY = 0x91
    RST = 0x92
    WAIT = 0x93
    WAITJ = 0x94
    MOVJ = 0x95
    SETJ = 0x96
    READJ = 0x97
    MOVOC = 0x98
    SETOC = 0x99
    MOVJC = 0x9A
    SETJC = 0x9B
    GRIPPER_OPEN = 0x9C
    GRIPPER_CLOSE = 0x9D
    SETJSPD = 0x9E
    OLEDI = 0xA1

    PRINT = 0xB1    # 调试用

    LABEL = 0xFF    # 标签，仅在汇编阶段使用，不参与机器码生成

class Operant:
    def __str__(self):
        pass

    def to_assembly_bytes(self) -> list:
        pass

class U8(Operant):
    def __init__(self, val : int):
        self.val = val

    def __str__(self):
        return f"{self.val}"

    def to_assembly_bytes(self) -> list:
        # 小端序一字节
        return [self.val & 0xFF]

class U16(Operant):
    def __init__(self, val : int):
        self.val = val

    def __str__(self):
        return f"{self.val}"

    def to_assembly_bytes(self) -> list:
        # 小端序两字节
        return [self.val & 0xFF, (self.val >> 8) & 0xFF]

class U32(Operant):
    def __init__(self, val : int):
        self.val = val

    def __str__(self):
        return f"{self.val}"

    def to_assembly_bytes(self) -> list:
        # 小端序四字节
        return [self.val & 0xFF, (self.val >> 8) & 0xFF, (self.val >> 16) & 0xFF, (self.val >> 24) & 0xFF]

class F32(Operant):
    def __init__(self, val : float):
        self.val = val

    def __str__(self):
        return f"{self.val}"

    def to_assembly_bytes(self) -> list:
        # 小端序四字节
        return list(struct.pack('<f', self.val))

class Label(Operant):
    def __init__(self, name : str):
        self.name = name
        self.addr = None

    def __str__(self):
        return self.name

    def to_assembly_bytes(self) -> list:
        # 小端序两字节
        if self.addr is None:
            raise ValueError("Label address is not set")
        return [self.addr & 0xFF, (self.addr >> 8) & 0xFF]

class Instruction:
    def __init__(self, op_code, *args : Operant):
        self.op_code = op_code
        self.args = args

    def __str__(self):
        return f"{self.op_code.name} {' '.join(map(str, self.args))}"

    def to_assembly_bytes(self) -> list:
        byte = [self.op_code.value]
        for arg in self.args:
            byte += arg.to_assembly_bytes()
        return byte

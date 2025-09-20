from .assemblier import AssemblyCode, LabelTable
from .instruction import *
import struct
import hashlib

class CodeGenerator:
    def __init__(self):
        self.label_callback = {}

    def gen(self, assembly : AssemblyCode, label_table : LabelTable) -> list:
        bytecode = [0xFF, 0xFF, 0xFF, 0xFF] # 32位文件总大小，待填充

        # 16位常量区大小
        constant_size = assembly.get_constant_size()
        bytecode.extend([constant_size & 0xFF, (constant_size >> 8) & 0xFF])

        # 写入常量
        for constant in assembly.constants:
            if isinstance(constant, int):
                # 32位整数常量
                bytecode.extend([constant & 0xFF, (constant >> 8) & 0xFF, (constant >> 16) & 0xFF, (constant >> 24) & 0xFF])
            elif isinstance(constant.value, float):
                # 32位浮点数常量
                bytecode.extend(list(struct.pack('<f', constant)))

        # 写入全局变量区大小
        global_size = assembly.global_size
        bytecode.extend([global_size & 0xFF, (global_size >> 8) & 0xFF])

        code_begin_addr = len(bytecode)

        # 写入代码
        for code in assembly.start_up:
            self._fill_code(code, bytecode, label_table, code_begin_addr)
        for code in assembly.code:
            self._fill_code(code, bytecode, label_table, code_begin_addr)

        # 设置大小
        code_size = len(bytecode) + 16 # 加上末尾的16字节MD5校验码
        bytecode[0] = code_size & 0xFF
        bytecode[1] = (code_size >> 8) & 0xFF
        bytecode[2] = (code_size >> 16) & 0xFF
        bytecode[3] = (code_size >> 24) & 0xFF

        # 计算MD5校验码
        md5 = hashlib.md5()
        md5.update(bytearray(bytecode))
        md5_code = md5.digest()

        bytecode.extend(list(md5_code))

        return bytecode

    def _fill_code(self, instruction : Instruction, bytecode : list , label_table : LabelTable, code_begin_addr : int):
        if instruction.op_code == OpCode.LABEL:
            # 处理标签
            label = instruction.args[0]
            if isinstance(label, Label):
                label_name = label.name
                # 设置偏移量
                offset = len(bytecode) - code_begin_addr
                label_table.set_label_offset(label_name, offset)
                # 处理回调
                label_todo_list = self.label_callback.get(label_name)
                if label_todo_list is not None and len(label_todo_list) > 0:
                    for todo in label_todo_list:
                        bytecode[todo] = offset & 0xFF
                        bytecode[todo+1] = (offset >> 8) & 0xFF
            else:
                raise RuntimeError("Invalid label type")
        elif instruction.op_code in (OpCode.JMP, OpCode.JZ, OpCode.JNZ, OpCode.CALL):
            # 将标签替换为偏移量
            label = instruction.args[0]
            if isinstance(label, Label):
                label_name = label.name
                offset = label_table.get_label_offset(label_name)
                if offset is not None and offset >= 0:
                    # 偏移量已设置，进行替换
                    label.addr = offset
                else:
                    # 偏移量未设置，添加回调
                    if label_name not in self.label_callback:
                        self.label_callback[label_name] = [len(bytecode) + 1]
                    else:
                        self.label_callback[label_name].append(len(bytecode) + 1)
                    # 占位符，待填充
                    label.addr = 0xFFFF
                bytecode.extend(instruction.to_assembly_bytes())

            else:
                raise RuntimeError("Invalid label type")

        else:
            bytecode.extend(instruction.to_assembly_bytes())

from .lexer import tokenize
from .parser import Parser, SemanticAnalyzer
from .assemblier import Assembler
from .codegen import CodeGenerator

from widgets.console import ProgramConsole

import json
import os

class ASCC:
    def __init__(self, master : ProgramConsole):
        self.master = master

    def ascc_compile(self, file_path : str):
        self.master.compile_success = False

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
        except FileNotFoundError:
            self.master.add_text("Error: File not found.")
            return

        try:
            project_name = os.path.splitext(os.path.basename(file_path))[0]

            self.master.add_text("Start compiling...")
            self.master.add_text("Tokenizing...")
            tokens = tokenize(code)

            self.master.add_text("Parsing...")
            parser = Parser(tokens)
            ast = parser.parse()
            analyzer = SemanticAnalyzer(parser.symbol_table)
            analyzer.examine(ast)

            for info in analyzer.info_box:
                self.master.add_text(info)

            # 创建build目录
            dir_path = os.path.dirname(file_path)  # 获取文件所在目录
            build_dir = os.path.join(dir_path, "build")
            os.makedirs(build_dir, exist_ok=True)

            # 保存AST
            ast_file_path = os.path.join(build_dir, "ast.json")
            with open(ast_file_path, 'w') as f:
                f.write(json.dumps(ast.json(), indent=4))

            self.master.add_text("Assembling...")
            assembler = Assembler()
            assembly, debug_info, label_table = assembler.assemble(ast, parser.symbol_table)

            # 保存汇编代码
            assembly_file_path = os.path.join(build_dir, project_name + ".asm")
            with open(assembly_file_path, 'w') as f:
                f.write(assembly.__str__())

            # 保存调试信息
            debug_info_file_path = os.path.join(build_dir, "debug_info.json")
            with open(debug_info_file_path, 'w') as f:
                f.write(json.dumps(debug_info, indent=4))

            self.master.add_text("Generating bytecode...")
            codegen = CodeGenerator()
            bytecode = codegen.gen(assembly, label_table)

            # 保存字节码
            bytecode_file_path = os.path.join(build_dir, project_name + ".byte")
            with open(bytecode_file_path, 'wb') as f:
                f.write(bytes(bytecode))

            flash_occupied = len(bytecode)
            constant_occupied = len(debug_info['constants']) * 4
            global_occupied = len(debug_info['globals']) * 4
            stack_occupied = 4096
            program_occupied = flash_occupied - (4 + 2 + 2 + 16 + constant_occupied)

            u16max = 2**16
            if program_occupied > u16max:
                raise RuntimeError("Program occupied " + str(program_occupied) + " bytes, max 65536 bytes.")
            if constant_occupied > u16max:
                raise RuntimeError("Constant occupied " + str(constant_occupied) + " bytes, max 65536 bytes.")
            if global_occupied > u16max:
                raise RuntimeError("Global occupied " + str(global_occupied) + " bytes, max 65536 bytes.")

            self.master.add_text("Flash occupied: " + str(flash_occupied) + " bytes")
            self.master.add_text("Memory occupied: " + str(constant_occupied + global_occupied + stack_occupied + program_occupied) + " bytes")
            self.master.add_text("-program: " + str(program_occupied) + " bytes")
            self.master.add_text("-constant: " + str(constant_occupied) + " bytes")
            self.master.add_text("-global: " + str(global_occupied) + " bytes")
            self.master.add_text("-stack: " + str(stack_occupied) + " bytes")

            self.master.add_text("Compile success!\n\n")

            self.master.compile_success = True

        except Exception as e:
            self.master.add_text("Error: " + str(e))

    def ascc_compile_and_download(self, file_path : str):
        self.ascc_compile(file_path)
        if self.master.compile_success:
            src_path = self.master.var_src_path.get()
            project_name = os.path.splitext(os.path.basename(src_path))[0]
            self.master.var_byte_path.set(os.path.join(os.path.dirname(src_path), "build/" + project_name + ".byte"))
            self.master._download_byte()

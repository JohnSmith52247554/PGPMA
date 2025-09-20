from .ast_node import *
from .parser import SymbolTable, get_expr_type
from .instruction import *

class AssemblyCode:
    def __init__(self):
        self.constants = []
        self.global_size = 0
        self.start_up = []
        self.code = []

    def get_constant_size(self) -> int:
        return self.constants.__len__()

    def __str__(self) -> str:
        gen_str = "CONSTANTS:\n"
        for const in self.constants:
            gen_str += "\t" + str(const) + "\n"
        gen_str += "GLOBAL_VAR_NUM: " + str(self.global_size) + "\n"
        gen_str += "CODE:\n"
        for inst in self.start_up:
            gen_str += "\t" + str(inst) + "\n"
        for inst in self.code:
            gen_str += "\t" + str(inst) + "\n"

        return gen_str

class LabelTable:
    def __init__(self):
        self.labels = {}
        self.label_counter = 0

    def create_label(self, label : str):
        self.labels[label] = -1
        self.label_counter += 1

    def get_label_offset(self, label : str) -> int:
        if label in self.labels:
            return self.labels[label]
        else:
            return -1

    def set_label_offset(self, label : str, offset : int):
        if label in self.labels:
            self.labels[label] = offset
        else:
            raise RuntimeError("Undefined label: " + label)


class Assembler:
    def __init__(self):
        self.assembly_code = AssemblyCode()
        self.debug_info = {
            "constants": {},
            "globals": {},
            "functions": {},
        }
        self.label_table = LabelTable()

    def assemble(self, ast : Program, symbol_table : SymbolTable) -> (AssemblyCode, dict, LabelTable):
        for decl in ast.global_decls:
            if isinstance(decl, FuncDecl):
                self._gen_func(decl, symbol_table)
            elif isinstance(decl, VarDecl):
                self._gen_global_var(decl, symbol_table)

        self.assembly_code.start_up.append(Instruction(OpCode.CALL, Label("main"), U8(0)))
        self.assembly_code.start_up.append(Instruction(OpCode.HALT))

        return self.assembly_code, self.debug_info, self.label_table

    def _gen_func(self, func_decl : FuncDecl, symbol_table : SymbolTable):
        self.debug_info["functions"][func_decl.name] = {
            "return_type" : func_decl.return_type.name,
            "local_var_num" : func_decl.local_var_num,
            "local_var": {},
            "param_num" : func_decl.params.__len__(),
            "offset" : None
        }
        self.assembly_code.code.append(Instruction(OpCode.LABEL, Label(func_decl.name)))
        self.label_table.create_label(func_decl.name)
        self.assembly_code.code.append(Instruction(OpCode.ENTER, U8(func_decl.local_var_num)))

        symbol_table.enter_scope()
        i = 0
        for param in func_decl.params:
            symbol_table.decl_local(param.var_name, {
                "type" : param.var_type,
                "is_const" : False,
                "offset" : i,
            })
            self.debug_info["functions"][func_decl.name]["local_var"][param.var_name] = {
                "type" : param.var_type.name,
                "offset" : i,
            }
            i += 1

        self._gen_stmts(func_decl.body, symbol_table, func_decl.name)
        symbol_table.exit_scope()

        if func_decl.return_type == VarType.VOID and self.assembly_code.code[-1].op_code!= OpCode.RET0:
            self.assembly_code.code.append(Instruction(OpCode.RET0))

    def _gen_stmts(self, stmts : List[Node], symbol_table : SymbolTable, func_name : str, break_jmp_label_name : str | None = None):
        #symbol_table.enter_scope()
        for stmt in stmts:
            if isinstance(stmt, IfStmt):
                self._gen_if_stmt(stmt, symbol_table, func_name)
            elif isinstance(stmt, WhileStmt):
                self._gen_while_stmt(stmt, symbol_table, func_name)
            elif isinstance(stmt, LoopStmt):
                self._gen_loop_stmt(stmt, symbol_table, func_name)
            elif isinstance(stmt, ReturnStmt):
                self._gen_return_stmt(stmt, symbol_table)
            elif isinstance(stmt, VarDecl):
                self._gen_local_var(stmt, symbol_table, func_name)
            elif isinstance(stmt, Expr):
                self.assembly_code.code.extend(self._gen_expr(stmt, symbol_table, require_result=False))
            elif isinstance(stmt, BreakStmt) and break_jmp_label_name is not None:
                self._gen_break_stmt(break_jmp_label_name)
            else:
                raise RuntimeError("Unsupported statement type: " + str(type(stmt)))
        #symbol_table.exit_scope()

    def _gen_if_stmt(self, if_stmt : IfStmt, symbol_table : SymbolTable, func_name : str):
        self.assembly_code.code.extend(self._gen_expr(if_stmt.cond_expr, symbol_table, require_result=True))
        else_label_name = str(self.label_table.label_counter) + "_if_else"
        self.label_table.create_label(else_label_name)
        end_label_name = str(self.label_table.label_counter) + "_if_end"
        self.label_table.create_label(end_label_name)

        self.assembly_code.code.append(Instruction(OpCode.JZ, Label(else_label_name)))

        symbol_table.enter_scope()
        self._gen_stmts(if_stmt.then_stmt, symbol_table, func_name)
        symbol_table.exit_scope()

        self.assembly_code.code.append(Instruction(OpCode.JMP, Label(end_label_name)))

        self.assembly_code.code.append(Instruction(OpCode.LABEL, Label(else_label_name)))
        if if_stmt.else_stmt is not None:
            symbol_table.enter_scope()
            self._gen_stmts(if_stmt.else_stmt, symbol_table, func_name)
            symbol_table.exit_scope()

        self.assembly_code.code.append(Instruction(OpCode.LABEL, Label(end_label_name)))

    def _gen_while_stmt(self, while_stmt : WhileStmt, symbol_table : SymbolTable, func_name : str):
        while_end_label_name = str(self.label_table.label_counter) + "_while_end"
        self.label_table.create_label(while_end_label_name)
        while_begin_label_name = str(self.label_table.label_counter) + "_while_begin"
        self.label_table.create_label(while_begin_label_name)

        self.assembly_code.code.append(Instruction(OpCode.LABEL, Label(while_begin_label_name)))
        self.assembly_code.code.extend(self._gen_expr(while_stmt.cond_expr, symbol_table, require_result=True))
        self.assembly_code.code.append(Instruction(OpCode.JZ, Label(while_end_label_name)))

        symbol_table.enter_scope()
        self._gen_stmts(while_stmt.body, symbol_table, func_name, break_jmp_label_name=while_end_label_name)
        symbol_table.exit_scope()

        self.assembly_code.code.append(Instruction(OpCode.JMP, Label(while_begin_label_name)))
        self.assembly_code.code.append(Instruction(OpCode.LABEL, Label(while_end_label_name)))

    def _gen_loop_stmt(self, loop_stmt : LoopStmt, symbol_table : SymbolTable, func_name : str):
        loop_begin_label_name = str(self.label_table.label_counter) + "_loop_begin"
        self.label_table.create_label(loop_begin_label_name)
        loop_end_label_name = str(self.label_table.label_counter) + "_loop_end"
        self.label_table.create_label(loop_end_label_name)
        self.assembly_code.code.append(Instruction(OpCode.LABEL, Label(loop_begin_label_name)))

        symbol_table.enter_scope()
        self._gen_stmts(loop_stmt.body, symbol_table, func_name, break_jmp_label_name=loop_end_label_name)
        symbol_table.exit_scope()

        self.assembly_code.code.append(Instruction(OpCode.JMP, Label(loop_begin_label_name)))
        self.assembly_code.code.append(Instruction(OpCode.LABEL, Label(loop_end_label_name)))

    def _gen_return_stmt(self, return_stmt : ReturnStmt, symbol_table : SymbolTable):
        if return_stmt.expr is not None:
            self.assembly_code.code.extend(self._gen_expr(return_stmt.expr, symbol_table, require_result=True))
            self.assembly_code.code.append(Instruction(OpCode.RET))
        else:
            self.assembly_code.code.append(Instruction(OpCode.RET0))

    def _gen_break_stmt(self, break_jmp_label_name : str):
        self.assembly_code.code.append(Instruction(OpCode.JMP, Label(break_jmp_label_name)))

    def _gen_local_var(self, var_decl : VarDecl, symbol_table : SymbolTable, func_name : str):
        if var_decl.is_const:
            self._gen_constant(var_decl, symbol_table)
        else:
            offset = self.debug_info["functions"][func_name]["local_var"].__len__()
            self.debug_info["functions"][func_name]["local_var"][var_decl.var_name] = {
                "type" : var_decl.var_type.name,
                "offset" : offset
            }
            symbol_table.decl_local(var_decl.var_name, {
                "type" : "var",
                "var_type" : var_decl.var_type,
                "is_const" : var_decl.is_const,
                "offset" : offset
            })

            if var_decl.init_expr is not None:
                self.assembly_code.code.extend(self._gen_expr(var_decl.init_expr, symbol_table, require_result=True))
                self.assembly_code.code.append(Instruction(OpCode.STORL, U8(offset)))

    def _gen_global_var(self, var_decl : VarDecl, symbol_table : SymbolTable):
        if var_decl.is_const:
            self._gen_constant(var_decl, symbol_table)
        else:
            offset = self.assembly_code.global_size
            self.debug_info["globals"][var_decl.var_name] = {
                "type" : var_decl.var_type.name,
                "offset" : offset
            }
            sym = symbol_table.lookup(var_decl.var_name)
            if sym is not None:
                sym["offset"] = offset
            else:
                raise RuntimeError("Undefined variable: " + var_decl.var_name)
            self.assembly_code.global_size += 1
            if var_decl.init_expr is not None:
                self._gen_global_init(init_expr=var_decl.init_expr, offset=offset, symbol_table=symbol_table)

    def _gen_constant(self, var_decl : VarDecl, symbol_table : SymbolTable):
        if var_decl.init_expr is not None and isinstance(var_decl.init_expr, LiteralExpr):
            init_val = var_decl.init_expr.value
            offset = self.assembly_code.get_constant_size()
            self.debug_info["constants"][var_decl.var_name] = {
                "type" : var_decl.var_type.name,
                "value" : init_val,
                "offset" : offset
            }
            sym = symbol_table.lookup(var_decl.var_name)
            if sym is not None:
                sym["offset"] = offset
            else:
                raise RuntimeError("Undefined variable: " + var_decl.var_name)
            self.assembly_code.constants.append(init_val)
        else:
            raise RuntimeError("Constant variable must be initialized with a literal value")

    def _gen_global_init(self, init_expr : Expr, offset : int, symbol_table : SymbolTable):
        self.assembly_code.start_up.extend(self._gen_expr(init_expr, symbol_table, require_result=True))
        self.assembly_code.start_up.append(Instruction(OpCode.STORG, U16(offset)))

    def _gen_expr(self, expr : Expr, symbol_table : SymbolTable, require_result : bool = True) -> List[Instruction]:
        instructions = []
        if isinstance(expr, UnaryExpr):
            if expr.op == KeywordType.MINUS:
                instructions.extend(self._gen_expr(expr.operand, symbol_table))
                if get_expr_type(expr.operand, symbol_table) == VarType.INT:
                    instructions.append(Instruction(OpCode.INEG))
                    #instructions.extend(self._gen_expr(expr.operand, symbol_table))
                else:
                    instructions.append(Instruction(OpCode.FNEG))
                    #instructions.extend(self._gen_expr(expr.operand, symbol_table))
                if not require_result:
                    instructions.append(Instruction(OpCode.POP))
            elif expr.op == KeywordType.NOT:
                instructions.extend(self._gen_expr(expr.operand, symbol_table))
                instructions.append(Instruction(OpCode.LNOT))
                if not require_result:
                    instructions.append(Instruction(OpCode.POP))
            elif expr.op == KeywordType.BIT_NOT:
                instructions.extend(self._gen_expr(expr.operand, symbol_table))
                instructions.append(Instruction(OpCode.BNOT))
                if not require_result:
                    instructions.append(Instruction(OpCode.POP))
            else:
                raise RuntimeError("Unsupported unary operator: " + str(expr.op))
        elif isinstance(expr, BinaryExpr):
            if expr.op == KeywordType.EQUAL:
                new_inst, lt, rt = self._gen_binary_operant(expr, symbol_table)
                instructions.extend(new_inst)
                if lt == VarType.INT and rt == VarType.INT:
                    instructions.append(Instruction(OpCode.IEQ))
                elif lt == VarType.FLOAT and rt == VarType.FLOAT:
                    instructions.append(Instruction(OpCode.FEQ))
                else:
                    raise RuntimeError("Unsupported binary operator: " + str(expr.op))
                if not require_result:
                    instructions.append(Instruction(OpCode.POP))
            elif expr.op == KeywordType.NOT_EQUAL:
                new_inst, lt, rt = self._gen_binary_operant(expr, symbol_table)
                instructions.extend(new_inst)
                if lt == VarType.INT and rt == VarType.INT:
                    instructions.append(Instruction(OpCode.INE))
                elif lt == VarType.FLOAT and rt == VarType.FLOAT:
                    instructions.append(Instruction(OpCode.FNE))
                else:
                    raise RuntimeError("Unsupported binary operator: " + str(expr.op))
                if not require_result:
                    instructions.append(Instruction(OpCode.POP))
            elif expr.op == KeywordType.GREATER:
                new_inst, lt, rt = self._gen_binary_operant(expr, symbol_table)
                instructions.extend(new_inst)
                if lt == VarType.INT and rt == VarType.INT:
                    instructions.append(Instruction(OpCode.IGT))
                elif lt == VarType.FLOAT and rt == VarType.FLOAT:
                    instructions.append(Instruction(OpCode.FGT))
                else:
                    raise RuntimeError("Unsupported binary operator: " + str(expr.op))
                if not require_result:
                    instructions.append(Instruction(OpCode.POP))
            elif expr.op == KeywordType.LESS:
                new_inst, lt, rt = self._gen_binary_operant(expr, symbol_table)
                instructions.extend(new_inst)
                if lt == VarType.INT and rt == VarType.INT:
                    instructions.append(Instruction(OpCode.ILT))
                elif lt == VarType.FLOAT and rt == VarType.FLOAT:
                    instructions.append(Instruction(OpCode.FLT))
                else:
                    raise RuntimeError("Unsupported binary operator: " + str(expr.op))
                if not require_result:
                    instructions.append(Instruction(OpCode.POP))
            elif expr.op == KeywordType.GREATER_EQUAL:
                new_inst, lt, rt = self._gen_binary_operant(expr, symbol_table)
                instructions.extend(new_inst)
                if lt == VarType.INT and rt == VarType.INT:
                    instructions.append(Instruction(OpCode.IGE))
                elif lt == VarType.FLOAT and rt == VarType.FLOAT:
                    instructions.append(Instruction(OpCode.FGE))
                else:
                    raise RuntimeError("Unsupported binary operator: " + str(expr.op))
                if not require_result:
                    instructions.append(Instruction(OpCode.POP))
            elif expr.op == KeywordType.LESS_EQUAL:
                new_inst, lt, rt = self._gen_binary_operant(expr, symbol_table)
                instructions.extend(new_inst)
                if lt == VarType.INT and rt == VarType.INT:
                    instructions.append(Instruction(OpCode.ILE))
                elif lt == VarType.FLOAT and rt == VarType.FLOAT:
                    instructions.append(Instruction(OpCode.FLE))
                else:
                    raise RuntimeError("Unsupported binary operator: " + str(expr.op))
                if not require_result:
                    instructions.append(Instruction(OpCode.POP))
            elif expr.op == KeywordType.AND:
                new_inst, lt, rt = self._gen_binary_operant(expr, symbol_table)
                instructions.extend(new_inst)
                if lt == VarType.INT and rt == VarType.INT:
                    instructions.append(Instruction(OpCode.BAND))
                else:
                    raise RuntimeError("Unsupported binary operator: " + str(expr.op))
                if not require_result:
                    instructions.append(Instruction(OpCode.POP))
            elif expr.op == KeywordType.OR:
                new_inst, lt, rt = self._gen_binary_operant(expr, symbol_table)
                instructions.extend(new_inst)
                if lt == VarType.INT and rt == VarType.INT:
                    instructions.append(Instruction(OpCode.BOR))
                else:
                    raise RuntimeError("Unsupported binary operator: " + str(expr.op))
                if not require_result:
                    instructions.append(Instruction(OpCode.POP))

            elif expr.op == KeywordType.PLUS:
                new_inst, lt, rt = self._gen_binary_operant(expr, symbol_table)
                instructions.extend(new_inst)
                if lt == VarType.INT and rt == VarType.INT:
                    instructions.append(Instruction(OpCode.IADD))
                elif lt == VarType.FLOAT and rt == VarType.FLOAT:
                    instructions.append(Instruction(OpCode.FADD))
                else:
                    raise RuntimeError("Unsupported binary operator: " + str(expr.op))
                if not require_result:
                    instructions.append(Instruction(OpCode.POP))
            elif expr.op == KeywordType.MINUS:
                new_inst, lt, rt = self._gen_binary_operant(expr, symbol_table)
                instructions.extend(new_inst)
                if lt == VarType.INT and rt == VarType.INT:
                    instructions.append(Instruction(OpCode.ISUB))
                elif lt == VarType.FLOAT and rt == VarType.FLOAT:
                    instructions.append(Instruction(OpCode.FSUB))
                else:
                    raise RuntimeError("Unsupported binary operator: " + str(expr.op))
                if not require_result:
                    instructions.append(Instruction(OpCode.POP))
            elif expr.op == KeywordType.MULTIPLY:
                new_inst, lt, rt = self._gen_binary_operant(expr, symbol_table)
                instructions.extend(new_inst)
                if lt == VarType.INT and rt == VarType.INT:
                    instructions.append(Instruction(OpCode.IMUL))
                elif lt == VarType.FLOAT and rt == VarType.FLOAT:
                    instructions.append(Instruction(OpCode.FMUL))
                else:
                    raise RuntimeError("Unsupported binary operator: " + str(expr.op))
                if not require_result:
                    instructions.append(Instruction(OpCode.POP))
            elif expr.op == KeywordType.DIVIDE:
                new_inst, lt, rt = self._gen_binary_operant(expr, symbol_table)
                instructions.extend(new_inst)
                if lt == VarType.INT and rt == VarType.INT:
                    instructions.append(Instruction(OpCode.IDIV))
                elif lt == VarType.FLOAT and rt == VarType.FLOAT:
                    instructions.append(Instruction(OpCode.FDIV))
                else:
                    raise RuntimeError("Unsupported binary operator: " + str(expr.op))
                if not require_result:
                    instructions.append(Instruction(OpCode.POP))
            elif expr.op == KeywordType.MODULO:
                new_inst, lt, rt = self._gen_binary_operant(expr, symbol_table)
                instructions.extend(new_inst)
                if lt == VarType.INT and rt == VarType.INT:
                    instructions.append(Instruction(OpCode.IMOD))
                else:
                    raise RuntimeError("Unsupported binary operator: " + str(expr.op))
                if not require_result:
                    instructions.append(Instruction(OpCode.POP))

            elif expr.op == KeywordType.ASSIGNMENT:
                instructions.extend(self._gen_expr(expr.right, symbol_table, True))
                if isinstance(expr.left, VarExpr):
                    instructions.extend(self._store_var(expr.left, symbol_table))
                    if require_result:
                        instructions.extend(self._load_var(expr.left, symbol_table))
                else:
                    raise RuntimeError("Unsupported binary operator: " + str(expr.op))
            elif expr.op == KeywordType.ADD_ASSIGNMENT:
                new_inst, lt, rt = self._gen_binary_operant(expr, symbol_table)
                instructions.extend(new_inst)
                if lt == VarType.INT and rt == VarType.INT:
                    instructions.append(Instruction(OpCode.IADD))
                elif lt == VarType.FLOAT and rt == VarType.FLOAT:
                    instructions.append(Instruction(OpCode.FADD))
                else:
                    raise RuntimeError("Unsupported binary operator: " + str(expr.op))
                if isinstance(expr.left, VarExpr):
                    instructions.extend(self._store_var(expr.left, symbol_table))
                    if require_result:
                        instructions.extend(self._load_var(expr.left, symbol_table))
                else:
                    raise RuntimeError("Unsupported left operand of assignment: " + str(expr.left))
            elif expr.op == KeywordType.SUBTRACT_ASSIGNMENT:
                new_inst, lt, rt = self._gen_binary_operant(expr, symbol_table)
                instructions.extend(new_inst)
                if lt == VarType.INT and rt == VarType.INT:
                    instructions.append(Instruction(OpCode.ISUB))
                elif lt == VarType.FLOAT and rt == VarType.FLOAT:
                    instructions.append(Instruction(OpCode.FSUB))
                else:
                    raise RuntimeError("Unsupported binary operator: " + str(expr.op))
                if isinstance(expr.left, VarExpr):
                    instructions.extend(self._store_var(expr.left, symbol_table))
                    if require_result:
                        instructions.extend(self._load_var(expr.left, symbol_table))
                else:
                    raise RuntimeError("Unsupported left operand of assignment: " + str(expr.left))
            elif expr.op == KeywordType.MULTIPLY_ASSIGNMENT:
                new_inst, lt, rt = self._gen_binary_operant(expr, symbol_table)
                instructions.extend(new_inst)
                if lt == VarType.INT and rt == VarType.INT:
                    instructions.append(Instruction(OpCode.IMUL))
                elif lt == VarType.FLOAT and rt == VarType.FLOAT:
                    instructions.append(Instruction(OpCode.FMUL))
                else:
                    raise RuntimeError("Unsupported binary operator: " + str(expr.op))
                if isinstance(expr.left, VarExpr):
                    instructions.extend(self._store_var(expr.left, symbol_table))
                    if require_result:
                        instructions.extend(self._load_var(expr.left, symbol_table))
                else:
                    raise RuntimeError("Unsupported left operand of assignment: " + str(expr.left))
            elif expr.op == KeywordType.DIVIDE_ASSIGNMENT:
                new_inst, lt, rt = self._gen_binary_operant(expr, symbol_table)
                instructions.extend(new_inst)
                if lt == VarType.INT and rt == VarType.INT:
                    instructions.append(Instruction(OpCode.IDIV))
                elif lt == VarType.FLOAT and rt == VarType.FLOAT:
                    instructions.append(Instruction(OpCode.FDIV))
                else:
                    raise RuntimeError("Unsupported binary operator: " + str(expr.op))
                if isinstance(expr.left, VarExpr):
                    instructions.extend(self._store_var(expr.left, symbol_table))
                    if require_result:
                        instructions.extend(self._load_var(expr.left, symbol_table))
                else:
                    raise RuntimeError("Unsupported left operand of assignment: " + str(expr.left))
            elif expr.op == KeywordType.MODULO_ASSIGNMENT:
                new_inst, lt, rt = self._gen_binary_operant(expr, symbol_table)
                instructions.extend(new_inst)
                if lt == VarType.INT and rt == VarType.INT:
                    instructions.append(Instruction(OpCode.IMOD))
                else:
                    raise RuntimeError("Unsupported binary operator: " + str(expr.op))
                if isinstance(expr.left, VarExpr):
                    instructions.extend(self._store_var(expr.left, symbol_table))
                    if require_result:
                        instructions.extend(self._load_var(expr.left, symbol_table))
                else:
                    raise RuntimeError("Unsupported left operand of assignment: " + str(expr.left))
            elif expr.op == KeywordType.BIT_AND_ASSIGNMENT:
                new_inst, lt, rt = self._gen_binary_operant(expr, symbol_table)
                instructions.extend(new_inst)
                if lt == VarType.INT and rt == VarType.INT:
                    instructions.append(Instruction(OpCode.BAND))
                else:
                    raise RuntimeError("Unsupported binary operator: " + str(expr.op))
                if isinstance(expr.left, VarExpr):
                    instructions.extend(self._store_var(expr.left, symbol_table))
                    if require_result:
                        instructions.extend(self._load_var(expr.left, symbol_table))
                else:
                    raise RuntimeError("Unsupported left operand of assignment: " + str(expr.left))
            elif expr.op == KeywordType.BIT_OR_ASSIGNMENT:
                new_inst, lt, rt = self._gen_binary_operant(expr, symbol_table)
                instructions.extend(new_inst)
                if lt == VarType.INT and rt == VarType.INT:
                    instructions.append(Instruction(OpCode.BOR))
                else:
                    raise RuntimeError("Unsupported binary operator: " + str(expr.op))
                if isinstance(expr.left, VarExpr):
                    instructions.extend(self._store_var(expr.left, symbol_table))
                    if require_result:
                        instructions.extend(self._load_var(expr.left, symbol_table))
                else:
                    raise RuntimeError("Unsupported left operand of assignment: " + str(expr.left))
            elif expr.op == KeywordType.BIT_XOR_ASSIGNMENT:
                new_inst, lt, rt = self._gen_binary_operant(expr, symbol_table)
                instructions.extend(new_inst)
                if lt == VarType.INT and rt == VarType.INT:
                    instructions.append(Instruction(OpCode.BXOR))
                else:
                    raise RuntimeError("Unsupported binary operator: " + str(expr.op))
                if isinstance(expr.left, VarExpr):
                    instructions.extend(self._store_var(expr.left, symbol_table))
                    if require_result:
                        instructions.extend(self._load_var(expr.left, symbol_table))
                else:
                    raise RuntimeError("Unsupported left operand of assignment: " + str(expr.left))
            elif expr.op == KeywordType.LEFT_SHIFT_ASSIGNMENT:
                new_inst, lt, rt = self._gen_binary_operant(expr, symbol_table)
                instructions.extend(new_inst)
                if lt == VarType.INT and rt == VarType.INT:
                    instructions.append(Instruction(OpCode.SHL))
                else:
                    raise RuntimeError("Unsupported binary operator: " + str(expr.op))
                if isinstance(expr.left, VarExpr):
                    instructions.extend(self._store_var(expr.left, symbol_table))
                    if require_result:
                        instructions.extend(self._load_var(expr.left, symbol_table))
                else:
                    raise RuntimeError("Unsupported left operand of assignment: " + str(expr.left))
            elif expr.op == KeywordType.RIGHT_SHIFT_ASSIGNMENT:
                new_inst, lt, rt = self._gen_binary_operant(expr, symbol_table)
                instructions.extend(new_inst)
                if lt == VarType.INT and rt == VarType.INT:
                    instructions.append(Instruction(OpCode.SHR))
                else:
                    raise RuntimeError("Unsupported binary operator: " + str(expr.op))
                if isinstance(expr.left, VarExpr):
                    instructions.extend(self._store_var(expr.left, symbol_table))
                    if require_result:
                        instructions.extend(self._load_var(expr.left, symbol_table))
                else:
                    raise RuntimeError("Unsupported left operand of assignment: " + str(expr.left))

            elif expr.op == KeywordType.BIT_AND:
                new_inst, lt, rt = self._gen_binary_operant(expr, symbol_table)
                instructions.extend(new_inst)
                if lt == VarType.INT and rt == VarType.INT:
                    instructions.append(Instruction(OpCode.BAND))
                else:
                    raise RuntimeError("Unsupported binary operator: " + str(expr.op))
                if not require_result:
                    instructions.append(Instruction(OpCode.POP))
            elif expr.op == KeywordType.BIT_OR:
                new_inst, lt, rt = self._gen_binary_operant(expr, symbol_table)
                instructions.extend(new_inst)
                if lt == VarType.INT and rt == VarType.INT:
                    instructions.append(Instruction(OpCode.BOR))
                else:
                    raise RuntimeError("Unsupported binary operator: " + str(expr.op))
                if not require_result:
                    instructions.append(Instruction(OpCode.POP))
            elif expr.op == KeywordType.BIT_XOR:
                new_inst, lt, rt = self._gen_binary_operant(expr, symbol_table)
                instructions.extend(new_inst)
                if lt == VarType.INT and rt == VarType.INT:
                    instructions.append(Instruction(OpCode.BXOR))
                else:
                    raise RuntimeError("Unsupported binary operator: " + str(expr.op))
                if not require_result:
                    instructions.append(Instruction(OpCode.POP))
            elif expr.op == KeywordType.LEFT_SHIFT:
                new_inst, lt, rt = self._gen_binary_operant(expr, symbol_table)
                instructions.extend(new_inst)
                if lt == VarType.INT and rt == VarType.INT:
                    instructions.append(Instruction(OpCode.SHL))
                else:
                    raise RuntimeError("Unsupported binary operator: " + str(expr.op))
                if not require_result:
                    instructions.append(Instruction(OpCode.POP))
            elif expr.op == KeywordType.RIGHT_SHIFT:
                new_inst, lt, rt = self._gen_binary_operant(expr, symbol_table)
                instructions.extend(new_inst)
                if lt == VarType.INT and rt == VarType.INT:
                    instructions.append(Instruction(OpCode.SHR))
                else:
                    raise RuntimeError("Unsupported binary operator: " + str(expr.op))
                if not require_result:
                    instructions.append(Instruction(OpCode.POP))

            elif expr.op == KeywordType.AS:
                if isinstance(expr.right, TypeCastExpr):
                    if expr.right.var_type == get_expr_type(expr.left, symbol_table):
                        pass
                    else:
                        instructions.extend(self._gen_expr(expr.left, symbol_table))
                        if expr.right.var_type == VarType.INT:
                            instructions.append(Instruction(OpCode.F2I))
                        elif expr.right.var_type == VarType.FLOAT:
                            instructions.append(Instruction(OpCode.I2F))
                else:
                    raise RuntimeError("Unsupported binary operator: " + str(expr.op))

            else:
                raise RuntimeError("Unsupported binary operator: " + str(expr.op))
        elif isinstance(expr, LiteralExpr):
            if isinstance(expr.value, int):
                instructions.append(Instruction(OpCode.IMMI, U32(expr.value)))
            else:
                instructions.append(Instruction(OpCode.IMMF, F32(expr.value)))
            if not require_result:
                instructions.append(Instruction(OpCode.POP))
        elif isinstance(expr, VarExpr):
            instructions.extend(self._load_var(expr, symbol_table))
            if not require_result:
                instructions.append(Instruction(OpCode.POP))

        elif isinstance(expr, FuncCallExpr):
            if expr.info["return_type"] == VarType.VOID and require_result:
                raise RuntimeError("Function call with void return type must not be used as an expression")
            for arg in expr.args:
                instructions.extend(self._gen_expr(arg, symbol_table))
            instructions.append(Instruction(OpCode.CALL, Label(expr.func), U8(len(expr.args))))
            if not require_result:
                instructions.append(Instruction(OpCode.POP))
        elif isinstance(expr, SysCallExpr):
            if expr.func is not KeywordType.READ_JOINT and require_result:
                raise RuntimeError("System call with no return must not be used as an expression")
            for arg in expr.args:
                instructions.extend(self._gen_expr(arg, symbol_table))
            if expr.func == KeywordType.DELAY:
                instructions.append(Instruction(OpCode.DELAY))
            elif expr.func == KeywordType.RESET:
                instructions.append(Instruction(OpCode.RST))
            elif expr.func == KeywordType.WAIT:
                instructions.append(Instruction(OpCode.WAIT))
            elif expr.func == KeywordType.WAIT_JOINT:
                instructions.append(Instruction(OpCode.WAITJ))
            elif expr.func == KeywordType.MOV_JOINT:
                instructions.append(Instruction(OpCode.MOVJ))
            elif expr.func == KeywordType.SET_JOINT:
                instructions.append(Instruction(OpCode.SETJ))
            elif expr.func == KeywordType.READ_JOINT:
                instructions.append(Instruction(OpCode.READJ))
                if not require_result:
                    instructions.append(Instruction(OpCode.POP))
            elif expr.func == KeywordType.MOV_ORTH_COORD:
                instructions.append(Instruction(OpCode.MOVOC))
            elif expr.func == KeywordType.SET_ORTH_COORD:
                instructions.append(Instruction(OpCode.SETOC))
            elif expr.func == KeywordType.MOV_JOINT_COORD:
                instructions.append(Instruction(OpCode.MOVJC))
            elif expr.func == KeywordType.SET_JOINT_COORD:
                instructions.append(Instruction(OpCode.SETJC))
            elif expr.func == KeywordType.GRIPPER_OPEN:
                instructions.append(Instruction(OpCode.GRIPPER_OPEN))
            elif expr.func == KeywordType.GRIPPER_CLOSE:
                instructions.append(Instruction(OpCode.GRIPPER_CLOSE))
            elif expr.func == KeywordType.SET_JOINT_SPEED:
                instructions.append(Instruction(OpCode.SETJSPD))
            elif expr.func == KeywordType.OLED_SHOW_INT:
                instructions.append(Instruction(OpCode.OLEDI))
            elif expr.func == KeywordType.PRINT:
                instructions.append(Instruction(OpCode.PRINT))
            else:
                raise RuntimeError("Unsupported system call: " + str(expr.func))

        return instructions

    def _gen_binary_operant(self, expr : BinaryExpr, symbol_table : SymbolTable) -> (List[Instruction], VarType, VarType):
        instructions = []
        instructions.extend(self._gen_expr(expr.left, symbol_table))
        instructions.extend(self._gen_expr(expr.right, symbol_table))
        lt = get_expr_type(expr.left, symbol_table)
        rt = get_expr_type(expr.right, symbol_table)
        return instructions, lt, rt

    def _load_var(self, expr : VarExpr, symbol_table : SymbolTable) -> List[Instruction]:
        instructions = []
        if expr.name in self.debug_info["constants"]:
            instructions.append(Instruction(OpCode.LOADK, U16(self.debug_info["constants"][expr.name]["offset"])))
        elif expr.name in self.debug_info["globals"]:
            instructions.append(Instruction(OpCode.LOADG, U16(self.debug_info["globals"][expr.name]["offset"])))
        else:
            sym = symbol_table.lookup(expr.name)
            offset = sym["offset"]
            instructions.append(Instruction(OpCode.LOADL, U8(offset)))
        return instructions

    def _store_var(self, expr : VarExpr, symbol_table : SymbolTable) -> List[Instruction]:
        instructions = []
        if expr.name in self.debug_info["globals"]:
            instructions.append(Instruction(OpCode.STORG, U16(self.debug_info["globals"][expr.name]["offset"])))
        else:
            sym = symbol_table.lookup(expr.name)
            offset = sym["offset"]
            instructions.append(Instruction(OpCode.STORL, U8(offset)))
        return instructions
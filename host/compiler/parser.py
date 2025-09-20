from .lexer import VarType, Token, TokenType, KeywordType, keywordtype_to_vartype
from .ast_node import *
from typing import List

# symbol table
class SymbolTable:
    def __init__(self):
        self.stack = [{}]
        self.local_var_count = 0

    def enter_scope(self):
        self.stack.append({})

    def exit_scope(self):
        if len(self.stack) > 1:
            self.stack.pop()
        else:
            raise Exception("Cannot exit global scope")

    def decl_local(self, name : str, info : dict) -> bool:
        if self.is_symbol_defined(name):
            return False
        current_scope = self.stack[-1]
        current_scope[name] = info
        self.local_var_count += 1
        return True

    def decl_global(self, name : str, info : dict) -> bool:
        if self.is_symbol_defined(name):
            return False
        self.stack[0][name] = info
        return True

    def lookup(self, name : str) -> dict:
        for scope in reversed(self.stack):
            if name in scope:
                return scope[name]
        raise RuntimeError(f"Symbol not found: {name}")

    def is_symbol_defined(self, name : str) -> bool:
        try:
            self.lookup(name)
            return True
        except RuntimeError:
            return False

    def get_current_scope_symbol_num(self) -> int:
        return len(self.stack[-1])

    def get_local_var_count(self) -> int:
        return self.local_var_count

    def clean_local_var_count(self):
        self.local_var_count = 0

# 数字越大，优先级越高
operator_precedence = {
    KeywordType.ASSIGNMENT: 10,
    KeywordType.ADD_ASSIGNMENT: 10,
    KeywordType.SUBTRACT_ASSIGNMENT: 10,
    KeywordType.MULTIPLY_ASSIGNMENT: 10,
    KeywordType.DIVIDE_ASSIGNMENT: 10,
    KeywordType.MODULO_ASSIGNMENT: 10,
    KeywordType.BIT_OR_ASSIGNMENT: 10,
    KeywordType.BIT_XOR_ASSIGNMENT: 10,
    KeywordType.BIT_AND_ASSIGNMENT: 10,
    KeywordType.LEFT_SHIFT_ASSIGNMENT: 10,
    KeywordType.RIGHT_SHIFT_ASSIGNMENT: 10,

    KeywordType.OR: 20,
    KeywordType.AND: 30,

    KeywordType.BIT_OR: 40,
    KeywordType.BIT_XOR: 50,
    KeywordType.BIT_AND: 60,

    KeywordType.EQUAL: 70,
    KeywordType.NOT_EQUAL: 70,
    KeywordType.LESS: 80,
    KeywordType.LESS_EQUAL: 80,
    KeywordType.GREATER: 80,
    KeywordType.GREATER_EQUAL: 80,

    KeywordType.LEFT_SHIFT: 90,
    KeywordType.RIGHT_SHIFT: 90,

    KeywordType.PLUS: 100,
    KeywordType.MINUS: 100,

    KeywordType.MULTIPLY: 110,
    KeywordType.DIVIDE: 110,
    KeywordType.MODULO: 110,

    KeywordType.NOT: 120,
    KeywordType.BIT_NOT: 120,

    KeywordType.AS: 120,
}

unary_ops = (KeywordType.NOT, KeywordType.BIT_NOT, KeywordType.MINUS)
binary_ops = (
    KeywordType.ASSIGNMENT,
    KeywordType.ADD_ASSIGNMENT,
    KeywordType.SUBTRACT_ASSIGNMENT,
    KeywordType.MULTIPLY_ASSIGNMENT,
    KeywordType.DIVIDE_ASSIGNMENT,
    KeywordType.MODULO_ASSIGNMENT,
    KeywordType.BIT_OR_ASSIGNMENT,
    KeywordType.BIT_XOR_ASSIGNMENT,
    KeywordType.BIT_AND_ASSIGNMENT,
    KeywordType.LEFT_SHIFT_ASSIGNMENT,
    KeywordType.RIGHT_SHIFT_ASSIGNMENT,

    KeywordType.OR,
    KeywordType.AND,

    KeywordType.BIT_OR,
    KeywordType.BIT_XOR,
    KeywordType.BIT_AND,

    KeywordType.EQUAL,
    KeywordType.NOT_EQUAL,
    KeywordType.LESS,
    KeywordType.LESS_EQUAL,
    KeywordType.GREATER,
    KeywordType.GREATER_EQUAL,

    KeywordType.LEFT_SHIFT,
    KeywordType.RIGHT_SHIFT,

    KeywordType.PLUS,
    KeywordType.MINUS,

    KeywordType.MULTIPLY,
    KeywordType.DIVIDE,
    KeywordType.MODULO,

    KeywordType.AS,
)

# parser
class Parser:
    def __init__(self, tokens : List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.symbol_table = SymbolTable()

    def _peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def _advance(self):
        tok = self._peek()
        if tok is not None:
            self.pos += 1
        return tok

    def _expect(self, keyword_type):
        tok = self._peek()
        if tok is None or tok.keyword_type != keyword_type:
            raise Exception(f"Expected {keyword_type}, got {tok}")
        self.pos += 1
        return tok

    def _at_end(self):
        return self.pos >= len(self.tokens)

    @staticmethod
    def _get_precedence(op : KeywordType) -> int:
        if op in operator_precedence:
            return operator_precedence[op]
        return -1

    def parse(self) -> Program:
        global_decls = []
        while self.pos < len(self.tokens):
            if self.tokens[self.pos].token_type == TokenType.KEYWORD and self.tokens[self.pos].keyword_type == KeywordType.FN:
                global_decls.append(self._parse_func_decl())
            elif self.tokens[self.pos].token_type == TokenType.KEYWORD and (self.tokens[self.pos].keyword_type == KeywordType.LET or self.tokens[self.pos].keyword_type == KeywordType.CONST):
                global_decls.extend(self._parse_var_decl())
            else:
                raise Exception(f"Unexpected token {self.tokens[self.pos].__str__()}")
            self.pos += 1
        return Program(global_decls)

    def _parse_func_decl(self) -> FuncDecl:
        self.pos += 1 # skip "fn"
        name : str
        params : list
        return_type : VarType = VarType.VOID
        body : list
        if self.pos < len(self.tokens) and self.tokens[self.pos].token_type == TokenType.IDENTIFIER:
            name = self.tokens[self.pos].name
            self.pos += 1
        else:
            raise Exception(f"Expected function name at line {self.tokens[self.pos-1].line}")
        if self.pos < len(self.tokens) and self.tokens[self.pos].token_type == TokenType.KEYWORD and self.tokens[self.pos].keyword_type == KeywordType.LEFT_PARENTHESIS:
            self.pos += 1
        else:
            raise Exception(f"Expected left parenthesis at line {self.tokens[self.pos-1].line}")
        params = self._parse_params()
        if self.pos < len(self.tokens) and self.tokens[self.pos].token_type == TokenType.KEYWORD and self.tokens[self.pos].keyword_type == KeywordType.RIGHT_PARENTHESIS:
            self.pos += 1
        else:
            raise Exception(f"Expected right parenthesis at line {self.tokens[self.pos-1].line}")
        if self.pos < len(self.tokens) and self.tokens[self.pos].token_type == TokenType.KEYWORD and self.tokens[self.pos].keyword_type == KeywordType.ARROW:
            self.pos += 1
            if self.pos < len(self.tokens) and self.tokens[self.pos].token_type == TokenType.KEYWORD:
                if self.tokens[self.pos].keyword_type == KeywordType.INT:
                    return_type = VarType.INT
                elif self.tokens[self.pos].keyword_type == KeywordType.FLOAT:
                    return_type = VarType.FLOAT
                #elif self.tokens[self.pos].keyword_type == KeywordType.BOOL:
                    #return_type = VarType.BOOL
                else:
                    raise Exception(f"Expected return type at line {self.tokens[self.pos-1].line}")
                self.pos += 1
        else:
            return_type = VarType.VOID

        func_info = {
            "type": "fn",
            "params": [p.var_type for p in params],
            "return_type": return_type,
        }
        if not self.symbol_table.decl_global(name, func_info):
            raise Exception(f"Symbol {name} redefined at line {self.tokens[self.pos - 1].line}")

        self.symbol_table.clean_local_var_count()
        self.symbol_table.enter_scope()
        for param in params:
            self.symbol_table.decl_local(param.var_name, {
                "type": "var",
                "var_type": param.var_type,
                "is_const": param.is_const
            })
        body = self._parse_chunk()
        self.symbol_table.exit_scope()

        #self.symbol_table.exit_scope()
        local_var_num = self.symbol_table.get_local_var_count()
        self.symbol_table.clean_local_var_count()

        func_decl = FuncDecl(name, params, return_type, body, local_var_num)
        return func_decl

    def _parse_var_decl(self) -> List[VarDecl]:
        is_const = False
        if self.tokens[self.pos].token_type == TokenType.KEYWORD and self.tokens[self.pos].keyword_type == KeywordType.CONST:
            is_const = True
            self.pos += 1
            if self.pos < len(self.tokens) and self.tokens[self.pos].token_type == TokenType.KEYWORD and self.tokens[self.pos].keyword_type == KeywordType.LET:
                #self.pos += 1
                pass
            else:
                raise Exception(f"Expected 'let' keyword at line {self.tokens[self.pos-1].line}")
        self.pos += 1 # skip let
        var_decls = []
        while 1:
            var_decls.append(self._parse_single_decl(is_const))
            if self.pos < len(self.tokens) and self.tokens[self.pos].token_type == TokenType.KEYWORD and self.tokens[self.pos].keyword_type == KeywordType.COMMA:
                self.pos += 1
            elif self.pos < len(self.tokens) and self.tokens[self.pos].token_type == TokenType.KEYWORD and self.tokens[self.pos].keyword_type == KeywordType.SEMICOLON:
                #self.pos += 1
                break
            else:
                raise Exception(f"Expected comma or semicolon at line {self.tokens[self.pos-1].line}")
        return var_decls

    def _parse_single_decl(self, is_const : bool) -> VarDecl:
        #name = ""
        var_type = VarType.AUTO
        init_expr = None
        has_decl_type = False
        if self.pos < len(self.tokens) and self.tokens[self.pos].token_type == TokenType.IDENTIFIER:
            name = self.tokens[self.pos].name
            self.pos += 1
        else:
            raise Exception(f"Expected variable name at line {self.tokens[self.pos-1].line}")
        if self.pos < len(self.tokens) and self.tokens[self.pos].token_type == TokenType.KEYWORD and self.tokens[self.pos].keyword_type == KeywordType.COLON:
            self.pos += 1
            if self.pos < len(self.tokens) and self.tokens[self.pos].token_type == TokenType.KEYWORD:
                if self.tokens[self.pos].keyword_type == KeywordType.INT:
                    var_type = VarType.INT
                elif self.tokens[self.pos].keyword_type == KeywordType.FLOAT:
                    var_type = VarType.FLOAT
                #elif self.tokens[self.pos].keyword_type == KeywordType.BOOL:
                    #var_type = VarType.BOOL
                else:
                    raise Exception(f"Expected variable type at line {self.tokens[self.pos-1].line}")
                self.pos += 1
                has_decl_type = True
        if self.pos < len(self.tokens) and self.tokens[self.pos].token_type == TokenType.KEYWORD and self.tokens[self.pos].keyword_type == KeywordType.ASSIGNMENT:
            self.pos += 1
            init_expr = self._parse_expr()
        elif not has_decl_type:
            raise Exception(f"Expected assignment or type declaration at line {self.tokens[self.pos-1].line}")

        if var_type == VarType.AUTO:
            inferred = get_expr_type(init_expr, self.symbol_table)
            var_type = inferred

        var_info = {
            "type" : "var",
            "var_type" : var_type,
            "is_const" : is_const,
        }

        if is_const:
            if not self.symbol_table.decl_global(name, var_info):
                raise Exception(f"Symbol {name} redefined at line {self.tokens[self.pos - 1].line}")
        elif not self.symbol_table.decl_local(name, var_info):
            raise Exception(f"Symbol {name} redefined at line {self.tokens[self.pos-1].line}")

        var_decl = VarDecl(var_type, name, is_const, init_expr)
        return var_decl

    def _parse_chunk(self) -> List[Node]:
        chunk = []
        if self.pos < len(self.tokens) and self.tokens[self.pos].token_type == TokenType.KEYWORD and self.tokens[self.pos].keyword_type == KeywordType.LEFT_BRACE:
            self.pos += 1
        else:
            raise Exception(f"Expected left brace at line {self.tokens[self.pos-1].line}")

        chunk_closed = False

        while self.pos < len(self.tokens):
            if self.tokens[self.pos].token_type == TokenType.KEYWORD:
                if self.tokens[self.pos].keyword_type == KeywordType.RIGHT_BRACE:
                    chunk_closed = True
                    break
                elif self.tokens[self.pos].keyword_type == KeywordType.LEFT_BRACE:
                    self.symbol_table.enter_scope()
                    chunk.extend(self._parse_chunk())
                    self.symbol_table.exit_scope()
                elif self.tokens[self.pos].keyword_type == KeywordType.IF:
                    chunk.append(self._parse_if_stmt())
                elif self.tokens[self.pos].keyword_type == KeywordType.WHILE:
                    chunk.append(self._parse_while_stmt())
                elif self.tokens[self.pos].keyword_type == KeywordType.LOOP:
                    chunk.append(self._parse_loop_stmt())
                elif self.tokens[self.pos].keyword_type == KeywordType.RETURN:
                    chunk.append(self._parse_return_stmt())
                elif self.tokens[self.pos].keyword_type == KeywordType.BREAK:
                    chunk.append(BreakStmt())
                    if self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1].token_type == TokenType.KEYWORD and self.tokens[self.pos + 1].keyword_type == KeywordType.SEMICOLON:
                        self.pos += 1
                    else:
                        raise Exception(f"Expected semicolon at line {self.tokens[self.pos-1].line}")
                elif self.tokens[self.pos].keyword_type == KeywordType.LET or self.tokens[self.pos].keyword_type == KeywordType.CONST:
                    chunk.extend(self._parse_var_decl())
                    #self.pos -= 1
                else:
                    chunk.append(self._parse_expr())
            else:
                chunk.append(self._parse_expr())
            self.pos += 1

        if not chunk_closed:
            raise Exception(f"Expected right brace at line {self.tokens[self.pos-1].line}")

        return chunk

    def _parse_params(self) -> List[Param]:
        params = []
        while 1:
            if self.pos < len(self.tokens) and self.tokens[self.pos].token_type == TokenType.IDENTIFIER:
                param = Param(VarType.INT, self.tokens[self.pos].name, False)
                self.pos += 1
                if self.pos < len(self.tokens) and self.tokens[self.pos].token_type == TokenType.KEYWORD and self.tokens[self.pos].keyword_type == KeywordType.COLON:
                    self.pos += 1
                    if self.pos < len(self.tokens) and self.tokens[self.pos].token_type == TokenType.KEYWORD:
                        if self.tokens[self.pos].keyword_type == KeywordType.CONST:
                            param.is_const = True
                            self.pos += 1
                            if self.tokens[self.pos].keyword_type == KeywordType.INT:
                                param.var_type = VarType.INT
                            elif self.tokens[self.pos].keyword_type == KeywordType.FLOAT:
                                param.var_type = VarType.FLOAT
                            #elif self.tokens[self.pos].keyword_type == KeywordType.BOOL:
                                #param.var_type = VarType.BOOL
                            else:
                                raise Exception(f"Expected parameter type at line {self.tokens[self.pos - 1].line}")
                        elif self.tokens[self.pos].keyword_type == KeywordType.INT:
                            param.var_type = VarType.INT
                        elif self.tokens[self.pos].keyword_type == KeywordType.FLOAT:
                            param.var_type = VarType.FLOAT
                        #elif self.tokens[self.pos].keyword_type == KeywordType.BOOL:
                            #param.var_type = VarType.BOOL
                        else:
                            raise Exception(f"Expected parameter type at line {self.tokens[self.pos-1].line}")
                        self.pos += 1
                    else:
                        raise Exception(f"Expected parameter type at line {self.tokens[self.pos - 1].line}")
                else:
                    raise Exception(f"Expected colon at line {self.tokens[self.pos-1].line}")
                params.append(param)
                if self.pos < len(self.tokens) and self.tokens[self.pos].token_type == TokenType.KEYWORD and self.tokens[self.pos].keyword_type == KeywordType.COMMA:
                    self.pos += 1
                else:
                    break
            elif self.pos < len(self.tokens) and self.tokens[self.pos].token_type == TokenType.KEYWORD and self.tokens[self.pos].keyword_type == KeywordType.RIGHT_PARENTHESIS:
                break
            else:
                raise Exception(f"Expected parameter at line {self.tokens[self.pos-1].line}")
        return params

    def _parse_if_stmt(self) -> IfStmt:
        self.pos += 1 # skip "if"
        cond_expr = self._parse_expr()
        self.symbol_table.enter_scope()
        then_stmt = self._parse_chunk()
        self.symbol_table.exit_scope()
        self.pos += 1 # skip "}"
        else_stmt = []
        if self.pos < len(self.tokens) and self.tokens[self.pos].token_type == TokenType.KEYWORD and self.tokens[self.pos].keyword_type == KeywordType.ELSE:
            self.pos += 1
            if self.pos < len(self.tokens) and self.tokens[self.pos].token_type == TokenType.KEYWORD and self.tokens[self.pos].keyword_type == KeywordType.IF:
                else_stmt.append(self._parse_if_stmt())
                #self.pos -= 1
            else:
                self.symbol_table.enter_scope()
                else_stmt.extend(self._parse_chunk())
                self.symbol_table.exit_scope()
        else:
            self.pos -= 1

        if_stmt = IfStmt(cond_expr, then_stmt, else_stmt)
        return if_stmt

    def _parse_while_stmt(self) -> WhileStmt:
        self.pos += 1 # skip "while"
        cond_expr = self._parse_expr()

        self.symbol_table.enter_scope()
        body = self._parse_chunk()
        self.symbol_table.exit_scope()
        while_stmt = WhileStmt(cond_expr, body)
        return while_stmt

    def _parse_loop_stmt(self) -> LoopStmt:
        self.pos += 1 # skip "loop"
        self.symbol_table.enter_scope()
        body = self._parse_chunk()
        self.symbol_table.exit_scope()
        loop_stmt = LoopStmt(body)
        return loop_stmt

    def _parse_return_stmt(self) -> ReturnStmt:
        self.pos += 1 # skip "return"
        if self.pos < len(self.tokens) and self.tokens[self.pos].token_type == TokenType.KEYWORD and self.tokens[self.pos].keyword_type == KeywordType.SEMICOLON:
            return ReturnStmt(None)
        return ReturnStmt(self._parse_expr())

    def _parse_expr(self) -> Expr:
        return self._parse_expr_bp(0)

    def _parse_expr_bp(self, min_bp : int = 0) -> Expr:
        tok = self._advance()
        if tok is None:
            raise Exception("Unexpected EOF in expression")

        # 解析前缀表达式
        if tok.token_type == TokenType.IDENTIFIER:
            name = tok.name
            # 查符号表（区分变量/函数/未定义）
            try:
                sym = self.symbol_table.lookup(name)
                if sym["type"] == "var":
                    left = VarExpr(name, sym)
                elif sym["type"] == "fn":
                    left = FuncCallExpr(name, sym)
                else:
                    raise Exception(f"Unexpected symbol type {sym['type']} at line {tok.line}")
            except RuntimeError:
                raise Exception(f"Undefined identifier {name} at line {tok.line}")
        elif tok.token_type == TokenType.LITERAL:
            if tok.literal_type == VarType.INT:
                left = LiteralExpr(tok.int_value)
            elif tok.literal_type == VarType.FLOAT:
                left = LiteralExpr(tok.float_value)
            #elif tok.literal_type == VarType.BOOL:
                #left = LiteralExpr(tok.bool_value)
            else:
                raise Exception(f"Unexpected literal type {tok.literal_type} at line {tok.line}")
        elif tok.token_type == TokenType.KEYWORD and tok.keyword_type in unary_ops:
            # 解析一元运算符
            rhs = self._parse_expr_bp(self._get_precedence(tok.keyword_type) if not tok.keyword_type == KeywordType.MINUS else 120)
            left = UnaryExpr(tok.keyword_type, rhs)
        elif tok.token_type == TokenType.KEYWORD and tok.keyword_type == KeywordType.LEFT_PARENTHESIS:
            # 解析括号表达式
            inner = self._parse_expr_bp(0)
            self._expect(KeywordType.RIGHT_PARENTHESIS)
            left = inner
        elif tok.token_type == TokenType.KEYWORD and KeywordType.DELAY.value <= tok.keyword_type.value <= KeywordType.PRINT.value:
            # 解析系统函数调用
            left = SysCallExpr(tok.keyword_type)
        else:
            raise Exception(f"Unexpected token {tok} at line {tok.line}")

        # 解析中缀表达式
        while not self._at_end():
            op = self._peek()
            if op.token_type != TokenType.KEYWORD:
                break

            # 二元运算符
            if op.keyword_type in binary_ops:
                bp = self._get_precedence(op.keyword_type)
                if bp < min_bp:
                    break
                self._advance()
                if op.keyword_type == KeywordType.AS:
                    type = self._advance()
                    if type is not None and type.token_type == TokenType.KEYWORD and type.keyword_type in [KeywordType.INT, KeywordType.FLOAT]:
                        rhs = TypeCastExpr(keywordtype_to_vartype(type.keyword_type))
                    else:
                        raise Exception(f"Unexpected type {type}")
                else:
                    rhs = self._parse_expr_bp(bp)
                left = BinaryExpr(op.keyword_type, left, rhs)
                continue
            # 函数调用 (arg,...)
            elif op.keyword_type == KeywordType.LEFT_PARENTHESIS and (isinstance(left, FuncCallExpr) or isinstance(left, SysCallExpr)):
                self._advance()
                args = []
                peek = self._peek()
                if not (peek.token_type == TokenType.KEYWORD and peek.keyword_type == KeywordType.RIGHT_PARENTHESIS):
                    while True:
                        args.append(self._parse_expr_bp(0))
                        if self._peek().keyword_type == KeywordType.COMMA:
                            self._advance()
                            continue
                        break
                self._expect(KeywordType.RIGHT_PARENTHESIS)
                left.args = args
            break
        return left

def get_expr_type(expr: Expr, symbol_table: SymbolTable) -> VarType:
    if isinstance(expr, LiteralExpr):
        if isinstance(expr.value, int):
            return VarType.INT
        elif isinstance(expr.value, float):
            return VarType.FLOAT
        #elif isinstance(expr.value, bool):
            #return VarType.BOOL
    elif isinstance(expr, VarExpr):
        return expr.symbol_info["var_type"]
    elif isinstance(expr, UnaryExpr):
        t = get_expr_type(expr.operand, symbol_table)
        if expr.op == KeywordType.MINUS and t in (VarType.INT, VarType.FLOAT):
            return t
        if expr.op == KeywordType.BIT_NOT or expr.op == KeywordType.NOT:
            if t == VarType.INT:
                return VarType.INT
            else:
                raise Exception(f"Invalid operand type for {expr.op.name}: {t}")
        #if expr.op == KeywordType.NOT and t == VarType.INT:
            #return VarType.INT
    elif isinstance(expr, BinaryExpr):
        lt = get_expr_type(expr.left, symbol_table)
        rt = get_expr_type(expr.right, symbol_table)
        if expr.op in (KeywordType.PLUS, KeywordType.MINUS, KeywordType.MULTIPLY, KeywordType.DIVIDE):
            return VarType.FLOAT if VarType.FLOAT in (lt, rt) else VarType.INT
        elif expr.op in (KeywordType.MODULO, KeywordType.BIT_AND, KeywordType.BIT_OR, KeywordType.BIT_XOR, KeywordType.LEFT_SHIFT, KeywordType.RIGHT_SHIFT):
            if lt == VarType.INT and rt == VarType.INT:
                return VarType.INT
            else:
                raise Exception(f"Invalid operand types for {expr.op.name}: {lt}, {rt}")
        elif expr.op in (KeywordType.ASSIGNMENT, KeywordType.ADD_ASSIGNMENT, KeywordType.SUBTRACT_ASSIGNMENT,
                         KeywordType.MULTIPLY_ASSIGNMENT, KeywordType.DIVIDE_ASSIGNMENT, KeywordType.MODULO_ASSIGNMENT,
                         KeywordType.BIT_AND_ASSIGNMENT, KeywordType.BIT_OR_ASSIGNMENT, KeywordType.BIT_XOR_ASSIGNMENT,
                         KeywordType.LEFT_SHIFT_ASSIGNMENT, KeywordType.RIGHT_SHIFT_ASSIGNMENT):
            return lt
        elif expr.op == KeywordType.AS:
            return expr.right.var_type
        elif expr.op in (KeywordType.EQUAL, KeywordType.NOT_EQUAL, KeywordType.LESS, KeywordType.LESS_EQUAL,
                         KeywordType.GREATER, KeywordType.GREATER_EQUAL, KeywordType.AND, KeywordType.OR):
            return VarType.INT

    elif isinstance(expr, FuncCallExpr):
        func_info = symbol_table.lookup(expr.func)
        return func_info["return_type"]
    elif isinstance(expr, SysCallExpr):
        return get_syscall_return_type(expr.func)
    elif isinstance(expr, TypeCastExpr):
        return expr.var_type
    raise Exception(f"Cannot infer type of {expr}")

def get_syscall_return_type(keyword_type: KeywordType) -> VarType:
    if keyword_type == KeywordType.READ_JOINT:
        return VarType.FLOAT
    else:
        return VarType.VOID

def get_syscall_arg(keyword_type: KeywordType) -> List[VarType]:
    if keyword_type == KeywordType.DELAY:
        return [VarType.INT]
    elif keyword_type == KeywordType.WAIT_JOINT:
        return [VarType.INT]
    elif keyword_type in (KeywordType.MOV_JOINT, KeywordType.SET_JOINT):
        return [VarType.INT, VarType.FLOAT]
    elif keyword_type == KeywordType.READ_JOINT:
        return [VarType.INT]
    elif keyword_type in (KeywordType.MOV_ORTH_COORD, KeywordType.SET_ORTH_COORD):
        return [VarType.FLOAT for _ in range(4)]
    elif keyword_type in (KeywordType.MOV_JOINT_COORD, KeywordType.SET_JOINT_COORD):
        return [VarType.FLOAT for _ in range(6)]
    elif keyword_type == KeywordType.SET_JOINT_SPEED:
        return [VarType.INT, VarType.FLOAT]
    elif keyword_type == KeywordType.OLED_SHOW_INT:
        return [VarType.INT, VarType.INT, VarType.INT, VarType.INT]
    elif keyword_type == KeywordType.PRINT:
        return [VarType.INT]
    else:
        return []

class SemanticAnalyzer:
    def __init__(self, symbol_table: SymbolTable):
        self.symbol_table = symbol_table
        self.info_box = []

    def examine(self, ast: Program):
        # 1. 检查 main 函数
        if "main" not in self.symbol_table.stack[0]:
            raise Exception("No main function found")
        main_func = self.symbol_table.stack[0]["main"]
        if not (main_func["type"] == "fn" and len(main_func["params"]) == 0 and main_func["return_type"] == VarType.VOID):
            raise Exception("No valid main function found")

        # 2. 遍历全局声明
        for decl in ast.global_decls:
            if isinstance(decl, VarDecl):
                self._check_vardecl(decl, True)
            elif isinstance(decl, FuncDecl):
                self._check_funcdecl(decl)

    def _check_vardecl(self, decl: VarDecl, check_init_expr = False):
        # 当变量声明中同时指定了类型和初始值时，需要检测两者类型是否匹配，如果不匹配，添加as语句
        if decl.init_expr is not None:
            if check_init_expr:
                decl.init_expr = self._check_expr(decl.init_expr)
            decl_type = decl.var_type
            init_type = get_expr_type(decl.init_expr, self.symbol_table)
            if decl_type != init_type:
                self.info_box.append(f"[hint] implicit cast {init_type.name} -> {decl_type.name} in variable declaration of {decl.var_name}")
                as_stmt = BinaryExpr(KeywordType.AS, decl.init_expr, TypeCastExpr(decl_type))
                decl.init_expr = as_stmt

    def _check_funcdecl(self, decl: FuncDecl):
        """
        1. 如果函数的返回值不是VOID，则需要确保函数的每个branch都有有效的返回值，并在恰达的地方插入as语句
        2. 确保break语句只出现在循环（while, loop）中
        3. 检查函数调用/系统调用的参数数量和类型是否匹配
        4. 检查表达式中是否存在隐式转换，如果存在，则输出提示并添加as语句
        """
        must_return = decl.return_type != VarType.VOID
        has_return = self._check_stmt_block(decl.body, decl.return_type, in_loop=False)
        if must_return and not has_return:
            raise Exception(f"Function {decl.name} must return {decl.return_type.name}")

    def _check_stmt_block(self, stmts: list, expected_return: VarType, in_loop: bool) -> bool:
        has_return = False
        for stmt in stmts:
            if isinstance(stmt, ReturnStmt):
                if expected_return != VarType.VOID:
                    if stmt.expr is not None:
                        stmt.expr = self._check_expr(stmt.expr)
                        expr_type = get_expr_type(stmt.expr, self.symbol_table)
                        if expr_type != expected_return:
                            self.info_box.append(f"[hint] implicit cast {expr_type.name} -> {expected_return} in return")
                            stmt.expr = BinaryExpr(KeywordType.AS, stmt.expr, TypeCastExpr(expected_return))
                    else:
                        if expected_return != VarType.VOID:
                            raise Exception("Return must provide value")
                    has_return = True
                else:
                    if stmt.expr is not None:
                        raise Exception("Expected void return")
                    has_return = True

            elif isinstance(stmt, BreakStmt):
                if not in_loop:
                    raise Exception("Break statement not inside a loop")

            elif isinstance(stmt, IfStmt):
                stmt.cond_expr = self._check_expr(stmt.cond_expr)
                cond_type = get_expr_type(stmt.cond_expr, self.symbol_table)
                if cond_type != VarType.INT:
                    self.info_box.append(f"[hint] implicit cast {cond_type.name} -> int in if condition")
                    stmt.cond_expr = BinaryExpr(KeywordType.AS, stmt.cond_expr, TypeCastExpr(VarType.INT))
                then_has = self._check_stmt_block(stmt.then_stmt, expected_return, in_loop)
                else_has = self._check_stmt_block(stmt.else_stmt, expected_return, in_loop) if stmt.else_stmt else False
                if then_has and else_has:
                    has_return = True

            elif isinstance(stmt, WhileStmt):
                stmt.cond_expr = self._check_expr(stmt.cond_expr)
                cond_type = get_expr_type(stmt.cond_expr, self.symbol_table)
                if cond_type != VarType.INT:
                    self.info_box.append(f"[hint] implicit cast {cond_type.name} -> bool in if condition")
                    stmt.cond_expr = BinaryExpr(KeywordType.AS, stmt.cond_expr, TypeCastExpr(VarType.INT))
                self._check_stmt_block(stmt.body, expected_return, in_loop=True)

            elif isinstance(stmt, LoopStmt):
                self._check_stmt_block(stmt.body, expected_return, in_loop=True)

            elif isinstance(stmt, VarDecl):
                self._check_vardecl(stmt, True)

            elif isinstance(stmt, Expr):
                stmt = self._check_expr(stmt)

        return has_return

    def _check_expr(self, expr: Expr) -> Expr:
        if isinstance(expr, BinaryExpr):
            expr.left = self._check_expr(expr.left)
            expr.right = self._check_expr(expr.right)

            lt = get_expr_type(expr.left, self.symbol_table)
            rt = get_expr_type(expr.right, self.symbol_table)

            if expr.op in (KeywordType.PLUS, KeywordType.MINUS, KeywordType.MULTIPLY, KeywordType.DIVIDE):
                if lt == VarType.INT and rt == VarType.FLOAT:
                    self.info_box.append("[hint] implicit cast int -> float on left side")
                    expr.left = BinaryExpr(KeywordType.AS, expr.left, TypeCastExpr(VarType.FLOAT))
                elif lt == VarType.FLOAT and rt == VarType.INT:
                    self.info_box.append("[hint] implicit cast int -> float on right side")
                    expr.right = BinaryExpr(KeywordType.AS, expr.right, TypeCastExpr(VarType.FLOAT))

            elif expr.op in (KeywordType.ASSIGNMENT, KeywordType.ADD_ASSIGNMENT, KeywordType.SUBTRACT_ASSIGNMENT,
                             KeywordType.MULTIPLY_ASSIGNMENT, KeywordType.DIVIDE_ASSIGNMENT):
                if lt != rt:
                    if lt == VarType.FLOAT and rt == VarType.INT:
                        self.info_box.append("[hint] implicit cast int -> float in assignment")
                        expr.right = BinaryExpr(KeywordType.AS, expr.right, TypeCastExpr(VarType.FLOAT))
                    elif lt == VarType.INT and rt == VarType.FLOAT:
                        self.info_box.append("[hint] implicit cast float -> int in assignment")
                        expr.right = BinaryExpr(KeywordType.AS, expr.right, TypeCastExpr(VarType.INT))
                    else:
                        raise Exception(f"Incompatible assignment {lt.name} -> {rt.name}")
                if not isinstance(expr.left, VarExpr):
                    raise Exception("Invalid left-hand side of assignment")
                elif expr.left.symbol_info["is_const"] == True:
                    raise Exception("Cannot assign to constant")

            elif expr.op in (KeywordType.LESS, KeywordType.LESS_EQUAL, KeywordType.GREATER, KeywordType.GREATER_EQUAL):
                if lt != rt:
                    if lt == VarType.FLOAT and rt == VarType.INT:
                        self.info_box.append("[hint] implicit cast int -> float in comparison")
                        expr.left = BinaryExpr(KeywordType.AS, expr.left, TypeCastExpr(VarType.FLOAT))
                    elif lt == VarType.INT and rt == VarType.FLOAT:
                        self.info_box.append("[hint] implicit cast int -> float in comparison")
                        expr.right = BinaryExpr(KeywordType.AS, expr.right, TypeCastExpr(VarType.FLOAT))


            elif expr.op in (KeywordType.MODULO, KeywordType.BIT_AND, KeywordType.BIT_OR, KeywordType.BIT_XOR, KeywordType.LEFT_SHIFT, KeywordType.RIGHT_SHIFT):
                if lt != VarType.INT or rt != VarType.INT:
                    raise Exception(f"Invalid operand types for {expr.op.name}: {lt.name}, {rt.name}")

            elif expr.op in (KeywordType.EQUAL, KeywordType.NOT_EQUAL):
                if lt != rt:
                    raise Exception(f"Incompatible comparison {lt.name} - {rt.name}")

        elif isinstance(expr, UnaryExpr):
            expr.operand = self._check_expr(expr.operand)

        elif isinstance(expr, FuncCallExpr):
            # 普通函数调用
            func_info = self.symbol_table.lookup(expr.func)
            if func_info["type"] != "fn":
                raise Exception(f"{expr.func} is not a function")
            if len(expr.args) != len(func_info["params"]):
                raise Exception(f"Function {expr.func} expects {len(func_info['params'])} args, got {len(expr.args)}")

            for i, (arg, param_type) in enumerate(zip(expr.args, func_info["params"])):
                arg = self._check_expr(arg)
                arg_type = get_expr_type(arg, self.symbol_table)
                if arg_type != param_type:
                    self.info_box.append(f"[hint] implicit cast {arg_type.name} -> {param_type.name} in function arg {i} of {expr.func}")
                    expr.args[i] = BinaryExpr(KeywordType.AS, arg, TypeCastExpr(param_type))

        elif isinstance(expr, SysCallExpr):
            # 系统调用
            if len(expr.args) != len(get_syscall_arg(expr.func)):
                raise Exception(f"System call {expr.func.name} expects {len(get_syscall_arg(expr.func))} args, got {len(expr.args)}")

            for i, (arg, param_type) in enumerate(zip(expr.args, get_syscall_arg(expr.func))):
                arg = self._check_expr(arg)
                arg_type = get_expr_type(arg, self.symbol_table)
                if arg_type != param_type:
                    self.info_box.append(f"[hint] implicit cast {arg_type.name} -> {param_type.name} in system call arg {i} of {expr.func.name}")
                    expr.args[i] = BinaryExpr(KeywordType.AS, arg, TypeCastExpr(param_type))

        # 常量折叠
        folded = SemanticAnalyzer.eval_const_expr(expr)
        if folded is not None:
            expr = LiteralExpr(folded)
        return expr


    @staticmethod
    def eval_const_expr(expr: Expr) -> int | float | None:
        if isinstance(expr, LiteralExpr):
            return expr.value
        elif isinstance(expr, UnaryExpr):
            val = SemanticAnalyzer.eval_const_expr(expr.operand)
            if val is None:
                return None
            if expr.op == KeywordType.MINUS:
                return -val
            elif expr.op == KeywordType.NOT:
                return not val
            elif expr.op == KeywordType.BIT_NOT:
                return ~val
            else:
                return None

        elif isinstance(expr, BinaryExpr):
            if expr.op == KeywordType.AS:
                left = SemanticAnalyzer.eval_const_expr(expr.left)
                if left is None:
                    return None
                if isinstance(expr.right, TypeCastExpr):
                    type = expr.right.var_type
                else:
                    raise Exception("Invalid type cast")
                if type == VarType.INT:
                    return int(left)
                elif type == VarType.FLOAT:
                    return float(left)
            else:
                left = SemanticAnalyzer.eval_const_expr(expr.left)
                right = SemanticAnalyzer.eval_const_expr(expr.right)
                if left is None or right is None:
                    return None
                if expr.op == KeywordType.PLUS:
                    return left + right
                elif expr.op == KeywordType.MINUS:
                    return left - right
                elif expr.op == KeywordType.MULTIPLY:
                    return left * right
                elif expr.op == KeywordType.DIVIDE:
                    return left / right
                elif expr.op == KeywordType.MODULO:
                    return left % right
                elif expr.op == KeywordType.LESS:
                    return left < right
                elif expr.op == KeywordType.LESS_EQUAL:
                    return left <= right
                elif expr.op == KeywordType.GREATER:
                    return left > right
                elif expr.op == KeywordType.GREATER_EQUAL:
                    return left >= right
                elif expr.op == KeywordType.EQUAL:
                    return left == right
                elif expr.op == KeywordType.NOT_EQUAL:
                    return left!= right
                elif expr.op == KeywordType.AND:
                    return left and right
                elif expr.op == KeywordType.OR:
                    return left or right
                elif expr.op == KeywordType.BIT_AND:
                    return left & right
                elif expr.op == KeywordType.BIT_OR:
                    return left | right
                elif expr.op == KeywordType.BIT_XOR:
                    return left ^ right
                elif expr.op == KeywordType.LEFT_SHIFT:
                    return left << right
                elif expr.op == KeywordType.RIGHT_SHIFT:
                    return left >> right
                else:
                    return None

        else:
            return None

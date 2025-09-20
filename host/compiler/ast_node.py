from typing import List
from .lexer import KeywordType, VarType

# AST node classes
class Node:
    def json(self) -> dict:
        pass

class Program(Node):
    def __init__(self, global_decls : List[Node]):
        self.global_decls = global_decls

    def json(self):
        return {
            "global_decls": [decl.json() for decl in self.global_decls]
        }

class Expr(Node):
    pass

class UnaryExpr(Expr):
    def __init__(self, op : KeywordType, operand : Expr):
        self.op = op
        self.operand = operand
    def json(self):
        return {
            "type": "unary",
            "op": self.op.name,
            "operand": self.operand.json()
        }

class TypeCastExpr(Expr):
    def __init__(self, var_type : VarType):
        self.var_type = var_type

    def json(self):
        return {
            "type": "type_cast",
            "var_type": self.var_type.name
        }

class BinaryExpr(Expr):
    def __init__(self, op : KeywordType, left: Expr, right: Expr):
        self.left = left
        self.op = op
        self.right = right
    def json(self):
        return {
            "type": "binary",
            "op": self.op.name,
            "left": self.left.json(),
            "right": self.right.json()
        }

class LiteralExpr(Expr):
    def __init__(self, value):
        self.value = value
    def json(self):
        return {"type": "literal", "value": self.value}

class VarExpr(Expr):
    def __init__(self, name: str, symbol_info: dict):
        self.name = name
        self.symbol_info = symbol_info
    def json(self):
        return {
            "type": "var",
            "name": self.name,
            "var_type": self.symbol_info["var_type"].name,
        }

class FuncCallExpr(Expr):
    def __init__(self, func: str, info : dict):
        self.func = func
        self.info = info
        self.args = []

    def add_arg(self, arg : Expr):
        self.args.append(arg)

    def json(self):
        return {
            "type": "func_call",
            "func": self.func,
            "args": [a.json() for a in self.args]
        }

class SysCallExpr(Expr):
    def __init__(self, func: KeywordType):
        self.func = func
        self.args = []

    def json(self):
        return {
            "type": "sys_call",
            "func": self.func.name,
            "args": [a.json() for a in self.args]
        }


class IfStmt(Node):
    def __init__(self, cond_expr : Expr, then_stmt : list, else_stmt : list):
        self.cond_expr = cond_expr
        self.then_stmt = then_stmt
        self.else_stmt = else_stmt  # None 或 下一个IfStmt

    def json(self):
        return {
            "type": "if_stmt",
            "cond_expr": self.cond_expr.json(),
            "then_stmt": [stmt.json() for stmt in self.then_stmt],
            "else_stmt": [stmt.json() for stmt in self.else_stmt]
        }

class WhileStmt(Node):
    def __init__(self, cond_expr : Expr, body : list):
        self.cond_expr = cond_expr
        self.body = body

    def json(self):
            return {
                "type": "while_stmt",
                "cond_expr": self.cond_expr.json(),
                "body": [stmt.json() for stmt in self.body]
            }

class LoopStmt(Node):
    def __init__(self, body : list):
        self.body = body

    def json(self):
        return {
            "type": "loop_stmt",
            "body": [stmt.json() for stmt in self.body]
        }

class ReturnStmt(Node):
    def __init__(self, expr : Expr = None):
        self.expr = expr

    def json(self):
        return {
            "type": "return_stmt",
            "expr": self.expr.json() if self.expr is not None else None
        }

class BreakStmt(Node):
    def __init__(self):
        pass

    def json(self):
        return {
            "type": "break_stmt"
        }

class VarDecl(Node):
    def __init__(self, var_type : VarType, var_name : str, is_const : bool, init_expr : Expr):
        self.var_type = var_type
        self.var_name = var_name
        self.is_const = is_const
        self.init_expr = init_expr

    def json(self):
        return {
            "type": "var_decl",
            "var_type": self.var_type.name,
            "var_name": self.var_name,
            "is_const": self.is_const,
            "init_expr": self.init_expr.json() if self.init_expr is not None else None
        }

class Param(Node):
    def __init__(self, var_type : VarType, var_name : str, is_const : bool):
        self.var_type = var_type
        self.var_name = var_name
        self.is_const = is_const

    def json(self):
        return {
            "var_type": self.var_type.name,
            "var_name": self.var_name
        }

class FuncDecl(Node):
    def __init__(self, name : str, params : List[Param], return_type : VarType, body : List[Node], local_var_num : int):
        self.name = name
        self.params = params
        self.return_type = return_type
        self.body = body
        self.local_var_num = local_var_num

    def json(self):
        return {
            "type": "func_decl",
            "name": self.name,
            "params": [param.json() for param in self.params],
            "return_type": self.return_type.name,
            "body": [stmt.json() for stmt in self.body],
            "local_var_num": self.local_var_num
        }

from enum import auto, Enum

class TokenType(Enum):
    IDENTIFIER = auto()
    KEYWORD = auto()
    LITERAL = auto()

class KeywordType(Enum):
    # 函数
    FN = auto()
    ARROW = auto()  # ->
    RETURN = auto()
    # 变量
    LET = auto()
    CONST = auto()
    COLON = auto()  # :
    INT = auto()
    FLOAT = auto()
    ASSIGNMENT = auto()  # =
    AS = auto()
    # 控制流
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    LOOP = auto()
    BREAK = auto()
    # 运算
    EQUAL = auto()  # ==
    NOT_EQUAL = auto()  # !=
    GREATER = auto()  # >
    LESS = auto()  # <
    GREATER_EQUAL = auto()  # >=
    LESS_EQUAL = auto()  # <=
    AND = auto()  # &&
    OR = auto()  # ||
    NOT = auto()  # !
    PLUS = auto()  # +
    MINUS = auto()  # -
    MULTIPLY = auto()  # *
    DIVIDE = auto()  # /
    MODULO = auto()  # %
    ADD_ASSIGNMENT = auto()  # +=
    SUBTRACT_ASSIGNMENT = auto()  # -=
    MULTIPLY_ASSIGNMENT = auto()  # *=
    DIVIDE_ASSIGNMENT = auto()  # /=
    MODULO_ASSIGNMENT = auto()  # %=
    BIT_AND = auto()  # &
    BIT_OR = auto()  # |
    BIT_XOR = auto()  # ^
    BIT_NOT = auto()  # ~
    BIT_AND_ASSIGNMENT = auto()  # &=
    BIT_OR_ASSIGNMENT = auto()  # |=
    BIT_XOR_ASSIGNMENT = auto()  # ^=
    LEFT_SHIFT = auto()  # <<
    RIGHT_SHIFT = auto()  # >>
    LEFT_SHIFT_ASSIGNMENT = auto()  # <<=
    RIGHT_SHIFT_ASSIGNMENT = auto()  # >>=
    # 系统调用
    DELAY = auto()
    RESET = auto()
    WAIT = auto()
    WAIT_JOINT = auto()
    MOV_JOINT = auto()
    SET_JOINT = auto()
    READ_JOINT = auto()
    MOV_ORTH_COORD = auto()
    SET_ORTH_COORD = auto()
    MOV_JOINT_COORD = auto()
    SET_JOINT_COORD = auto()
    GRIPPER_OPEN = auto()
    GRIPPER_CLOSE = auto()
    SET_JOINT_SPEED = auto()
    OLED_SHOW_INT = auto()
    # 其他
    LEFT_PARENTHESIS = auto()  # (
    RIGHT_PARENTHESIS = auto()  # )
    LEFT_BRACE = auto()  # {
    RIGHT_BRACE = auto()  # }.
    COMMA = auto()  # ,
    SEMICOLON = auto()  # ;

    # 调试用
    PRINT = auto()

class VarType(Enum):
    AUTO = auto()
    VOID = auto()
    INT = auto()
    FLOAT = auto()

class IdentifierType(Enum):
    VARIABLE = auto()
    FUNCTION = auto()

class Token:
    token_type : TokenType
    line : int

    # id 使用
    name : str
    hash : int
    id_type : IdentifierType

    # 关键字使用
    keyword_type : KeywordType

    # 字面量使用
    literal_type : VarType
    int_value : int
    float_value : float

    @staticmethod
    def create_identifier(name : str, line : int):
        token = Token()
        token.token_type = TokenType.IDENTIFIER
        token.name = name
        token.hash = hash(name)
        token.line = line
        return token

    @staticmethod
    def create_keyword(value : KeywordType, line : int):
        token = Token()
        token.token_type = TokenType.KEYWORD
        token.keyword_type = value
        token.line = line
        return token


    @staticmethod
    def create_int(value : int, line : int):
        token = Token()
        token.token_type = TokenType.LITERAL
        token.literal_type = VarType.INT
        token.int_value = value
        token.line = line
        return token

    @staticmethod
    def create_float(value : float, line : int):
        token = Token()
        token.token_type = TokenType.LITERAL
        token.literal_type = VarType.FLOAT
        token.float_value = value
        token.line = line
        return token

    """
    @staticmethod
    def create_bool(value : bool, line : int):
        token = Token()
        token.token_type = TokenType.LITERAL
        token.literal_type = VarType.BOOL
        token.bool_value = value
        token.line = line
        return token
    """

    def __str__(self):
        if self.token_type == TokenType.IDENTIFIER:
            return f"Identifier: {self.name}"
        elif self.token_type == TokenType.KEYWORD:
            return f"Keyword: {self.keyword_type.name}"
        elif self.token_type == TokenType.LITERAL:
            if self.literal_type == VarType.INT:
                return f"Literal: {self.int_value}"
            elif self.literal_type == VarType.FLOAT:
                return f"Literal: {self.float_value}"
            #elif self.literal_type == VarType.BOOL:
                #return f"Literal: {self.bool_value}"

keyword_map = {
    'fn' : KeywordType.FN,
    'return' : KeywordType.RETURN,
    'let' : KeywordType.LET,
    'const' : KeywordType.CONST,
    'int' : KeywordType.INT,
    'float' : KeywordType.FLOAT,
    #'bool' : KeywordType.BOOL,
    'as' : KeywordType.AS,
    'if' : KeywordType.IF,
    'else' : KeywordType.ELSE,
    'while' : KeywordType.WHILE,
    'loop' : KeywordType.LOOP,
    'break' : KeywordType.BREAK,
    'delay' : KeywordType.DELAY,
    'reset' : KeywordType.RESET,
    'wait' : KeywordType.WAIT,
    'wait_joint' : KeywordType.WAIT_JOINT,
    'mov_joint' : KeywordType.MOV_JOINT,
    'set_joint' : KeywordType.SET_JOINT,
    'read_joint' : KeywordType.READ_JOINT,
    'mov_orth_coord' : KeywordType.MOV_ORTH_COORD,
    'set_orth_coord' : KeywordType.SET_ORTH_COORD,
    'mov_joint_coord' : KeywordType.MOV_JOINT_COORD,
    'set_joint_coord' : KeywordType.SET_JOINT_COORD,
    'gripper_open' : KeywordType.GRIPPER_OPEN,
    'gripper_close' : KeywordType.GRIPPER_CLOSE,
    'set_joint_speed' : KeywordType.SET_JOINT_SPEED,
    'oled_show_int' : KeywordType.OLED_SHOW_INT,

    # 调试用
    'print' : KeywordType.PRINT,
}


def tokenize(code : str) -> list:
    tokens = []
    i = 0
    line = 1
    len_code = len(code)
    while i < len_code:
        ch = code[i]
        if ch == ' ' or ch == '\t':
            pass    # 忽略空格
        elif ch == '\n':
            line += 1
        elif ch == '/':
            if i < len_code - 1 and code[i+1] == '/':
                # 跳过单行注释
                i += 2
                while i < len_code and code[i] != '\n':
                    if code[i] == '\n':
                        line += 1
                    i += 1
            elif i < len_code - 1 and code[i+1] == '*':
                # 跳过多行注释
                i += 2
                while i < len_code - 1:
                    if code[i] == '\n':
                        line += 1
                    if code[i] == '*' and code[i+1] == '/':
                        i += 2
                        break
                    i += 1
            elif i < len_code - 1 and code[i+1] == '=':
                # 解析 /=
                tokens.append(Token.create_keyword(KeywordType.DIVIDE_ASSIGNMENT, line))
                i += 1
            else:
                # 解析除号
                tokens.append(Token.create_keyword(KeywordType.DIVIDE, line))
        elif ch.isdigit():
            # 解析数字
            token, i = parse_number(code, i, line)
            tokens.append(token)
            i -= 1
        elif ch.isalpha() or ch == '_':
            # 解析符号
            # 读取字符串
            name = ''
            while 1:
                name += code[i]
                if i + 1< len_code and (code[i + 1].isalpha() or code[i + 1].isdigit() or code[i + 1] == '_'):
                    i += 1
                else:
                    break
            # 关键字
            if name in keyword_map:
                tokens.append(Token.create_keyword(keyword_map[name], line))
            else:
                tokens.append(Token.create_identifier(name, line))
        elif ch == '-':
            if i < len_code - 1 and code[i+1] == '>':
                # 解析 ->
                tokens.append(Token.create_keyword(KeywordType.ARROW, line))
                i += 1
            elif i < len_code - 1 and code[i+1] == '=':
                # 解析 -=
                tokens.append(Token.create_keyword(KeywordType.SUBTRACT_ASSIGNMENT, line))
                i += 1
            else:
                # 解析减号
                tokens.append(Token.create_keyword(KeywordType.MINUS, line))
        elif ch == ':':
            tokens.append(Token.create_keyword(KeywordType.COLON, line))
        elif ch == '=':
            if i < len_code - 1 and code[i+1] == '=':
                # 解析 ==
                tokens.append(Token.create_keyword(KeywordType.EQUAL, line))
                i += 1
            else:
                # 解析赋值符号
                tokens.append(Token.create_keyword(KeywordType.ASSIGNMENT, line))
        elif ch == '!':
            if i < len_code - 1 and code[i+1] == '=':
                # 解析 !=
                tokens.append(Token.create_keyword(KeywordType.NOT_EQUAL, line))
                i += 1
            else:
                tokens.append(Token.create_keyword(KeywordType.NOT, line))
        elif ch == '&':
            if i < len_code - 1 and code[i+1] == '&':
                # 解析 &&
                tokens.append(Token.create_keyword(KeywordType.AND, line))
                i += 1
            elif i < len_code - 1 and code[i+1] == '=':
                # 解析 &=
                tokens.append(Token.create_keyword(KeywordType.BIT_AND_ASSIGNMENT, line))
                i += 1
            else:
                # 解析位与
                tokens.append(Token.create_keyword(KeywordType.BIT_AND, line))
        elif ch == '|':
            if i < len_code - 1 and code[i+1] == '|':
                # 解析 ||
                tokens.append(Token.create_keyword(KeywordType.OR, line))
                i += 1
            elif i < len_code - 1 and code[i+1] == '=':
                # 解析 |=
                tokens.append(Token.create_keyword(KeywordType.BIT_OR_ASSIGNMENT, line))
                i += 1
            else:
                # 解析位或
                tokens.append(Token.create_keyword(KeywordType.BIT_OR, line))
        elif ch == '+':
            if i < len_code - 1 and code[i+1] == '=':
                # 解析 +=
                tokens.append(Token.create_keyword(KeywordType.ADD_ASSIGNMENT, line))
                i += 1
            else:
                # 解析加号
                tokens.append(Token.create_keyword(KeywordType.PLUS, line))
        elif ch == '-':
            if i < len_code - 1 and code[i+1] == '=':
                # 解析 -=
                tokens.append(Token.create_keyword(KeywordType.SUBTRACT_ASSIGNMENT, line))
                i += 1
            else:
                # 解析减号
                tokens.append(Token.create_keyword(KeywordType.MINUS, line))
        elif ch == '*':
            if i < len_code - 1 and code[i+1] == '=':
                # 解析 *=
                tokens.append(Token.create_keyword(KeywordType.MULTIPLY_ASSIGNMENT, line))
                i += 1
            else:
                # 解析乘号
                tokens.append(Token.create_keyword(KeywordType.MULTIPLY, line))
        elif ch == '%':
            if i < len_code - 1 and code[i+1] == '=':
                # 解析 %=
                tokens.append(Token.create_keyword(KeywordType.MODULO_ASSIGNMENT, line))
                i += 1
            else:
                # 解析取模符号
                tokens.append(Token.create_keyword(KeywordType.MODULO, line))
        elif ch == '^':
            if i < len_code - 1 and code[i+1] == '=':
                # 解析 ^=
                tokens.append(Token.create_keyword(KeywordType.BIT_XOR_ASSIGNMENT, line))
                i += 1
            else:
                # 解析异或
                tokens.append(Token.create_keyword(KeywordType.BIT_XOR, line))
        elif ch == '~':
            # 解析位取反
            tokens.append(Token.create_keyword(KeywordType.BIT_NOT, line))
        elif ch == '<':
            if i < len_code - 1 and code[i+1] == '<':
                if i < len_code - 2 and code[i+2] == '=':
                    # 解析 <<=
                    tokens.append(Token.create_keyword(KeywordType.LEFT_SHIFT_ASSIGNMENT, line))
                    i += 2
                else:
                    # 解析 <<
                    tokens.append(Token.create_keyword(KeywordType.LEFT_SHIFT, line))
                    i += 1
            elif i < len_code - 1 and code[i+1] == '=':
                # 解析 <=
                tokens.append(Token.create_keyword(KeywordType.LESS_EQUAL, line))
                i += 1
            else:
                # 解析小于号
                tokens.append(Token.create_keyword(KeywordType.LESS, line))
        elif ch == '>':
            if i < len_code - 1 and code[i+1] == '>':
                if i < len_code - 2 and code[i+2] == '=':
                    # 解析 >>=
                    tokens.append(Token.create_keyword(KeywordType.RIGHT_SHIFT_ASSIGNMENT, line))
                    i += 2
                else:
                    # 解析 >>
                    tokens.append(Token.create_keyword(KeywordType.RIGHT_SHIFT, line))
                    i += 1
            else:
                # 解析大于号
                tokens.append(Token.create_keyword(KeywordType.GREATER, line))
        elif ch == '(':
            tokens.append(Token.create_keyword(KeywordType.LEFT_PARENTHESIS, line))
        elif ch == ')':
            tokens.append(Token.create_keyword(KeywordType.RIGHT_PARENTHESIS, line))
        elif ch == '{':
            tokens.append(Token.create_keyword(KeywordType.LEFT_BRACE, line))
        elif ch == '}':
            tokens.append(Token.create_keyword(KeywordType.RIGHT_BRACE, line))
        elif ch == ',':
            tokens.append(Token.create_keyword(KeywordType.COMMA, line))
        elif ch == ';':
            tokens.append(Token.create_keyword(KeywordType.SEMICOLON, line))
        else:
            raise Exception(f"Unexpected character '{ch}' at line {line}")

        i += 1

    return tokens

def parse_number(code: str, start_index: int, line : int) -> (Token, int):
    i = start_index
    len_code = len(code)

    # 处理 0x / 0b / 0o 前缀
    if code[i] == '0' and i + 1 < len_code:
        if code[i+1] in ('x', 'X'):   # 十六进制
            i += 2
            start = i
            if i >= len_code or not (code[i].isdigit() or ('a' <= code[i].lower() <= 'f')):
                raise Exception(f"Invalid hex literal at line {line}")
            while i < len_code and code[i].isdigit() or ('a' <= code[i].lower() <= 'f'):
                i += 1
            value_str = code[start:i]
            value = int(value_str, 16)
            return Token.create_int(value, line), i

        elif code[i+1] in ('b', 'B'):  # 二进制
            i += 2
            start = i
            if i >= len_code or not (code[i] in ('0', '1')):
                raise Exception(f"Invalid binary literal at line {line}")
            while i < len_code and code[i] in ('0', '1'):
                i += 1
            value_str = code[start:i]
            value = int(value_str, 2)
            return Token.create_int(value, line), i

        elif code[i+1] in ('o', 'O'):  # 八进制
            i += 2
            start = i
            if i >= len_code or not ('0' <= code[i] <= '7'):
                raise Exception(f"Invalid octal literal at line {line}")
            while i < len_code and '0' <= code[i] <= '7':
                i += 1
            value_str = code[start:i]
            value = int(value_str, 8)
            return Token.create_int(value, line), i
        # 否则继续按十进制走

    # 十进制 / 浮点数
    start = i
    has_dot = False
    while i < len_code and (code[i].isdigit() or code[i] == '.'):
        if code[i] == '.':
            if has_dot:  # 已经有一个点，再遇到点就停
                break
            has_dot = True
        i += 1

    value_str = code[start:i]

    if has_dot:
        try:
            value = float(value_str)
        except ValueError:
            raise Exception(f"Invalid float literal '{value_str}' at line {line}")
        return Token.create_float(value, line), i
    else:
        value = int(value_str, 10)
        return Token.create_int(value, line), i

def keywordtype_to_vartype(keyword_type : KeywordType) -> VarType:
    if keyword_type == KeywordType.INT:
        return VarType.INT
    elif keyword_type == KeywordType.FLOAT:
        return VarType.FLOAT
    #elif keyword_type == KeywordType.BOOL:
        #return VarType.BOOL
    else:
        raise Exception(f"Invalid keyword type {keyword_type}")
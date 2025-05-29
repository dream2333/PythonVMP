"""
PyVM词法分析器
将Python源代码转换为token序列
"""

import re
from enum import Enum, auto
from typing import List, NamedTuple, Optional, Iterator
from dataclasses import dataclass


class TokenType(Enum):
    """Token类型枚举"""
    # 字面量
    NUMBER = auto()
    STRING = auto()
    BOOLEAN = auto()
    
    # 标识符和关键字
    IDENTIFIER = auto()
    KEYWORD = auto()
    
    # 运算符
    PLUS = auto()           # +
    MINUS = auto()          # -
    MULTIPLY = auto()       # *
    DIVIDE = auto()         # /
    MODULO = auto()         # %
    
    # 比较运算符
    EQUAL = auto()          # ==
    NOT_EQUAL = auto()      # !=
    LESS_THAN = auto()      # <
    LESS_EQUAL = auto()     # <=
    GREATER_THAN = auto()   # >
    GREATER_EQUAL = auto()  # >=
    
    # 赋值
    ASSIGN = auto()         # =
    
    # 分隔符
    LPAREN = auto()         # (
    RPAREN = auto()         # )
    COLON = auto()          # :
    COMMA = auto()          # ,
    
    # 其他
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    EOF = auto()
    
    # 错误
    ERROR = auto()


@dataclass
class Token:
    """Token数据类"""
    type: TokenType
    value: str
    line: int
    column: int
    
    def __str__(self):
        return f"Token({self.type.name}, '{self.value}', {self.line}:{self.column})"


class LexerError(Exception):
    """词法分析错误"""
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"词法错误 {line}:{column}: {message}")


class Lexer:
    """词法分析器"""
    
    # Python关键字
    KEYWORDS = {
        'if', 'else', 'elif', 'while', 'for', 'def', 'return',
        'True', 'False', 'and', 'or', 'not', 'in', 'is',
        'class', 'import', 'from', 'as', 'try', 'except',
        'finally', 'with', 'pass', 'break', 'continue'
    }
    
    # 运算符映射
    OPERATORS = {
        '+': TokenType.PLUS,
        '-': TokenType.MINUS,
        '*': TokenType.MULTIPLY,
        '/': TokenType.DIVIDE,
        '%': TokenType.MODULO,
        '==': TokenType.EQUAL,
        '!=': TokenType.NOT_EQUAL,
        '<': TokenType.LESS_THAN,
        '<=': TokenType.LESS_EQUAL,
        '>': TokenType.GREATER_THAN,
        '>=': TokenType.GREATER_EQUAL,
        '=': TokenType.ASSIGN,
    }
    
    # 分隔符映射
    DELIMITERS = {
        '(': TokenType.LPAREN,
        ')': TokenType.RPAREN,
        ':': TokenType.COLON,
        ',': TokenType.COMMA,
    }
    
    def __init__(self, source: str):
        self.source = source
        self.lines = source.split('\n')
        self.pos = 0
        self.line = 1
        self.column = 1
        self.indent_stack = [0]  # 缩进栈
        self.at_line_start = True
        
    def tokenize(self) -> List[Token]:
        """对源代码进行词法分析"""
        tokens = []
        
        try:
            while self.pos < len(self.source):
                token = self._next_token()
                if token:
                    tokens.append(token)
            
            # 处理文件结尾的DEDENT
            while len(self.indent_stack) > 1:
                self.indent_stack.pop()
                tokens.append(Token(TokenType.DEDENT, '', self.line, self.column))
            
            # 添加EOF token
            tokens.append(Token(TokenType.EOF, '', self.line, self.column))
            
        except LexerError as e:
            # 添加错误token
            tokens.append(Token(TokenType.ERROR, str(e), e.line, e.column))
        
        return tokens
    
    def _next_token(self) -> Optional[Token]:
        """获取下一个token"""
        self._skip_whitespace()
        
        if self.pos >= len(self.source):
            return None
        
        # 处理行首缩进
        if self.at_line_start:
            return self._handle_indentation()
        
        char = self.source[self.pos]
        
        # 注释
        if char == '#':
            self._skip_comment()
            return self._next_token()
        
        # 换行符
        if char == '\n':
            self.at_line_start = True
            return self._make_token(TokenType.NEWLINE, char)
        
        # 字符串
        if char in ('"', "'"):
            return self._read_string()
        
        # 数字
        if char.isdigit():
            return self._read_number()
        
        # 标识符或关键字
        if char.isalpha() or char == '_':
            return self._read_identifier()
        
        # 双字符运算符
        if self.pos + 1 < len(self.source):
            two_char = self.source[self.pos:self.pos+2]
            if two_char in self.OPERATORS:
                token = Token(self.OPERATORS[two_char], two_char, 
                             self.line, self.column)
                self._advance(2)
                return token
        
        # 单字符运算符和分隔符
        if char in self.OPERATORS:
            return self._make_token(self.OPERATORS[char], char)
        
        if char in self.DELIMITERS:
            return self._make_token(self.DELIMITERS[char], char)
        
        # 未知字符
        raise LexerError(f"未识别的字符: '{char}'", self.line, self.column)
    
    def _handle_indentation(self) -> Optional[Token]:
        """处理行首缩进"""
        self.at_line_start = False
        
        # 跳过空行
        if self._is_blank_line():
            return None
        
        # 计算缩进级别
        indent_level = 0
        start_pos = self.pos
        
        while (self.pos < len(self.source) and 
               self.source[self.pos] in (' ', '\t')):
            if self.source[self.pos] == ' ':
                indent_level += 1
            else:  # tab
                indent_level += 8  # tab = 8个空格
            self.pos += 1
        
        # 检查是否为空行或注释行
        if (self.pos >= len(self.source) or 
            self.source[self.pos] == '\n' or 
            self.source[self.pos] == '#'):
            return None
        
        current_indent = self.indent_stack[-1]
        
        if indent_level > current_indent:
            # 缩进增加
            self.indent_stack.append(indent_level)
            self.column += indent_level
            return Token(TokenType.INDENT, '', self.line, start_pos + 1)
        
        elif indent_level < current_indent:
            # 缩进减少
            if indent_level not in self.indent_stack:
                raise LexerError("缩进不匹配", self.line, self.column)
            
            while self.indent_stack[-1] > indent_level:
                self.indent_stack.pop()
            
            self.column += indent_level
            return Token(TokenType.DEDENT, '', self.line, start_pos + 1)
        
        else:
            # 缩进相同
            self.column += indent_level
            return None
    
    def _is_blank_line(self) -> bool:
        """检查是否为空行"""
        pos = self.pos
        while pos < len(self.source):
            char = self.source[pos]
            if char == '\n':
                return True
            if char not in (' ', '\t'):
                return char == '#'  # 注释行也算空行
            pos += 1
        return True
    
    def _read_string(self) -> Token:
        """读取字符串字面量"""
        start_pos = self.pos
        start_column = self.column
        quote = self.source[self.pos]
        self._advance()
        
        value = ''
        while self.pos < len(self.source):
            char = self.source[self.pos]
            
            if char == quote:
                self._advance()
                return Token(TokenType.STRING, value, self.line, start_column)
            
            if char == '\\' and self.pos + 1 < len(self.source):
                # 处理转义字符
                self._advance()
                escape_char = self.source[self.pos]
                if escape_char == 'n':
                    value += '\n'
                elif escape_char == 't':
                    value += '\t'
                elif escape_char == 'r':
                    value += '\r'
                elif escape_char == '\\':
                    value += '\\'
                elif escape_char == quote:
                    value += quote
                else:
                    value += escape_char
                self._advance()
            else:
                value += char
                self._advance()
        
        raise LexerError("未闭合的字符串", self.line, start_column)
    
    def _read_number(self) -> Token:
        """读取数字字面量"""
        start_column = self.column
        value = ''
        has_dot = False
        
        while (self.pos < len(self.source) and 
               (self.source[self.pos].isdigit() or self.source[self.pos] == '.')):
            char = self.source[self.pos]
            
            if char == '.':
                if has_dot:
                    break  # 第二个点，停止
                has_dot = True
            
            value += char
            self._advance()
        
        return Token(TokenType.NUMBER, value, self.line, start_column)
    
    def _read_identifier(self) -> Token:
        """读取标识符或关键字"""
        start_column = self.column
        value = ''
        
        while (self.pos < len(self.source) and 
               (self.source[self.pos].isalnum() or self.source[self.pos] == '_')):
            value += self.source[self.pos]
            self._advance()
        
        # 检查是否为关键字
        token_type = TokenType.KEYWORD if value in self.KEYWORDS else TokenType.IDENTIFIER
        return Token(token_type, value, self.line, start_column)
    
    def _skip_whitespace(self) -> None:
        """跳过空白字符（不包括换行符）"""
        while (self.pos < len(self.source) and 
               self.source[self.pos] in (' ', '\t') and 
               not self.at_line_start):
            self._advance()
    
    def _skip_comment(self) -> None:
        """跳过注释"""
        while self.pos < len(self.source) and self.source[self.pos] != '\n':
            self._advance()
    
    def _make_token(self, token_type: TokenType, value: str) -> Token:
        """创建token并前进位置"""
        token = Token(token_type, value, self.line, self.column)
        self._advance(len(value))
        return token
    
    def _advance(self, count: int = 1) -> None:
        """前进位置"""
        for _ in range(count):
            if self.pos < len(self.source):
                if self.source[self.pos] == '\n':
                    self.line += 1
                    self.column = 1
                else:
                    self.column += 1
                self.pos += 1


def tokenize(source: str) -> List[Token]:
    """便捷函数：对源代码进行词法分析"""
    lexer = Lexer(source)
    return lexer.tokenize()

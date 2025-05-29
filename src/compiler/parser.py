"""
PyVM语法分析器
将token序列转换为抽象语法树(AST)
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Any, Union
from dataclasses import dataclass
from .lexer import Token, TokenType, LexerError


# AST节点基类
class ASTNode(ABC):
    """抽象语法树节点基类"""
    pass


# 表达式节点
class Expression(ASTNode):
    """表达式基类"""
    pass


@dataclass
class NumberLiteral(Expression):
    """数字字面量"""
    value: Union[int, float]


@dataclass
class StringLiteral(Expression):
    """字符串字面量"""
    value: str


@dataclass
class BooleanLiteral(Expression):
    """布尔字面量"""
    value: bool


@dataclass
class Identifier(Expression):
    """标识符"""
    name: str


@dataclass
class BinaryOperation(Expression):
    """二元运算"""
    left: Expression
    operator: str
    right: Expression


@dataclass
class UnaryOperation(Expression):
    """一元运算"""
    operator: str
    operand: Expression


@dataclass
class FunctionCall(Expression):
    """函数调用"""
    name: str
    arguments: List[Expression]


# 语句节点
class Statement(ASTNode):
    """语句基类"""
    pass


@dataclass
class Assignment(Statement):
    """赋值语句"""
    target: str
    value: Expression


@dataclass
class ExpressionStatement(Statement):
    """表达式语句"""
    expression: Expression


@dataclass
class IfStatement(Statement):
    """if语句"""
    condition: Expression
    then_body: List[Statement]
    else_body: Optional[List[Statement]] = None


@dataclass
class WhileStatement(Statement):
    """while语句"""
    condition: Expression
    body: List[Statement]


@dataclass
class FunctionDef(Statement):
    """函数定义"""
    name: str
    parameters: List[str]
    body: List[Statement]


@dataclass
class ReturnStatement(Statement):
    """return语句"""
    value: Optional[Expression] = None


@dataclass
class Program(ASTNode):
    """程序（语句列表）"""
    statements: List[Statement]


class ParseError(Exception):
    """语法分析错误"""
    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"语法错误 {token.line}:{token.column}: {message}")


class Parser:
    """语法分析器"""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0] if tokens else None
    
    def parse(self) -> Program:
        """解析程序"""
        statements = []
        
        while not self._is_at_end():
            # 跳过换行符
            if self._match(TokenType.NEWLINE):
                continue
            
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
        
        return Program(statements)
    
    def _parse_statement(self) -> Optional[Statement]:
        """解析语句"""
        try:
            # 处理缩进块
            if self._match(TokenType.INDENT):
                return None  # 缩进由上层处理
            
            if self._match(TokenType.DEDENT):
                return None  # 缩进由上层处理
            
            # if语句
            if self._check(TokenType.KEYWORD, 'if'):
                return self._parse_if_statement()
            
            # while语句
            if self._check(TokenType.KEYWORD, 'while'):
                return self._parse_while_statement()
            
            # 函数定义
            if self._check(TokenType.KEYWORD, 'def'):
                return self._parse_function_def()
            
            # return语句
            if self._check(TokenType.KEYWORD, 'return'):
                return self._parse_return_statement()
            
            # 赋值或表达式语句
            return self._parse_assignment_or_expression()
        
        except ParseError as e:
            self._synchronize()
            raise e
    
    def _parse_if_statement(self) -> IfStatement:
        """解析if语句"""
        self._consume(TokenType.KEYWORD, "期望 'if'")
        condition = self._parse_expression()
        self._consume(TokenType.COLON, "期望 ':'")
        self._consume(TokenType.NEWLINE, "期望换行")
        
        then_body = self._parse_block()
        else_body = None
        
        if self._check(TokenType.KEYWORD, 'else'):
            self._advance()
            self._consume(TokenType.COLON, "期望 ':'")
            self._consume(TokenType.NEWLINE, "期望换行")
            else_body = self._parse_block()
        
        return IfStatement(condition, then_body, else_body)
    
    def _parse_while_statement(self) -> WhileStatement:
        """解析while语句"""
        self._consume(TokenType.KEYWORD, "期望 'while'")
        condition = self._parse_expression()
        self._consume(TokenType.COLON, "期望 ':'")
        self._consume(TokenType.NEWLINE, "期望换行")
        
        body = self._parse_block()
        return WhileStatement(condition, body)
    
    def _parse_function_def(self) -> FunctionDef:
        """解析函数定义"""
        self._consume(TokenType.KEYWORD, "期望 'def'")
        name = self._consume(TokenType.IDENTIFIER, "期望函数名").value
        
        self._consume(TokenType.LPAREN, "期望 '('")
        parameters = []
        
        if not self._check(TokenType.RPAREN):
            parameters.append(self._consume(TokenType.IDENTIFIER, "期望参数名").value)
            while self._match(TokenType.COMMA):
                parameters.append(self._consume(TokenType.IDENTIFIER, "期望参数名").value)
        
        self._consume(TokenType.RPAREN, "期望 ')'")
        self._consume(TokenType.COLON, "期望 ':'")
        self._consume(TokenType.NEWLINE, "期望换行")
        
        body = self._parse_block()
        return FunctionDef(name, parameters, body)
    
    def _parse_return_statement(self) -> ReturnStatement:
        """解析return语句"""
        self._consume(TokenType.KEYWORD, "期望 'return'")
        
        value = None
        if not self._check(TokenType.NEWLINE):
            value = self._parse_expression()
        
        return ReturnStatement(value)
    
    def _parse_block(self) -> List[Statement]:
        """解析代码块"""
        statements = []
        
        self._consume(TokenType.INDENT, "期望缩进")
        
        while not self._check(TokenType.DEDENT) and not self._is_at_end():
            if self._match(TokenType.NEWLINE):
                continue
            
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
        
        self._consume(TokenType.DEDENT, "期望反缩进")
        return statements
    
    def _parse_assignment_or_expression(self) -> Statement:
        """解析赋值或表达式语句"""
        # 先解析表达式
        expr = self._parse_expression()
        
        # 检查是否为赋值
        if self._match(TokenType.ASSIGN):
            if not isinstance(expr, Identifier):
                raise ParseError("赋值目标必须是标识符", self.current_token)
            
            value = self._parse_expression()
            return Assignment(expr.name, value)
        
        # 否则是表达式语句
        return ExpressionStatement(expr)
    
    def _parse_expression(self) -> Expression:
        """解析表达式"""
        return self._parse_or()
    
    def _parse_or(self) -> Expression:
        """解析or表达式"""
        expr = self._parse_and()
        
        while self._check(TokenType.KEYWORD, 'or'):
            operator = self._advance().value
            right = self._parse_and()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def _parse_and(self) -> Expression:
        """解析and表达式"""
        expr = self._parse_equality()
        
        while self._check(TokenType.KEYWORD, 'and'):
            operator = self._advance().value
            right = self._parse_equality()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def _parse_equality(self) -> Expression:
        """解析相等性表达式"""
        expr = self._parse_comparison()
        
        while self._match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            operator = self._previous().value
            right = self._parse_comparison()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def _parse_comparison(self) -> Expression:
        """解析比较表达式"""
        expr = self._parse_term()
        
        while self._match(TokenType.GREATER_THAN, TokenType.GREATER_EQUAL,
                          TokenType.LESS_THAN, TokenType.LESS_EQUAL):
            operator = self._previous().value
            right = self._parse_term()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def _parse_term(self) -> Expression:
        """解析加减表达式"""
        expr = self._parse_factor()
        
        while self._match(TokenType.PLUS, TokenType.MINUS):
            operator = self._previous().value
            right = self._parse_factor()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def _parse_factor(self) -> Expression:
        """解析乘除表达式"""
        expr = self._parse_unary()
        
        while self._match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            operator = self._previous().value
            right = self._parse_unary()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def _parse_unary(self) -> Expression:
        """解析一元表达式"""
        if self._match(TokenType.MINUS, TokenType.PLUS):
            operator = self._previous().value
            expr = self._parse_unary()
            return UnaryOperation(operator, expr)
        
        if self._check(TokenType.KEYWORD, 'not'):
            operator = self._advance().value
            expr = self._parse_unary()
            return UnaryOperation(operator, expr)
        
        return self._parse_primary()
    
    def _parse_primary(self) -> Expression:
        """解析基本表达式"""
        # 数字
        if self._check(TokenType.NUMBER):
            value = self._advance().value
            if '.' in value:
                return NumberLiteral(float(value))
            else:
                return NumberLiteral(int(value))
        
        # 字符串
        if self._check(TokenType.STRING):
            return StringLiteral(self._advance().value)
        
        # 布尔值
        if self._check(TokenType.KEYWORD, 'True'):
            self._advance()
            return BooleanLiteral(True)
        
        if self._check(TokenType.KEYWORD, 'False'):
            self._advance()
            return BooleanLiteral(False)
        
        # 标识符或函数调用
        if self._check(TokenType.IDENTIFIER):
            name = self._advance().value
            
            # 函数调用
            if self._match(TokenType.LPAREN):
                arguments = []
                
                if not self._check(TokenType.RPAREN):
                    arguments.append(self._parse_expression())
                    while self._match(TokenType.COMMA):
                        arguments.append(self._parse_expression())
                
                self._consume(TokenType.RPAREN, "期望 ')'")
                return FunctionCall(name, arguments)
            
            # 普通标识符
            return Identifier(name)
        
        # 括号表达式
        if self._match(TokenType.LPAREN):
            expr = self._parse_expression()
            self._consume(TokenType.RPAREN, "期望 ')'")
            return expr
        
        raise ParseError(f"意外的token: {self.current_token.value}", self.current_token)
    
    def _match(self, *types: TokenType) -> bool:
        """检查当前token是否匹配指定类型"""
        for token_type in types:
            if self._check(token_type):
                self._advance()
                return True
        return False
    
    def _check(self, token_type: TokenType, value: str = None) -> bool:
        """检查当前token类型"""
        if self._is_at_end():
            return False
        
        if self.current_token.type != token_type:
            return False
        
        if value is not None and self.current_token.value != value:
            return False
        
        return True
    
    def _advance(self) -> Token:
        """前进到下一个token"""
        if not self._is_at_end():
            self.pos += 1
            if self.pos < len(self.tokens):
                self.current_token = self.tokens[self.pos]
        return self._previous()
    
    def _is_at_end(self) -> bool:
        """检查是否到达末尾"""
        return (self.current_token is None or 
                self.current_token.type == TokenType.EOF)
    
    def _previous(self) -> Token:
        """获取前一个token"""
        return self.tokens[self.pos - 1]
    
    def _consume(self, token_type: TokenType, message: str) -> Token:
        """消费指定类型的token"""
        if self._check(token_type):
            return self._advance()
        
        raise ParseError(message, self.current_token)
    
    def _synchronize(self) -> None:
        """错误恢复：同步到下一个语句"""
        self._advance()
        
        while not self._is_at_end():
            if self._previous().type == TokenType.NEWLINE:
                return
            
            if self.current_token.type == TokenType.KEYWORD:
                if self.current_token.value in ['if', 'while', 'def', 'return']:
                    return
            
            self._advance()


def parse(tokens: List[Token]) -> Program:
    """便捷函数：解析token序列为AST"""
    parser = Parser(tokens)
    return parser.parse()

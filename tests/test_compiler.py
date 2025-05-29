"""
PyVM编译器测试
"""

import unittest
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from compiler import tokenize, parse, generate_code, TokenType


class TestLexer(unittest.TestCase):
    """词法分析器测试"""
    
    def test_numbers(self):
        """测试数字解析"""
        tokens = tokenize("123 45.67")
        self.assertEqual(len(tokens), 3)  # 2个数字 + EOF
        self.assertEqual(tokens[0].type, TokenType.NUMBER)
        self.assertEqual(tokens[0].value, "123")
        self.assertEqual(tokens[1].type, TokenType.NUMBER)
        self.assertEqual(tokens[1].value, "45.67")
    
    def test_strings(self):
        """测试字符串解析"""
        tokens = tokenize('"hello" \'world\'')
        self.assertEqual(len(tokens), 3)  # 2个字符串 + EOF
        self.assertEqual(tokens[0].type, TokenType.STRING)
        self.assertEqual(tokens[0].value, "hello")
        self.assertEqual(tokens[1].type, TokenType.STRING)
        self.assertEqual(tokens[1].value, "world")
    
    def test_identifiers(self):
        """测试标识符解析"""
        tokens = tokenize("abc _var var123")
        self.assertEqual(len(tokens), 4)  # 3个标识符 + EOF
        for i in range(3):
            self.assertEqual(tokens[i].type, TokenType.IDENTIFIER)
    
    def test_keywords(self):
        """测试关键字解析"""
        tokens = tokenize("if else while")
        self.assertEqual(len(tokens), 4)  # 3个关键字 + EOF
        for i in range(3):
            self.assertEqual(tokens[i].type, TokenType.KEYWORD)
    
    def test_operators(self):
        """测试运算符解析"""
        tokens = tokenize("+ - * / == !=")
        operators = [TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, 
                    TokenType.DIVIDE, TokenType.EQUAL, TokenType.NOT_EQUAL]
        
        for i, op_type in enumerate(operators):
            self.assertEqual(tokens[i].type, op_type)


class TestParser(unittest.TestCase):
    """语法分析器测试"""
    
    def test_assignment(self):
        """测试赋值语句"""
        tokens = tokenize("x = 10")
        ast = parse(tokens)
        self.assertEqual(len(ast.statements), 1)
        
        stmt = ast.statements[0]
        self.assertEqual(stmt.target, "x")
        self.assertEqual(stmt.value.value, 10)
    
    def test_binary_operation(self):
        """测试二元运算"""
        tokens = tokenize("result = a + b")
        ast = parse(tokens)
        stmt = ast.statements[0]
        
        self.assertEqual(stmt.target, "result")
        self.assertEqual(stmt.value.operator, "+")
        self.assertEqual(stmt.value.left.name, "a")
        self.assertEqual(stmt.value.right.name, "b")
    
    def test_if_statement(self):
        """测试if语句"""
        source = """
if x > 0:
    print(x)
"""
        tokens = tokenize(source)
        ast = parse(tokens)
        self.assertEqual(len(ast.statements), 1)
        
        stmt = ast.statements[0]
        self.assertEqual(stmt.condition.operator, ">")
        self.assertEqual(len(stmt.then_body), 1)


class TestCodeGenerator(unittest.TestCase):
    """代码生成器测试"""
    
    def test_simple_assignment(self):
        """测试简单赋值"""
        tokens = tokenize("x = 42")
        ast = parse(tokens)
        constants, symbols, instructions = generate_code(ast)
        
        # 应该有一个常量42
        self.assertEqual(len(constants), 1)
        self.assertEqual(constants[0].value, 42)
        
        # 应该有一个符号x
        self.assertEqual(len(symbols), 1)
        self.assertEqual(symbols[0].name, "x")
        
        # 应该有3条指令: LOAD_CONST, STORE_VAR, HALT
        self.assertEqual(len(instructions), 3)
    
    def test_arithmetic(self):
        """测试算术运算"""
        tokens = tokenize("result = 10 + 20")
        ast = parse(tokens)
        constants, symbols, instructions = generate_code(ast)
        
        # 应该有两个常量: 10, 20
        self.assertEqual(len(constants), 2)
        
        # 应该包含ADD指令
        opcodes = [inst.opcode.name for inst in instructions]
        self.assertIn("ADD", opcodes)


if __name__ == '__main__':
    unittest.main()

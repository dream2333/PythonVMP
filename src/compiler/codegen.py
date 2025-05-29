"""
PyVM代码生成器
将抽象语法树(AST)转换为字节码
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Any, Optional
from vm.instructions import (
    OpCode, Instruction, Constant, Symbol, 
    DataType, SymbolType
)
from .parser import (
    ASTNode, Program, Statement, Expression,
    Assignment, ExpressionStatement, IfStatement, WhileStatement,
    FunctionDef, ReturnStatement,
    NumberLiteral, StringLiteral, BooleanLiteral, Identifier,
    BinaryOperation, UnaryOperation, FunctionCall
)


class CodeGenError(Exception):
    """代码生成错误"""
    pass


class CodeGenerator:
    """代码生成器"""
    
    def __init__(self):
        self.instructions: List[Instruction] = []
        self.constants: List[Constant] = []
        self.symbols: List[Symbol] = []
        
        # 符号表管理
        self.symbol_map: Dict[str, int] = {}  # 符号名 -> 索引
        self.constant_map: Dict[Any, int] = {}  # 常量值 -> 索引
        
        # 变量管理
        self.next_var_index = 0
        self.var_map: Dict[str, int] = {}  # 变量名 -> 索引
        
        # 控制流管理
        self.break_targets: List[int] = []  # break跳转目标
        self.continue_targets: List[int] = []  # continue跳转目标
    
    def generate(self, ast: Program) -> tuple:
        """生成字节码"""
        self._reset()
        
        # 遍历AST生成指令
        for statement in ast.statements:
            self._generate_statement(statement)
        
        # 添加程序结束指令
        self._emit(OpCode.HALT)
        
        return self.constants, self.symbols, self.instructions
    
    def _reset(self) -> None:
        """重置生成器状态"""
        self.instructions.clear()
        self.constants.clear()
        self.symbols.clear()
        self.symbol_map.clear()
        self.constant_map.clear()
        self.next_var_index = 0
        self.var_map.clear()
        self.break_targets.clear()
        self.continue_targets.clear()
    
    def _generate_statement(self, stmt: Statement) -> None:
        """生成语句代码"""
        if isinstance(stmt, Assignment):
            self._generate_assignment(stmt)
        elif isinstance(stmt, ExpressionStatement):
            # 检查是否为函数调用
            if isinstance(stmt.expression, FunctionCall):
                # 函数调用可能有副作用，需要执行但不需要保留返回值
                self._generate_expression(stmt.expression)
                # 对于有返回值的函数（如input），需要弹出返回值
                if stmt.expression.name == 'input':
                    self._emit(OpCode.POP)
            else:
                # 普通表达式需要弹出结果
                self._generate_expression(stmt.expression)
                self._emit(OpCode.POP)
        elif isinstance(stmt, IfStatement):
            self._generate_if_statement(stmt)
        elif isinstance(stmt, WhileStatement):
            self._generate_while_statement(stmt)
        elif isinstance(stmt, FunctionDef):
            self._generate_function_def(stmt)
        elif isinstance(stmt, ReturnStatement):
            self._generate_return_statement(stmt)
        else:
            raise CodeGenError(f"不支持的语句类型: {type(stmt)}")
    
    def _generate_assignment(self, stmt: Assignment) -> None:
        """生成赋值语句代码"""
        # 生成右侧表达式
        self._generate_expression(stmt.value)
        
        # 获取或创建变量索引
        var_index = self._get_var_index(stmt.target)
        
        # 存储到变量
        self._emit(OpCode.STORE_VAR, var_index)
    
    def _generate_if_statement(self, stmt: IfStatement) -> None:
        """生成if语句代码"""
        # 生成条件表达式
        self._generate_expression(stmt.condition)
        
        # 条件跳转（假时跳转到else或endif）
        else_jump = self._emit_jump(OpCode.JUMP_IF_FALSE)
        
        # 生成then分支
        for s in stmt.then_body:
            self._generate_statement(s)
        
        if stmt.else_body:
            # 跳过else分支
            endif_jump = self._emit_jump(OpCode.JUMP)
            
            # 修正else跳转目标
            self._patch_jump(else_jump)
            
            # 生成else分支
            for s in stmt.else_body:
                self._generate_statement(s)
            
            # 修正endif跳转目标
            self._patch_jump(endif_jump)
        else:
            # 修正else跳转目标
            self._patch_jump(else_jump)
    
    def _generate_while_statement(self, stmt: WhileStatement) -> None:
        """生成while语句代码"""
        loop_start = len(self.instructions)
        
        # 生成条件表达式
        self._generate_expression(stmt.condition)
        
        # 条件跳转（假时跳出循环）
        exit_jump = self._emit_jump(OpCode.JUMP_IF_FALSE)
        
        # 保存跳转目标
        self.break_targets.append(exit_jump)
        self.continue_targets.append(loop_start)
        
        # 生成循环体
        for s in stmt.body:
            self._generate_statement(s)
        
        # 跳回循环开始
        self._emit(OpCode.JUMP, loop_start)
        
        # 修正退出跳转
        self._patch_jump(exit_jump)
        
        # 清理跳转目标
        self.break_targets.pop()
        self.continue_targets.pop()
    
    def _generate_function_def(self, stmt: FunctionDef) -> None:
        """生成函数定义代码"""
        # 简化实现：暂不支持用户定义函数
        raise CodeGenError("用户定义函数暂未实现")
    
    def _generate_return_statement(self, stmt: ReturnStatement) -> None:
        """生成return语句代码"""
        if stmt.value:
            self._generate_expression(stmt.value)
        else:
            # 默认返回None
            none_index = self._add_constant(None, DataType.INT)  # 简化为0
            self._emit(OpCode.LOAD_CONST, none_index)
        
        self._emit(OpCode.RETURN)
    
    def _generate_expression(self, expr: Expression) -> None:
        """生成表达式代码"""
        if isinstance(expr, NumberLiteral):
            self._generate_number_literal(expr)
        elif isinstance(expr, StringLiteral):
            self._generate_string_literal(expr)
        elif isinstance(expr, BooleanLiteral):
            self._generate_boolean_literal(expr)
        elif isinstance(expr, Identifier):
            self._generate_identifier(expr)
        elif isinstance(expr, BinaryOperation):
            self._generate_binary_operation(expr)
        elif isinstance(expr, UnaryOperation):
            self._generate_unary_operation(expr)
        elif isinstance(expr, FunctionCall):
            self._generate_function_call(expr)
        else:
            raise CodeGenError(f"不支持的表达式类型: {type(expr)}")
    
    def _generate_number_literal(self, expr: NumberLiteral) -> None:
        """生成数字字面量代码"""
        if isinstance(expr.value, int):
            data_type = DataType.INT
        else:
            data_type = DataType.FLOAT
        
        const_index = self._add_constant(expr.value, data_type)
        self._emit(OpCode.LOAD_CONST, const_index)
    
    def _generate_string_literal(self, expr: StringLiteral) -> None:
        """生成字符串字面量代码"""
        const_index = self._add_constant(expr.value, DataType.STRING)
        self._emit(OpCode.LOAD_CONST, const_index)
    
    def _generate_boolean_literal(self, expr: BooleanLiteral) -> None:
        """生成布尔字面量代码"""
        const_index = self._add_constant(expr.value, DataType.BOOL)
        self._emit(OpCode.LOAD_CONST, const_index)
    
    def _generate_identifier(self, expr: Identifier) -> None:
        """生成标识符代码"""
        var_index = self._get_var_index(expr.name)
        self._emit(OpCode.LOAD_VAR, var_index)
    
    def _generate_binary_operation(self, expr: BinaryOperation) -> None:
        """生成二元运算代码"""
        # 生成左操作数
        self._generate_expression(expr.left)
        
        # 生成右操作数
        self._generate_expression(expr.right)
        
        # 生成运算指令
        op_map = {
            '+': OpCode.ADD,
            '-': OpCode.SUB,
            '*': OpCode.MUL,
            '/': OpCode.DIV,
            '%': OpCode.MOD,
            '==': OpCode.CMP_EQ,
            '!=': OpCode.CMP_NE,
            '<': OpCode.CMP_LT,
            '<=': OpCode.CMP_LE,
            '>': OpCode.CMP_GT,
            '>=': OpCode.CMP_GE,
        }
        
        if expr.operator in op_map:
            self._emit(op_map[expr.operator])
        elif expr.operator == 'and':
            # 短路求值：如果左边为假，直接返回假
            # 这里简化实现，不做短路优化
            self._emit(OpCode.MUL)  # 简化为乘法
        elif expr.operator == 'or':
            # 短路求值：如果左边为真，直接返回真
            # 这里简化实现，不做短路优化
            self._emit(OpCode.ADD)  # 简化为加法
        else:
            raise CodeGenError(f"不支持的二元运算符: {expr.operator}")
    
    def _generate_unary_operation(self, expr: UnaryOperation) -> None:
        """生成一元运算代码"""
        self._generate_expression(expr.operand)
        
        if expr.operator == '-':
            self._emit(OpCode.NEG)
        elif expr.operator == '+':
            pass  # 正号不需要操作
        elif expr.operator == 'not':
            # 简化实现：not x 等价于 x == False
            false_index = self._add_constant(False, DataType.BOOL)
            self._emit(OpCode.LOAD_CONST, false_index)
            self._emit(OpCode.CMP_EQ)
        else:
            raise CodeGenError(f"不支持的一元运算符: {expr.operator}")
    
    def _generate_function_call(self, expr: FunctionCall) -> None:
        """生成函数调用代码"""
        # 内置函数特殊处理
        if expr.name == 'print':
            if len(expr.arguments) != 1:
                raise CodeGenError("print函数只支持一个参数")
            
            self._generate_expression(expr.arguments[0])
            self._emit(OpCode.PRINT)
            # print函数不返回值，不需要在栈上留下结果
        elif expr.name == 'input':
            if len(expr.arguments) != 0:
                raise CodeGenError("input函数不支持参数")
            
            self._emit(OpCode.INPUT)
            # input函数返回值，会在栈上留下结果
        else:
            # 用户定义函数（暂未实现）
            raise CodeGenError(f"未知函数: {expr.name}")
    
    def _add_constant(self, value: Any, data_type: DataType) -> int:
        """添加常量到常量池"""
        # 检查是否已存在
        if value in self.constant_map:
            return self.constant_map[value]
        
        # 添加新常量
        index = len(self.constants)
        constant = Constant(value, data_type)
        self.constants.append(constant)
        self.constant_map[value] = index
        
        return index
    
    def _get_var_index(self, name: str) -> int:
        """获取变量索引"""
        if name in self.var_map:
            return self.var_map[name]
        
        # 创建新变量
        index = self.next_var_index
        self.next_var_index += 1
        self.var_map[name] = index
        
        # 添加到符号表
        symbol = Symbol(name, SymbolType.VAR, index)
        self.symbols.append(symbol)
        self.symbol_map[name] = len(self.symbols) - 1
        
        return index
    
    def _emit(self, opcode: OpCode, operand: int = None) -> int:
        """发出指令"""
        instruction = Instruction(opcode, operand)
        self.instructions.append(instruction)
        return len(self.instructions) - 1
    
    def _emit_jump(self, opcode: OpCode) -> int:
        """发出跳转指令（返回指令索引用于后续修正）"""
        return self._emit(opcode, 0)  # 占位符，后续修正
    
    def _patch_jump(self, instruction_index: int) -> None:
        """修正跳转指令的目标地址"""
        target = len(self.instructions)
        self.instructions[instruction_index].operand = target
    
    def get_disassembly(self) -> str:
        """获取反汇编代码"""
        lines = []
        
        # 常量池
        lines.append("=== 常量池 ===")
        for i, const in enumerate(self.constants):
            lines.append(f"[{i:2d}] {const}")
        
        # 符号表
        lines.append("\n=== 符号表 ===")
        for i, symbol in enumerate(self.symbols):
            lines.append(f"[{i:2d}] {symbol}")
        
        # 指令序列
        lines.append("\n=== 指令序列 ===")
        for i, inst in enumerate(self.instructions):
            lines.append(f"{i:04d}: {inst}")
        
        return "\n".join(lines)


def generate_code(ast: Program) -> tuple:
    """便捷函数：生成字节码"""
    generator = CodeGenerator()
    return generator.generate(ast)

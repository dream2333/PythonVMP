"""
PyVM虚拟机核心模块
实现字节码执行引擎
"""

import sys
import time
from typing import Any, List, Dict, Optional
from .instructions import OpCode, Instruction, Constant, Symbol, DataType
from .stack import VMStack, CallStack, CallFrame


class VMError(Exception):
    """虚拟机运行时错误"""
    pass


class PyVirtualMachine:
    """Python虚拟机"""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        
        # 执行状态
        self.pc = 0  # 程序计数器
        self.running = False
        
        # 数据存储
        self.constants: List[Constant] = []      # 常量池
        self.variables: Dict[int, Any] = {}      # 变量表
        self.symbols: Dict[str, Symbol] = {}     # 符号表
        self.instructions: List[Instruction] = [] # 指令序列
        
        # 运行时栈
        self.stack = VMStack()
        self.call_stack = CallStack()
        
        # 统计信息
        self.instruction_count = 0
        self.start_time = 0
        self.execution_time = 0
        self.instruction_stats = {}  # 指令执行统计
    
    def load_program(self, constants: List[Constant], symbols: List[Symbol], 
                    instructions: List[Instruction]) -> None:
        """加载程序到虚拟机"""
        self.constants = constants
        self.instructions = instructions
        
        # 构建符号表
        self.symbols = {symbol.name: symbol for symbol in symbols}
        
        # 重置状态
        self.pc = 0
        self.running = True  # 准备执行
        self.stack.clear()
        self.variables.clear()
        self.instruction_count = 0
        
        if self.debug:
            print(f"程序加载完成: {len(instructions)} 条指令")
    
    def run(self) -> None:
        """运行程序"""
        self.running = True
        self.pc = 0
        self.start_time = time.time()
        
        if self.debug:
            print("开始执行程序...")
            self._print_program_info()
        
        try:
            while self.running and self.pc < len(self.instructions):
                self._execute_instruction()
        except Exception as e:
            self._handle_error(e)
        finally:
            self.execution_time = time.time() - self.start_time
            if self.debug:
                print(f"程序执行完成")
                print(f"执行指令数: {self.instruction_count}")
                print(f"执行时间: {self.execution_time:.4f} 秒")
                print(f"平均指令执行速度: {self.instruction_count / max(self.execution_time, 0.0001):.0f} 指令/秒")
    
    def step(self) -> bool:
        """单步执行一条指令"""
        if not self.running or self.pc >= len(self.instructions):
            return False
        
        try:
            self._execute_instruction()
            return self.running
        except Exception as e:
            self._handle_error(e)
            return False
    
    def _execute_instruction(self) -> None:
        """执行当前指令"""
        if self.pc >= len(self.instructions):
            self.running = False
            return
        
        instruction = self.instructions[self.pc]
        
        if self.debug:
            self._print_debug_info(instruction)
        
        # 执行指令
        self._dispatch_instruction(instruction)
        
        # 更新计数器
        self.instruction_count += 1
        
        # 默认移动到下一条指令（跳转指令会覆盖）
        self.pc += 1
    
    def _dispatch_instruction(self, instruction: Instruction) -> None:
        """分发指令执行"""
        opcode = instruction.opcode
        operand = instruction.operand
        
        # 统计指令执行次数
        if opcode.name not in self.instruction_stats:
            self.instruction_stats[opcode.name] = 0
        self.instruction_stats[opcode.name] += 1
        
        # 栈操作指令
        if opcode == OpCode.NOP:
            pass
        elif opcode == OpCode.LOAD_CONST:
            self._load_const(operand)
        elif opcode == OpCode.LOAD_VAR:
            self._load_var(operand)
        elif opcode == OpCode.STORE_VAR:
            self._store_var(operand)
        elif opcode == OpCode.POP:
            self.stack.pop()
        elif opcode == OpCode.DUP:
            self.stack.dup()
        
        # 算术运算指令
        elif opcode == OpCode.ADD:
            self._binary_op(lambda a, b: a + b)
        elif opcode == OpCode.SUB:
            self._binary_op(lambda a, b: a - b)
        elif opcode == OpCode.MUL:
            self._binary_op(lambda a, b: a * b)
        elif opcode == OpCode.DIV:
            self._binary_op(lambda a, b: a / b)
        elif opcode == OpCode.MOD:
            self._binary_op(lambda a, b: a % b)
        elif opcode == OpCode.NEG:
            self._unary_op(lambda a: -a)
        
        # 比较运算指令
        elif opcode == OpCode.CMP_EQ:
            self._binary_op(lambda a, b: a == b)
        elif opcode == OpCode.CMP_NE:
            self._binary_op(lambda a, b: a != b)
        elif opcode == OpCode.CMP_LT:
            self._binary_op(lambda a, b: a < b)
        elif opcode == OpCode.CMP_LE:
            self._binary_op(lambda a, b: a <= b)
        elif opcode == OpCode.CMP_GT:
            self._binary_op(lambda a, b: a > b)
        elif opcode == OpCode.CMP_GE:
            self._binary_op(lambda a, b: a >= b)
        
        # 控制流指令
        elif opcode == OpCode.JUMP:
            self._jump(operand)
        elif opcode == OpCode.JUMP_IF_FALSE:
            self._jump_if_false(operand)
        elif opcode == OpCode.JUMP_IF_TRUE:
            self._jump_if_true(operand)
        elif opcode == OpCode.CALL:
            self._call(operand)
        elif opcode == OpCode.RETURN:
            self._return()
        
        # 内置函数指令
        elif opcode == OpCode.PRINT:
            self._print()
        elif opcode == OpCode.INPUT:
            self._input()
        
        # 程序控制指令
        elif opcode == OpCode.HALT:
            self.running = False
        
        else:
            raise VMError(f"未知指令: {opcode}")
    
    def _load_const(self, index: int) -> None:
        """加载常量到栈"""
        if index >= len(self.constants):
            raise VMError(f"常量索引超出范围: {index}")
        self.stack.push(self.constants[index].value)
    
    def _load_var(self, index: int) -> None:
        """加载变量到栈"""
        if index not in self.variables:
            raise VMError(f"未定义的变量索引: {index}")
        self.stack.push(self.variables[index])
    
    def _store_var(self, index: int) -> None:
        """将栈顶值存储到变量"""
        value = self.stack.pop()
        self.variables[index] = value
    
    def _binary_op(self, operation) -> None:
        """执行二元运算"""
        b = self.stack.pop()
        a = self.stack.pop()
        result = operation(a, b)
        self.stack.push(result)
    
    def _unary_op(self, operation) -> None:
        """执行一元运算"""
        a = self.stack.pop()
        result = operation(a)
        self.stack.push(result)
    
    def _jump(self, offset: int) -> None:
        """无条件跳转"""
        self.pc = offset - 1  # -1 因为执行完会自动+1
    
    def _jump_if_false(self, offset: int) -> None:
        """条件跳转（假）"""
        condition = self.stack.pop()
        if not condition:
            self.pc = offset - 1
    
    def _jump_if_true(self, offset: int) -> None:
        """条件跳转（真）"""
        condition = self.stack.pop()
        if condition:
            self.pc = offset - 1
    
    def _call(self, function_address: int) -> None:
        """函数调用"""
        # 创建新的调用帧
        frame = CallFrame(self.pc + 1)  # 返回地址是下一条指令
        self.call_stack.push_frame(frame)
        
        # 跳转到函数地址
        self.pc = function_address - 1  # -1 因为执行完会自动+1
        
        if self.debug:
            print(f"调用函数，跳转到地址: {function_address}")
    
    def _return(self) -> None:
        """函数返回"""
        if self.call_stack.is_empty():
            # 如果没有调用帧，说明是主程序结束
            self.running = False
            return
        
        # 弹出调用帧并恢复执行位置
        frame = self.call_stack.pop_frame()
        self.pc = frame.return_address - 1  # -1 因为执行完会自动+1
        
        if self.debug:
            print(f"函数返回，返回地址: {frame.return_address}")
    
    def _print(self) -> None:
        """打印栈顶值"""
        value = self.stack.pop()
        print(value)
    
    def _input(self) -> None:
        """读取输入"""
        try:
            value = input("输入: ")
            # 尝试转换为数字
            try:
                if '.' in value:
                    self.stack.push(float(value))
                else:
                    self.stack.push(int(value))
            except ValueError:
                self.stack.push(value)  # 作为字符串
        except EOFError:
            self.stack.push("")
    
    def _print_debug_info(self, instruction: Instruction) -> None:
        """打印调试信息"""
        print(f"PC={self.pc:3d} | {instruction} | Stack: {self.stack}")
    
    def _print_program_info(self) -> None:
        """打印程序信息"""
        print(f"常量池: {len(self.constants)} 个常量")
        for i, const in enumerate(self.constants):
            print(f"  [{i}] {const}")
        
        print(f"指令序列: {len(self.instructions)} 条指令")
        for i, instr in enumerate(self.instructions):
            print(f"  [{i:3d}] {instr}")
    
    def _handle_error(self, error: Exception) -> None:
        """处理运行时错误"""
        print(f"运行时错误: {error}", file=sys.stderr)
        print(f"错误位置: PC={self.pc}", file=sys.stderr)
        
        if self.pc < len(self.instructions):
            print(f"当前指令: {self.instructions[self.pc]}", file=sys.stderr)
        
        print("栈状态:", file=sys.stderr)
        for line in self.stack.get_stack_trace():
            print(f"  {line}", file=sys.stderr)
        
        if not self.call_stack.is_empty():
            print("调用栈跟踪:", file=sys.stderr)
            for line in self.call_stack.get_stack_trace():
                print(f"  {line}", file=sys.stderr)
        
        self.running = False
    
    def get_status(self) -> dict:
        """获取虚拟机状态"""
        return {
            'running': self.running,
            'pc': self.pc,
            'instruction_count': self.instruction_count,
            'stack_size': self.stack.size(),
            'variables_count': len(self.variables),
            'call_depth': self.call_stack.depth(),
            'execution_time': self.execution_time
        }
    
    def get_performance_report(self) -> str:
        """获取性能报告"""
        lines = []
        lines.append("=== PyVM性能报告 ===")
        lines.append(f"总执行时间: {self.execution_time:.4f} 秒")
        lines.append(f"执行指令数: {self.instruction_count}")
        
        if self.execution_time > 0:
            ips = self.instruction_count / self.execution_time
            lines.append(f"平均执行速度: {ips:.0f} 指令/秒")
        
        lines.append("指令执行统计:")
        if self.instruction_stats:
            sorted_stats = sorted(self.instruction_stats.items(), 
                                key=lambda x: x[1], reverse=True)
            for opcode, count in sorted_stats:
                percentage = (count / self.instruction_count) * 100
                lines.append(f"  {opcode:<15}: {count:>6} 次 ({percentage:>5.1f}%)")
        
        lines.append("内存使用:")
        lines.append(f"  常量池大小: {len(self.constants)}")
        lines.append(f"  变量数量: {len(self.variables)}")
        lines.append(f"  栈深度: {self.stack.size()}")
        
        return "\n".join(lines)
    
    def reset_stats(self) -> None:
        """重置性能统计"""
        self.instruction_count = 0
        self.execution_time = 0
        self.instruction_stats.clear()

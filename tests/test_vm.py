"""
PyVM虚拟机测试
"""

import unittest
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from vm import PyVirtualMachine, OpCode, Instruction, Constant, Symbol, DataType, SymbolType


class TestVMStack(unittest.TestCase):
    """虚拟机栈测试"""
    
    def test_stack_operations(self):
        """测试栈基本操作"""
        vm = PyVirtualMachine()
        
        # 测试压栈和弹栈
        vm.stack.push(10)
        vm.stack.push(20)
        self.assertEqual(vm.stack.size(), 2)
        
        self.assertEqual(vm.stack.pop(), 20)
        self.assertEqual(vm.stack.pop(), 10)
        self.assertTrue(vm.stack.is_empty())
    
    def test_stack_peek(self):
        """测试栈查看操作"""
        vm = PyVirtualMachine()
        vm.stack.push(42)
        
        self.assertEqual(vm.stack.peek(), 42)
        self.assertEqual(vm.stack.size(), 1)  # 确保没有弹出


class TestVMInstructions(unittest.TestCase):
    """虚拟机指令测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.vm = PyVirtualMachine()
    
    def test_load_const(self):
        """测试加载常量"""
        constants = [
            Constant(42, DataType.INT),
            Constant("hello", DataType.STRING)
        ]
        symbols = []
        instructions = [
            Instruction(OpCode.LOAD_CONST, 0),
            Instruction(OpCode.LOAD_CONST, 1),
            Instruction(OpCode.HALT)
        ]
        
        self.vm.load_program(constants, symbols, instructions)
        
        # 执行前两条指令
        self.vm.step()  # LOAD_CONST 0
        self.vm.step()  # LOAD_CONST 1
        
        # 检查栈状态
        self.assertEqual(self.vm.stack.size(), 2)
        self.assertEqual(self.vm.stack.pop(), "hello")
        self.assertEqual(self.vm.stack.pop(), 42)
    
    def test_arithmetic_operations(self):
        """测试算术运算"""
        constants = [
            Constant(10, DataType.INT),
            Constant(5, DataType.INT)
        ]
        symbols = []
        instructions = [
            Instruction(OpCode.LOAD_CONST, 0),  # 加载10
            Instruction(OpCode.LOAD_CONST, 1),  # 加载5
            Instruction(OpCode.ADD),            # 10 + 5
            Instruction(OpCode.HALT)
        ]
        
        self.vm.load_program(constants, symbols, instructions)
        self.vm.run()
        
        # 检查结果
        self.assertEqual(self.vm.stack.size(), 1)
        self.assertEqual(self.vm.stack.pop(), 15)
    
    def test_variable_operations(self):
        """测试变量操作"""
        constants = [Constant(100, DataType.INT)]
        symbols = [Symbol("x", SymbolType.VAR, 0)]
        instructions = [
            Instruction(OpCode.LOAD_CONST, 0),  # 加载100
            Instruction(OpCode.STORE_VAR, 0),   # 存储到变量x
            Instruction(OpCode.LOAD_VAR, 0),    # 加载变量x
            Instruction(OpCode.HALT)
        ]
        
        self.vm.load_program(constants, symbols, instructions)
        self.vm.run()
        
        # 检查结果
        self.assertEqual(self.vm.stack.size(), 1)
        self.assertEqual(self.vm.stack.pop(), 100)
        self.assertEqual(self.vm.variables[0], 100)
    
    def test_comparison_operations(self):
        """测试比较运算"""
        constants = [
            Constant(10, DataType.INT),
            Constant(5, DataType.INT)
        ]
        symbols = []
        instructions = [
            Instruction(OpCode.LOAD_CONST, 0),  # 加载10
            Instruction(OpCode.LOAD_CONST, 1),  # 加载5
            Instruction(OpCode.CMP_GT),         # 10 > 5
            Instruction(OpCode.HALT)
        ]
        
        self.vm.load_program(constants, symbols, instructions)
        self.vm.run()
        
        # 检查结果
        self.assertEqual(self.vm.stack.size(), 1)
        self.assertEqual(self.vm.stack.pop(), True)
    
    def test_jump_instructions(self):
        """测试跳转指令"""
        constants = [
            Constant(True, DataType.BOOL),
            Constant(1, DataType.INT),
            Constant(2, DataType.INT)
        ]
        symbols = []
        instructions = [
            Instruction(OpCode.LOAD_CONST, 0),    # 0: 加载True
            Instruction(OpCode.JUMP_IF_TRUE, 4),  # 1: 如果真则跳转到4
            Instruction(OpCode.LOAD_CONST, 1),    # 2: 加载1 (应该被跳过)
            Instruction(OpCode.JUMP, 5),          # 3: 跳转到5 (应该被跳过)
            Instruction(OpCode.LOAD_CONST, 2),    # 4: 加载2
            Instruction(OpCode.HALT)              # 5: 结束
        ]
        
        self.vm.load_program(constants, symbols, instructions)
        self.vm.run()
        
        # 检查结果：应该只有常量2在栈中
        self.assertEqual(self.vm.stack.size(), 1)
        self.assertEqual(self.vm.stack.pop(), 2)


class TestVMIntegration(unittest.TestCase):
    """虚拟机集成测试"""
    
    def test_simple_program(self):
        """测试简单程序执行"""
        # 程序: x = 10; y = 20; result = x + y
        constants = [
            Constant(10, DataType.INT),   # 0
            Constant(20, DataType.INT),   # 1
        ]
        symbols = [
            Symbol("x", SymbolType.VAR, 0),      # 变量x -> 索引0
            Symbol("y", SymbolType.VAR, 1),      # 变量y -> 索引1
            Symbol("result", SymbolType.VAR, 2), # 变量result -> 索引2
        ]
        instructions = [
            Instruction(OpCode.LOAD_CONST, 0),   # 加载10
            Instruction(OpCode.STORE_VAR, 0),    # x = 10
            Instruction(OpCode.LOAD_CONST, 1),   # 加载20
            Instruction(OpCode.STORE_VAR, 1),    # y = 20
            Instruction(OpCode.LOAD_VAR, 0),     # 加载x
            Instruction(OpCode.LOAD_VAR, 1),     # 加载y
            Instruction(OpCode.ADD),             # x + y
            Instruction(OpCode.STORE_VAR, 2),    # result = x + y
            Instruction(OpCode.HALT)
        ]
        
        vm = PyVirtualMachine()
        vm.load_program(constants, symbols, instructions)
        vm.run()
        
        # 检查变量值
        self.assertEqual(vm.variables[0], 10)    # x
        self.assertEqual(vm.variables[1], 20)    # y
        self.assertEqual(vm.variables[2], 30)    # result
        self.assertTrue(vm.stack.is_empty())     # 栈应该为空


if __name__ == '__main__':
    unittest.main()

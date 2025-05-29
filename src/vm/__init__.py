"""
PyVM虚拟机模块
"""

from .instructions import *
from .stack import VMStack, CallStack, CallFrame
from .machine import PyVirtualMachine, VMError
from .bytecode_file import BytecodeFile

def disassemble(instructions):
    """反汇编指令序列"""
    result = []
    for i, instruction in enumerate(instructions):
        if instruction.operand is not None:
            line = f"{i:04d}: {instruction.opcode.name:<12} {instruction.operand}"
        else:
            line = f"{i:04d}: {instruction.opcode.name}"
        result.append(line)
    return '\n'.join(result)

__all__ = [
    'OpCode', 'DataType', 'SymbolType',
    'Instruction', 'Constant', 'Symbol',
    'VMStack', 'CallStack', 'CallFrame',
    'PyVirtualMachine', 'VMError',
    'BytecodeFile', 'disassemble'
]

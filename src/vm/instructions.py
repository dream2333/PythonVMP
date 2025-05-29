"""
PyVM指令定义模块
定义虚拟机的所有指令操作码和相关常量
"""

from enum import IntEnum
from typing import Any, List


class OpCode(IntEnum):
    """操作码枚举"""
    # 栈操作指令 (0x00-0x0F)
    NOP = 0x00          # 空操作
    LOAD_CONST = 0x01   # 加载常量
    LOAD_VAR = 0x02     # 加载变量
    STORE_VAR = 0x03    # 存储变量
    POP = 0x04          # 弹出栈顶
    DUP = 0x05          # 复制栈顶

    # 算术运算指令 (0x10-0x1F)
    ADD = 0x10          # 加法
    SUB = 0x11          # 减法
    MUL = 0x12          # 乘法
    DIV = 0x13          # 除法
    MOD = 0x14          # 取模
    NEG = 0x15          # 取负

    # 比较运算指令 (0x20-0x2F)
    CMP_EQ = 0x20       # 相等
    CMP_NE = 0x21       # 不等
    CMP_LT = 0x22       # 小于
    CMP_LE = 0x23       # 小于等于
    CMP_GT = 0x24       # 大于
    CMP_GE = 0x25       # 大于等于

    # 控制流指令 (0x30-0x3F)
    JUMP = 0x30         # 无条件跳转
    JUMP_IF_FALSE = 0x31 # 假时跳转
    JUMP_IF_TRUE = 0x32  # 真时跳转
    CALL = 0x33         # 函数调用
    RETURN = 0x34       # 函数返回

    # 内置函数指令 (0x40-0x4F)
    PRINT = 0x40        # 打印
    INPUT = 0x41        # 输入

    # 程序控制指令
    HALT = 0xFF         # 程序结束


class DataType(IntEnum):
    """数据类型枚举"""
    INT = 0x01          # 整数
    FLOAT = 0x02        # 浮点数
    STRING = 0x03       # 字符串
    BOOL = 0x04         # 布尔值


class SymbolType(IntEnum):
    """符号类型枚举"""
    VAR = 0x01          # 变量
    FUNC = 0x02         # 函数


class Instruction:
    """指令类"""
    
    def __init__(self, opcode: OpCode, operand: int = None):
        self.opcode = opcode
        self.operand = operand
    
    def __str__(self):
        if self.operand is not None:
            return f"{self.opcode.name} {self.operand}"
        return self.opcode.name
    
    def __repr__(self):
        return f"Instruction({self.opcode.name}, {self.operand})"


class Constant:
    """常量类"""
    
    def __init__(self, value: Any, data_type: DataType):
        self.value = value
        self.data_type = data_type
    
    def __str__(self):
        return f"{self.data_type.name}({self.value})"
    
    def __repr__(self):
        return f"Constant({self.value}, {self.data_type.name})"


class Symbol:
    """符号类"""
    
    def __init__(self, name: str, symbol_type: SymbolType, index: int):
        self.name = name
        self.symbol_type = symbol_type
        self.index = index
    
    def __str__(self):
        return f"{self.symbol_type.name}({self.name})[{self.index}]"
    
    def __repr__(self):
        return f"Symbol({self.name}, {self.symbol_type.name}, {self.index})"


# 指令属性映射
INSTRUCTION_INFO = {
    # 指令: (助记符, 是否有操作数, 描述)
    OpCode.NOP: ("NOP", False, "空操作"),
    OpCode.LOAD_CONST: ("LOAD_CONST", True, "加载常量到栈顶"),
    OpCode.LOAD_VAR: ("LOAD_VAR", True, "加载变量到栈顶"),
    OpCode.STORE_VAR: ("STORE_VAR", True, "将栈顶值存储到变量"),
    OpCode.POP: ("POP", False, "弹出栈顶元素"),
    OpCode.DUP: ("DUP", False, "复制栈顶元素"),
    
    OpCode.ADD: ("ADD", False, "加法运算"),
    OpCode.SUB: ("SUB", False, "减法运算"),
    OpCode.MUL: ("MUL", False, "乘法运算"),
    OpCode.DIV: ("DIV", False, "除法运算"),
    OpCode.MOD: ("MOD", False, "取模运算"),
    OpCode.NEG: ("NEG", False, "取负运算"),
    
    OpCode.CMP_EQ: ("CMP_EQ", False, "相等比较"),
    OpCode.CMP_NE: ("CMP_NE", False, "不等比较"),
    OpCode.CMP_LT: ("CMP_LT", False, "小于比较"),
    OpCode.CMP_LE: ("CMP_LE", False, "小于等于比较"),
    OpCode.CMP_GT: ("CMP_GT", False, "大于比较"),
    OpCode.CMP_GE: ("CMP_GE", False, "大于等于比较"),
    
    OpCode.JUMP: ("JUMP", True, "无条件跳转"),
    OpCode.JUMP_IF_FALSE: ("JUMP_IF_FALSE", True, "条件跳转(假)"),
    OpCode.JUMP_IF_TRUE: ("JUMP_IF_TRUE", True, "条件跳转(真)"),
    OpCode.CALL: ("CALL", True, "函数调用"),
    OpCode.RETURN: ("RETURN", False, "函数返回"),
    
    OpCode.PRINT: ("PRINT", False, "打印栈顶值"),
    OpCode.INPUT: ("INPUT", False, "读取输入"),
    
    OpCode.HALT: ("HALT", False, "程序结束"),
}


def get_instruction_info(opcode: OpCode) -> tuple:
    """获取指令信息"""
    return INSTRUCTION_INFO.get(opcode, ("UNKNOWN", False, "未知指令"))


def format_instruction(instruction: Instruction) -> str:
    """格式化指令为可读字符串"""
    mnemonic, has_operand, description = get_instruction_info(instruction.opcode)
    if has_operand and instruction.operand is not None:
        return f"{mnemonic} {instruction.operand:>3}"
    return f"{mnemonic:<12}"


def disassemble(instructions: List[Instruction]) -> str:
    """反汇编指令序列"""
    lines = []
    for i, inst in enumerate(instructions):
        addr = f"{i:04d}:"
        formatted = format_instruction(inst)
        lines.append(f"{addr} {formatted}")
    return "\n".join(lines)

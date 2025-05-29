"""
PyVM字节码文件处理模块
支持将编译后的字节码保存为二进制文件和从二进制文件加载
"""

import struct
import os
from typing import List, Tuple, BinaryIO
from .instructions import Instruction, OpCode, Constant, Symbol, DataType, SymbolType


class BytecodeFile:
    """字节码文件处理类"""
    
    # 文件格式常量
    MAGIC_NUMBER = 0x50594D56  # "PYMV"
    VERSION = 0x0001
    
    @staticmethod
    def save_bytecode(filepath: str, constants: List[Constant], 
                     symbols: List[Symbol], instructions: List[Instruction]) -> None:
        """保存字节码到二进制文件"""
        with open(filepath, 'wb') as f:
            # 写入文件头
            BytecodeFile._write_header(f, constants, symbols, instructions)
            
            # 写入常量池
            BytecodeFile._write_constants(f, constants)
            
            # 写入符号表
            BytecodeFile._write_symbols(f, symbols)
            
            # 写入指令序列
            BytecodeFile._write_instructions(f, instructions)
    
    @staticmethod
    def load_bytecode(filepath: str) -> Tuple[List[Constant], List[Symbol], List[Instruction]]:
        """从二进制文件加载字节码"""
        with open(filepath, 'rb') as f:
            # 读取并验证文件头
            header = BytecodeFile._read_header(f)
            
            # 读取常量池
            constants = BytecodeFile._read_constants(f, header['const_count'])
            
            # 读取符号表
            symbols = BytecodeFile._read_symbols(f, header['symbol_count'])
            
            # 读取指令序列
            instructions = BytecodeFile._read_instructions(f, header['code_size'])
            
            return constants, symbols, instructions
    
    @staticmethod
    def _write_header(f: BinaryIO, constants: List[Constant], 
                     symbols: List[Symbol], instructions: List[Instruction]) -> None:
        """写入文件头"""
        # 计算代码段大小
        code_size = len(instructions) * 2  # 每条指令2字节
        
        # 写入文件头
        f.write(struct.pack('<I', BytecodeFile.MAGIC_NUMBER))  # 魔数
        f.write(struct.pack('<H', BytecodeFile.VERSION))       # 版本
        f.write(struct.pack('<H', 0))                          # 标志位
        f.write(struct.pack('<I', len(constants)))             # 常量数量
        f.write(struct.pack('<I', len(symbols)))               # 符号数量
        f.write(struct.pack('<I', code_size))                  # 代码大小
    
    @staticmethod
    def _read_header(f: BinaryIO) -> dict:
        """读取文件头"""
        magic = struct.unpack('<I', f.read(4))[0]
        if magic != BytecodeFile.MAGIC_NUMBER:
            raise ValueError(f"无效的字节码文件：魔数不匹配 (0x{magic:08X})")
        
        version = struct.unpack('<H', f.read(2))[0]
        if version != BytecodeFile.VERSION:
            raise ValueError(f"不支持的版本：{version}")
        
        flags = struct.unpack('<H', f.read(2))[0]
        const_count = struct.unpack('<I', f.read(4))[0]
        symbol_count = struct.unpack('<I', f.read(4))[0]
        code_size = struct.unpack('<I', f.read(4))[0]
        
        return {
            'version': version,
            'flags': flags,
            'const_count': const_count,
            'symbol_count': symbol_count,
            'code_size': code_size
        }
    
    @staticmethod
    def _write_constants(f: BinaryIO, constants: List[Constant]) -> None:
        """写入常量池"""
        for const in constants:
            # 写入数据类型
            f.write(struct.pack('<B', const.data_type.value))
            
            if const.data_type == DataType.INT:
                # 整数：4字节大小 + 数据
                f.write(struct.pack('<I', 4))
                f.write(struct.pack('<i', const.value))
            elif const.data_type == DataType.FLOAT:
                # 浮点数：8字节大小 + 数据
                f.write(struct.pack('<I', 8))
                f.write(struct.pack('<d', const.value))
            elif const.data_type == DataType.STRING:
                # 字符串：长度 + UTF-8数据 + null终止符
                data = const.value.encode('utf-8') + b'\x00'
                f.write(struct.pack('<I', len(data)))
                f.write(data)
            elif const.data_type == DataType.BOOL:
                # 布尔值：1字节大小 + 数据
                f.write(struct.pack('<I', 1))
                f.write(struct.pack('<B', 1 if const.value else 0))
    
    @staticmethod
    def _read_constants(f: BinaryIO, count: int) -> List[Constant]:
        """读取常量池"""
        constants = []
        
        for _ in range(count):
            data_type = DataType(struct.unpack('<B', f.read(1))[0])
            size = struct.unpack('<I', f.read(4))[0]
            
            if data_type == DataType.INT:
                value = struct.unpack('<i', f.read(4))[0]
            elif data_type == DataType.FLOAT:
                value = struct.unpack('<d', f.read(8))[0]
            elif data_type == DataType.STRING:
                data = f.read(size)
                value = data[:-1].decode('utf-8')  # 去掉null终止符
            elif data_type == DataType.BOOL:
                value = bool(struct.unpack('<B', f.read(1))[0])
            else:
                raise ValueError(f"未知的数据类型：{data_type}")
            
            constants.append(Constant(value, data_type))
        
        return constants
    
    @staticmethod
    def _write_symbols(f: BinaryIO, symbols: List[Symbol]) -> None:
        """写入符号表"""
        for symbol in symbols:
            # 写入符号类型
            f.write(struct.pack('<B', symbol.symbol_type.value))
            
            # 写入名称长度和名称（带null终止符）
            name_data = symbol.name.encode('utf-8') + b'\x00'
            f.write(struct.pack('<B', len(name_data)))
            f.write(name_data)
            
            # 写入符号索引
            f.write(struct.pack('<I', symbol.index))
    
    @staticmethod
    def _read_symbols(f: BinaryIO, count: int) -> List[Symbol]:
        """读取符号表"""
        symbols = []
        
        for _ in range(count):
            symbol_type = SymbolType(struct.unpack('<B', f.read(1))[0])
            name_len = struct.unpack('<B', f.read(1))[0]
            name_data = f.read(name_len)
            name = name_data[:-1].decode('utf-8')  # 去掉null终止符
            symbol_index = struct.unpack('<I', f.read(4))[0]
            
            symbols.append(Symbol(name, symbol_type, symbol_index))
        
        return symbols
    
    @staticmethod
    def _write_instructions(f: BinaryIO, instructions: List[Instruction]) -> None:
        """写入指令序列"""
        for instruction in instructions:
            # 写入操作码
            f.write(struct.pack('<B', instruction.opcode.value))
              # 写入操作数
            if instruction.operand is not None:
                f.write(struct.pack('<B', instruction.operand))
            else:
                f.write(struct.pack('<B', 0))
    
    @staticmethod
    def _read_instructions(f: BinaryIO, code_size: int) -> List[Instruction]:
        """读取指令序列"""
        instructions = []
        bytes_read = 0
        
        while bytes_read < code_size:
            opcode_value = struct.unpack('<B', f.read(1))[0]
            operand_value = struct.unpack('<B', f.read(1))[0]
            
            opcode = OpCode(opcode_value)
            
            # 根据指令类型确定是否需要操作数
            from .instructions import INSTRUCTION_INFO
            _, has_operand, _ = INSTRUCTION_INFO.get(opcode, ("UNKNOWN", False, ""))
            
            if has_operand:
                operand = operand_value
            else:
                operand = None
                
            instruction = Instruction(opcode, operand)
            instructions.append(instruction)
            
            bytes_read += 2
        
        return instructions
    
    @staticmethod
    def get_file_info(filepath: str) -> dict:
        """获取字节码文件信息"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"文件不存在：{filepath}")
        
        with open(filepath, 'rb') as f:
            header = BytecodeFile._read_header(f)
            
            file_size = os.path.getsize(filepath)
            
            return {
                'filepath': filepath,
                'file_size': file_size,
                'version': header['version'],
                'const_count': header['const_count'],
                'symbol_count': header['symbol_count'],
                'code_size': header['code_size'],
                'header_size': 20,  # 固定的文件头大小
            }


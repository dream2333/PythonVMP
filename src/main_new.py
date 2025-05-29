"""
PyVM主程序入口
提供命令行接口来编译和运行Python代码
支持生成和执行二进制字节码文件
"""

import sys
import os
import argparse
from pathlib import Path
from typing import Optional

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from compiler import tokenize, parse, generate_code, LexerError, ParseError, CodeGenError
from vm import PyVirtualMachine, VMError, disassemble, BytecodeFile


def read_file(filepath: str) -> str:
    """读取源文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"错误: 文件未找到 '{filepath}'", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"错误: 读取文件失败 '{filepath}': {e}", file=sys.stderr)
        sys.exit(1)


def compile_source(source: str, debug: bool = False) -> tuple:
    """编译源代码"""
    try:
        # 词法分析
        if debug:
            print("=== 词法分析 ===")
        tokens = tokenize(source)
        
        if debug:
            print("Tokens:")
            for token in tokens:
                print(f"  {token}")
            print()
        
        # 语法分析
        if debug:
            print("=== 语法分析 ===")
        ast = parse(tokens)
        
        if debug:
            print(f"AST: {ast}")
            print()
        
        # 代码生成
        if debug:
            print("=== 代码生成 ===")
        constants, symbols, instructions = generate_code(ast)
        
        if debug:
            print("字节码生成完成")
            print()
        
        return constants, symbols, instructions
    
    except LexerError as e:
        print(f"词法分析错误: {e}", file=sys.stderr)
        sys.exit(1)
    except ParseError as e:
        print(f"语法分析错误: {e}", file=sys.stderr)
        sys.exit(1)
    except CodeGenError as e:
        print(f"代码生成错误: {e}", file=sys.stderr)
        sys.exit(1)


def compile_to_bytecode(source_file: str, output_file: str = None, debug: bool = False) -> str:
    """编译源文件到字节码文件"""
    if output_file is None:
        # 自动生成输出文件名：将.py替换为.pvm
        output_file = source_file.rsplit('.', 1)[0] + '.pvm'
    
    # 读取源文件
    source = read_file(source_file)
    
    # 编译源代码
    constants, symbols, instructions = compile_source(source, debug)
    
    # 保存字节码
    try:
        BytecodeFile.save_bytecode(output_file, constants, symbols, instructions)
        if debug:
            print(f"字节码已保存到: {output_file}")
        return output_file
    except Exception as e:
        print(f"错误: 保存字节码失败: {e}", file=sys.stderr)
        sys.exit(1)


def run_bytecode(constants, symbols, instructions, debug: bool = False, 
                 show_performance: bool = False) -> None:
    """运行字节码"""
    try:
        vm = PyVirtualMachine(debug=debug)
        vm.load_program(constants, symbols, instructions)
        vm.run()
        
        if show_performance:
            print("\n" + vm.get_performance_report())
    except VMError as e:
        print(f"虚拟机运行错误: {e}", file=sys.stderr)
        sys.exit(1)


def run_bytecode_file(bytecode_file: str, debug: bool = False, 
                     show_performance: bool = False) -> None:
    """运行字节码文件"""
    try:
        # 加载字节码
        constants, symbols, instructions = BytecodeFile.load_bytecode(bytecode_file)
        
        if debug:
            print(f"从 {bytecode_file} 加载字节码成功")
            print(f"常量: {len(constants)}, 符号: {len(symbols)}, 指令: {len(instructions)}")
        
        # 运行字节码
        run_bytecode(constants, symbols, instructions, debug, show_performance)
        
    except FileNotFoundError:
        print(f"错误: 字节码文件不存在 '{bytecode_file}'", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"错误: 无效的字节码文件: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"错误: 加载字节码失败: {e}", file=sys.stderr)
        sys.exit(1)


def show_bytecode(constants, symbols, instructions) -> None:
    """显示字节码"""
    print("=== PyVM字节码 ===")
    
    # 常量池
    print("\n常量池:")
    for i, const in enumerate(constants):
        print(f"  [{i:2d}] {const}")
    
    # 符号表
    print("\n符号表:")
    for i, symbol in enumerate(symbols):
        print(f"  [{i:2d}] {symbol}")
    
    # 指令序列
    print("\n指令序列:")
    disasm = disassemble(instructions)
    for line in disasm.split('\n'):
        print(f"  {line}")


def show_bytecode_file_info(bytecode_file: str) -> None:
    """显示字节码文件信息"""
    try:
        info = BytecodeFile.get_file_info(bytecode_file)
        
        print("=== 字节码文件信息 ===")
        print(f"文件路径: {info['filepath']}")
        print(f"文件大小: {info['file_size']} 字节")
        print(f"版本: {info['version']}")
        print(f"常量数量: {info['const_count']}")
        print(f"符号数量: {info['symbol_count']}")
        print(f"代码大小: {info['code_size']} 字节")
        print(f"文件头大小: {info['header_size']} 字节")
        
        # 计算各部分占比
        total_size = info['file_size']
        header_percent = (info['header_size'] / total_size) * 100
        code_percent = (info['code_size'] / total_size) * 100
        
        print(f"\n大小分布:")
        print(f"  文件头: {header_percent:.1f}%")
        print(f"  代码段: {code_percent:.1f}%")
        print(f"  其他数据: {100 - header_percent - code_percent:.1f}%")
        
    except Exception as e:
        print(f"错误: 无法读取文件信息: {e}", file=sys.stderr)
        sys.exit(1)


def interactive_mode():
    """交互模式"""
    print("PyVM交互模式 (输入 'exit' 退出)")
    vm = PyVirtualMachine(debug=False)
    
    while True:
        try:
            line = input(">>> ")
            if line.strip().lower() == 'exit':
                break
            
            if not line.strip():
                continue
            
            # 编译并运行
            constants, symbols, instructions = compile_source(line)
            vm.load_program(constants, symbols, instructions)
            vm.run()
            
        except KeyboardInterrupt:
            print("\n退出交互模式")
            break
        except EOFError:
            print("\n退出交互模式")
            break
        except Exception as e:
            print(f"错误: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="PyVM - Python虚拟机",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py hello.py                    # 运行Python文件
  python main.py hello.py --debug            # 调试模式运行
  python main.py hello.py --show-bytecode    # 显示字节码
  python main.py hello.py --compile          # 编译为.pvm文件
  python main.py hello.pvm                   # 运行.pvm字节码文件
  python main.py hello.pvm --info            # 显示.pvm文件信息
  python main.py --interactive               # 交互模式        """
    )
    
    parser.add_argument('file', nargs='?', help='Python源文件(.py)或字节码文件(.pvm)')
    parser.add_argument('--debug', '-d', action='store_true', 
                       help='启用调试模式')
    parser.add_argument('--show-bytecode', '-s', action='store_true',
                       help='显示字节码而不执行')
    parser.add_argument('--performance', '-p', action='store_true',
                       help='显示性能报告')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='进入交互模式')
    parser.add_argument('--compile', '-c', action='store_true',
                       help='编译为字节码文件(.pvm)')
    parser.add_argument('--output', '-o', type=str,
                       help='指定输出文件名（用于--compile）')
    parser.add_argument('--info', action='store_true',
                       help='显示字节码文件信息（用于.pvm文件）')
    
    args = parser.parse_args()
    
    # 交互模式
    if args.interactive:
        interactive_mode()
        return
    
    # 需要文件参数
    if not args.file:
        print("错误: 需要指定源文件或字节码文件，或使用 --interactive 进入交互模式", file=sys.stderr)
        parser.print_help()
        sys.exit(1)
    
    # 检查文件是否存在
    if not Path(args.file).exists():
        print(f"错误: 文件不存在 '{args.file}'", file=sys.stderr)
        sys.exit(1)
    
    # 判断文件类型
    file_ext = Path(args.file).suffix.lower()
    
    if file_ext == '.pvm':
        # 字节码文件
        if args.info:
            show_bytecode_file_info(args.file)
        elif args.show_bytecode:
            # 加载字节码并显示
            constants, symbols, instructions = BytecodeFile.load_bytecode(args.file)
            show_bytecode(constants, symbols, instructions)
        else:
            run_bytecode_file(args.file, args.debug, args.performance)
    
    elif file_ext == '.py':
        # Python源文件
        if args.compile:
            # 编译模式
            output_file = compile_to_bytecode(args.file, args.output, args.debug)
            print(f"编译完成: {args.file} -> {output_file}")
        else:
            # 运行模式
            source = read_file(args.file)
            constants, symbols, instructions = compile_source(source, args.debug)
            
            if args.show_bytecode:
                show_bytecode(constants, symbols, instructions)
            else:
                run_bytecode(constants, symbols, instructions, args.debug, args.performance)
    
    else:
        print(f"错误: 不支持的文件类型 '{file_ext}'. 支持 .py 和 .pvm 文件", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

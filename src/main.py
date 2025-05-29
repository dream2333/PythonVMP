"""
PyVM主程序入口
提供命令行接口来编译和运行Python代码
"""

import sys
import os
import argparse
from pathlib import Path
from typing import Optional

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from compiler import tokenize, parse, generate_code, LexerError, ParseError, CodeGenError
from vm import PyVirtualMachine, VMError, disassemble


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
  python main.py hello.py              # 运行Python文件
  python main.py hello.py --debug      # 调试模式运行
  python main.py hello.py --show-bytecode  # 显示字节码
  python main.py --interactive         # 交互模式        """
    )
    
    parser.add_argument('file', nargs='?', help='Python源文件路径')
    parser.add_argument('--debug', '-d', action='store_true', 
                       help='启用调试模式')
    parser.add_argument('--show-bytecode', '-s', action='store_true',
                       help='显示字节码而不执行')
    parser.add_argument('--performance', '-p', action='store_true',
                       help='显示性能报告')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='进入交互模式')
    
    args = parser.parse_args()
    
    # 交互模式
    if args.interactive:
        interactive_mode()
        return
    
    # 需要文件参数
    if not args.file:
        print("错误: 需要指定Python源文件，或使用 --interactive 进入交互模式", file=sys.stderr)
        parser.print_help()
        sys.exit(1)
    
    # 检查文件是否存在
    if not Path(args.file).exists():
        print(f"错误: 文件不存在 '{args.file}'", file=sys.stderr)
        sys.exit(1)
    
    # 读取并编译源文件
    source = read_file(args.file)
    constants, symbols, instructions = compile_source(source, args.debug)
      # 显示字节码或运行程序
    if args.show_bytecode:
        show_bytecode(constants, symbols, instructions)
    else:
        run_bytecode(constants, symbols, instructions, args.debug, args.performance)


if __name__ == '__main__':
    main()

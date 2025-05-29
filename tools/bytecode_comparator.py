"""
PyVM字节码比较工具
比较不同实现的字节码差异和性能
"""

import sys
import os
import time
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

from compiler import tokenize, parse, generate_code
from vm import PyVirtualMachine, disassemble


class BytecodeComparator:
    """字节码比较器"""
    
    def compare_implementations(self, source1: str, source2: str, name1: str = "实现1", name2: str = "实现2"):
        """比较两个实现的字节码和性能"""
        print(f"=== 字节码比较: {name1} vs {name2} ===\n")
        
        # 编译两个实现
        print("编译两个实现...")
        impl1 = self.compile_and_analyze(source1, name1)
        impl2 = self.compile_and_analyze(source2, name2)
        
        # 比较字节码
        print(f"\n{'='*60}")
        print("字节码比较:")
        print(f"{'='*60}")
        self.compare_bytecode(impl1, impl2, name1, name2)
        
        # 比较性能
        print(f"\n{'='*60}")
        print("性能比较:")
        print(f"{'='*60}")
        self.compare_performance(impl1, impl2, name1, name2)
        
        return impl1, impl2
    
    def compile_and_analyze(self, source: str, name: str) -> dict:
        """编译并分析源代码"""
        print(f"\n编译 {name}...")
        
        # 编译
        compile_start = time.time()
        tokens = tokenize(source)
        ast = parse(tokens)
        constants, symbols, instructions = generate_code(ast)
        compile_time = time.time() - compile_start
          # 执行
        vm = PyVirtualMachine(debug=False)
        vm.load_program(constants, symbols, instructions)
        
        exec_start = time.time()
        vm.run()
        exec_time = time.time() - exec_start
        
        return {
            'name': name,
            'source': source,
            'constants': constants,
            'symbols': symbols,
            'instructions': instructions,
            'compile_time': compile_time,
            'exec_time': exec_time,
            'vm': vm,
            'bytecode': disassemble(instructions)
        }
    
    def compare_bytecode(self, impl1: dict, impl2: dict, name1: str, name2: str):
        """比较字节码差异"""
        print(f"\n指令数量:")
        print(f"  {name1}: {len(impl1['instructions'])} 条指令")
        print(f"  {name2}: {len(impl2['instructions'])} 条指令")
        print(f"  差异: {len(impl2['instructions']) - len(impl1['instructions'])} 条")
        
        print(f"\n常量数量:")
        print(f"  {name1}: {len(impl1['constants'])} 个常量")
        print(f"  {name2}: {len(impl2['constants'])} 个常量")
        
        print(f"\n符号数量:")
        print(f"  {name1}: {len(impl1['symbols'])} 个符号")
        print(f"  {name2}: {len(impl2['symbols'])} 个符号")
        
        # 显示字节码
        print(f"\n{name1} 字节码:")
        print("-" * 40)
        for i, line in enumerate(impl1['bytecode'].split('\n')[:10]):  # 只显示前10行
            print(f"{i:2d}: {line}")
        if len(impl1['bytecode'].split('\n')) > 10:
            print("    ...")
        
        print(f"\n{name2} 字节码:")
        print("-" * 40)
        for i, line in enumerate(impl2['bytecode'].split('\n')[:10]):  # 只显示前10行
            print(f"{i:2d}: {line}")
        if len(impl2['bytecode'].split('\n')) > 10:
            print("    ...")
    
    def compare_performance(self, impl1: dict, impl2: dict, name1: str, name2: str):
        """比较性能差异"""
        vm1, vm2 = impl1['vm'], impl2['vm']
        
        print(f"\n编译时间:")
        print(f"  {name1}: {impl1['compile_time']:.4f}秒")
        print(f"  {name2}: {impl2['compile_time']:.4f}秒")
        compile_diff = impl2['compile_time'] - impl1['compile_time']
        print(f"  差异: {compile_diff:+.4f}秒 ({compile_diff/impl1['compile_time']*100:+.1f}%)")
        
        print(f"\n执行时间:")
        print(f"  {name1}: {impl1['exec_time']:.4f}秒")
        print(f"  {name2}: {impl2['exec_time']:.4f}秒")
        exec_diff = impl2['exec_time'] - impl1['exec_time']
        if impl1['exec_time'] > 0:
            print(f"  差异: {exec_diff:+.4f}秒 ({exec_diff/impl1['exec_time']*100:+.1f}%)")
        
        print(f"\n执行指令数:")
        print(f"  {name1}: {vm1.instruction_count}")
        print(f"  {name2}: {vm2.instruction_count}")
        
        ips1 = vm1.instruction_count / impl1['exec_time'] if impl1['exec_time'] > 0 else 0
        ips2 = vm2.instruction_count / impl2['exec_time'] if impl2['exec_time'] > 0 else 0
        print(f"\n执行速度:")
        print(f"  {name1}: {ips1:.0f} 指令/秒")
        print(f"  {name2}: {ips2:.0f} 指令/秒")
        
        # 胜负判定
        print(f"\n性能总结:")
        if len(impl1['instructions']) < len(impl2['instructions']):
            print(f"  🏆 {name1} 字节码更紧凑")
        elif len(impl1['instructions']) > len(impl2['instructions']):
            print(f"  🏆 {name2} 字节码更紧凑")
        else:
            print(f"  🤝 字节码大小相同")
        
        if ips1 > ips2:
            print(f"  🏆 {name1} 执行更快")
        elif ips1 < ips2:
            print(f"  🏆 {name2} 执行更快")
        else:
            print(f"  🤝 执行速度相同")


def demo_comparison():
    """演示比较功能"""
    # 两种不同的斐波那契实现
    fib_iterative = '''
# 迭代版本斐波那契
n = 10
a = 0
b = 1
i = 2
while i <= n:
    temp = a + b
    a = b
    b = temp
    i = i + 1
print(b)
'''
    
    fib_simple = '''
# 简化版本斐波那契
n = 10
result = 1
prev = 0
count = 1
while count < n:
    next_val = result + prev
    prev = result
    result = next_val
    count = count + 1
print(result)
'''
    
    comparator = BytecodeComparator()
    comparator.compare_implementations(
        fib_iterative, fib_simple, 
        "迭代版斐波那契", "简化版斐波那契"
    )


def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo_comparison()
    else:
        print("PyVM字节码比较工具")
        print("用法:")
        print("  python bytecode_comparator.py demo  # 运行演示比较")
        print("\n此工具可用于:")
        print("  - 比较不同算法实现的效率")
        print("  - 分析编译器优化效果")
        print("  - 学习字节码生成规律")


if __name__ == "__main__":
    main()

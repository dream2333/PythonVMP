"""
PyVM高级性能分析工具
提供深度性能分析和优化建议
"""

import sys
import os
import time
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

from compiler import tokenize, parse, generate_code
from vm import PyVirtualMachine, disassemble


class PerformanceAnalyzer:
    """性能分析器"""
    
    def __init__(self):
        self.results = {}
    
    def analyze_file(self, filepath: str, iterations: int = 1) -> dict:
        """分析单个文件的性能"""
        print(f"=== 分析文件: {filepath} ===")
        
        # 读取源文件
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # 编译
        print("编译阶段...")
        compile_start = time.time()
        tokens = tokenize(source)
        ast = parse(tokens)
        constants, symbols, instructions = generate_code(ast)
        compile_time = time.time() - compile_start
        
        print(f"编译完成 - 耗时: {compile_time:.4f}秒")
        print(f"生成指令数: {len(instructions)}")
        print(f"常量数: {len(constants)}")
        print(f"符号数: {len(symbols)}")
        
        # 字节码分析
        print("\n字节码分析:")
        bytecode_info = self.analyze_bytecode(instructions)
        
        # 执行性能测试
        print(f"\n执行性能测试 (迭代次数: {iterations})...")
        execution_results = []
        
        for i in range(iterations):
            vm = PyVirtualMachine(debug=False)
            vm.load_program(constants, symbols, instructions)
            
            start_time = time.time()
            vm.run()
            end_time = time.time()
            
            exec_time = end_time - start_time
            execution_results.append({
                'execution_time': exec_time,
                'instruction_count': vm.instruction_count,
                'instructions_per_second': vm.instruction_count / exec_time if exec_time > 0 else 0,
                'performance_report': vm.get_performance_report()
            })
        
        # 统计结果
        avg_exec_time = sum(r['execution_time'] for r in execution_results) / iterations
        avg_inst_count = sum(r['instruction_count'] for r in execution_results) / iterations
        avg_ips = sum(r['instructions_per_second'] for r in execution_results) / iterations
        
        result = {
            'filepath': filepath,
            'compile_time': compile_time,
            'bytecode_info': bytecode_info,
            'execution_stats': {
                'iterations': iterations,
                'avg_execution_time': avg_exec_time,
                'avg_instruction_count': avg_inst_count,
                'avg_instructions_per_second': avg_ips,
                'min_execution_time': min(r['execution_time'] for r in execution_results),
                'max_execution_time': max(r['execution_time'] for r in execution_results),
            },
            'latest_performance_report': execution_results[-1]['performance_report'] if execution_results else None
        }
        
        self.results[filepath] = result
        return result
    
    def analyze_bytecode(self, instructions) -> dict:
        """分析字节码特征"""
        opcode_counts = {}
        total_instructions = len(instructions)
        
        for instruction in instructions:
            opcode = instruction.opcode.name
            opcode_counts[opcode] = opcode_counts.get(opcode, 0) + 1
        
        # 计算复杂度指标
        unique_opcodes = len(opcode_counts)
        most_common = max(opcode_counts.items(), key=lambda x: x[1])
        
        return {
            'total_instructions': total_instructions,
            'unique_opcodes': unique_opcodes,
            'opcode_distribution': opcode_counts,
            'most_common_opcode': most_common,
            'complexity_score': unique_opcodes / total_instructions if total_instructions > 0 else 0
        }
    
    def print_analysis_report(self, result: dict):
        """打印分析报告"""
        print(f"\n{'='*50}")
        print(f"性能分析报告: {result['filepath']}")
        print(f"{'='*50}")
        
        # 编译信息
        print(f"\n编译性能:")
        print(f"  编译时间: {result['compile_time']:.4f}秒")
        
        # 字节码信息
        bytecode = result['bytecode_info']
        print(f"\n字节码分析:")
        print(f"  总指令数: {bytecode['total_instructions']}")
        print(f"  唯一操作码: {bytecode['unique_opcodes']}")
        print(f"  复杂度分数: {bytecode['complexity_score']:.3f}")
        print(f"  最常见操作: {bytecode['most_common_opcode'][0]} ({bytecode['most_common_opcode'][1]}次)")
        
        # 执行性能
        exec_stats = result['execution_stats']
        print(f"\n执行性能:")
        print(f"  测试迭代: {exec_stats['iterations']}")
        print(f"  平均执行时间: {exec_stats['avg_execution_time']:.4f}秒")
        print(f"  平均指令数: {exec_stats['avg_instruction_count']:.0f}")
        print(f"  平均执行速度: {exec_stats['avg_instructions_per_second']:.0f} 指令/秒")
        print(f"  最快执行: {exec_stats['min_execution_time']:.4f}秒")
        print(f"  最慢执行: {exec_stats['max_execution_time']:.4f}秒")
        
        # 性能建议
        self.print_optimization_suggestions(result)
    
    def print_optimization_suggestions(self, result: dict):
        """打印优化建议"""
        print(f"\n优化建议:")
        
        exec_stats = result['execution_stats']
        bytecode = result['bytecode_info']
        
        # 执行速度建议
        avg_ips = exec_stats['avg_instructions_per_second']
        if avg_ips < 100000:
            print("  ⚠️  执行速度较慢，考虑减少复杂计算")
        elif avg_ips > 1000000:
            print("  ✅ 执行速度优秀")
        else:
            print("  ✓  执行速度良好")
        
        # 字节码复杂度建议
        complexity = bytecode['complexity_score']
        if complexity > 0.5:
            print("  ✅ 代码结构复杂，指令多样性高")
        elif complexity < 0.1:
            print("  ⚠️  代码结构简单，可能存在优化空间")
        else:
            print("  ✓  代码复杂度适中")
        
        # 指令分布建议
        most_common = bytecode['most_common_opcode']
        if most_common[1] > bytecode['total_instructions'] * 0.5:
            print(f"  ⚠️  操作 {most_common[0]} 使用频率过高 ({most_common[1]/bytecode['total_instructions']*100:.1f}%)")
        
        print("  💡 提示: 使用 --debug 模式查看详细执行过程")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python performance_analyzer.py <python_file> [iterations]")
        print("示例: python performance_analyzer.py ../examples/fibonacci.py 5")
        sys.exit(1)
    
    filepath = sys.argv[1]
    iterations = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    
    if not os.path.exists(filepath):
        print(f"错误: 文件不存在 '{filepath}'")
        sys.exit(1)
    
    analyzer = PerformanceAnalyzer()
    
    try:
        result = analyzer.analyze_file(filepath, iterations)
        analyzer.print_analysis_report(result)
        
    except Exception as e:
        print(f"分析失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

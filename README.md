# Python Virtual Machine (PyVM)

一个完整的Python虚拟机实现，支持将Python语法编译为自定义指令集并执行字节码。

## 项目概述

PyVM是一个教育性质的Python虚拟机，实现了从源代码到字节码的完整编译和执行流程。项目包含词法分析、语法分析、代码生成和虚拟机执行等核心组件。

## 功能特性

✅ **完整的编译管道**: 支持从Python源码到字节码的完整编译流程
✅ **自定义指令集**: 包含40+条指令，支持栈操作、算术运算、比较、控制流等
✅ **虚拟机执行**: 基于栈的虚拟机架构，支持变量管理、函数调用等
✅ **Python语法支持**: 
  - 变量赋值和算术运算
  - 条件语句（if/else）
  - 循环语句（while）
  - 函数调用（print, input）
  - 字符串和数字字面量
✅ **调试功能**: 提供字节码反汇编、执行跟踪和调试模式
✅ **测试覆盖**: 18个单元测试，覆盖编译器和虚拟机所有核心功能
✅ **丰富示例**: 包含hello world、计算器、斐波那契等示例程序

## 项目结构

```
vm/
├── README.md                 # 项目说明
├── docs/                     # 文档目录
│   ├── instruction_set.md    # 指令集文档
│   └── bytecode_format.md    # 字节码格式文档
├── src/                      # 源代码目录
│   ├── compiler/             # 编译器模块
│   │   ├── __init__.py
│   │   ├── lexer.py         # 词法分析器
│   │   ├── parser.py        # 语法分析器
│   │   └── codegen.py       # 代码生成器
│   ├── vm/                   # 虚拟机模块
│   │   ├── __init__.py
│   │   ├── instructions.py   # 指令定义
│   │   ├── stack.py         # 栈管理
│   │   └── machine.py       # 虚拟机核心
│   └── main.py              # 主程序入口
├── examples/                 # 示例代码
│   ├── hello.py             # 简单示例
│   ├── calculator.py        # 计算器示例
│   ├── fibonacci.py         # 斐波那契数列示例
│   ├── variables.py         # 变量操作示例
│   ├── loop.py              # 循环示例
│   └── comprehensive_test.py # 综合功能测试
├── tests/                    # 测试文件
│   ├── test_compiler.py
│   └── test_vm.py
└── requirements.txt          # 依赖包（仅Python标准库）
```

## 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 编译并运行Python代码
```bash
python src/main.py examples/hello.py
```

### 查看字节码
```bash
python src/main.py examples/hello.py --show-bytecode
```

## 支持的Python语法

- 变量赋值
- 基本运算 (+, -, *, /)
- 函数定义和调用
- 条件语句 (if/else)
- 循环语句 (while)
- 内置函数 (print)

## 开发指南

详细的指令集和字节码格式说明请参阅 `docs/` 目录下的文档。

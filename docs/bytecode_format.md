# PyVM字节码格式文档

PyVM字节码是编译器生成的二进制格式，包含程序的指令序列和元数据。

## 文件格式

PyVM字节码文件(`.pyc`)采用以下格式：

```
+------------------+
| 文件头(Header)    |
+------------------+
| 常量池(Constants) |
+------------------+
| 符号表(Symbols)   |
+------------------+
| 指令序列(Code)    |
+------------------+
```

## 文件头格式

```c
struct Header {
    uint32_t magic;         // 魔数: 0x50594D56 ("PYMV")
    uint16_t version;       // 版本号
    uint16_t flags;         // 标志位
    uint32_t const_count;   // 常量数量
    uint32_t symbol_count;  // 符号数量
    uint32_t code_size;     // 代码段大小
};
```

### 魔数
- 固定值：`0x50594D56` (ASCII: "PYMV")
- 用于识别PyVM字节码文件

### 版本号
- 当前版本：`0x0001`
- 用于兼容性检查

### 标志位
- Bit 0: 调试信息 (1=包含, 0=不包含)
- Bit 1-15: 保留

## 常量池格式

常量池存储编译时确定的字面量值。

```c
struct ConstantPool {
    Constant constants[const_count];
};

struct Constant {
    uint8_t type;           // 类型标识
    uint32_t size;          // 数据大小
    uint8_t data[size];     // 数据内容
};
```

### 常量类型

| 类型码 | 类型名 | 描述 |
|--------|--------|------|
| 0x01 | INT | 32位整数 |
| 0x02 | FLOAT | 64位浮点数 |
| 0x03 | STRING | UTF-8字符串 |
| 0x04 | BOOL | 布尔值 |

### 常量编码示例

#### 整数常量
```
类型: 0x01 (INT)
大小: 0x04
数据: 0x0000000A (整数10)
```

#### 字符串常量
```
类型: 0x03 (STRING)
大小: 0x0C
数据: "Hello World\0" (12字节)
```

## 符号表格式

符号表存储变量和函数名称信息。

```c
struct SymbolTable {
    Symbol symbols[symbol_count];
};

struct Symbol {
    uint8_t type;           // 符号类型
    uint16_t name_len;      // 名称长度
    char name[name_len];    // 符号名称
    uint32_t value;         // 符号值(索引或地址)
};
```

### 符号类型

| 类型码 | 类型名 | 描述 |
|--------|--------|------|
| 0x01 | VAR | 变量 |
| 0x02 | FUNC | 函数 |

## 指令序列格式

指令序列是顺序执行的字节码指令。

```c
struct CodeSection {
    uint8_t instructions[code_size];
};
```

每条指令的格式：
```
[操作码(1字节)] [操作数(0-4字节)]
```

### 操作数编码

根据指令类型，操作数可能是：
- **无操作数**: 如 ADD, SUB
- **1字节操作数**: 小索引值
- **2字节操作数**: 中等索引值  
- **4字节操作数**: 大索引值或地址偏移

## 完整示例

以下是一个简单程序的字节码格式：

```python
# 源代码
x = 10
y = 20
print(x + y)
```

### 编译后的字节码 (十六进制)

```
文件头:
50 59 4D 56  # 魔数 "PYMV"
01 00        # 版本 1.0
00 00        # 标志位
03 00 00 00  # 常量数量: 3
02 00 00 00  # 符号数量: 2
0E 00 00 00  # 代码大小: 14字节

常量池:
# 常量0: 整数10
01 04 00 00 00  0A 00 00 00
# 常量1: 整数20
01 04 00 00 00  14 00 00 00
# 常量2: 字符串"print"
03 06 00 00 00  70 72 69 6E 74 00

符号表:
# 符号0: 变量x
01 01 00 78 00 00 00 00
# 符号1: 变量y  
01 01 00 79 01 00 00 00

指令序列:
01 00        # LOAD_CONST 0 (加载10)
03 00        # STORE_VAR 0 (存储到x)
01 01        # LOAD_CONST 1 (加载20)
03 01        # STORE_VAR 1 (存储到y)
02 00        # LOAD_VAR 0 (加载x)
02 01        # LOAD_VAR 1 (加载y)
10           # ADD (相加)
40           # PRINT (打印结果)
FF           # HALT (结束程序)
```

## 调试信息格式

当标志位包含调试信息时，在代码段后附加调试数据：

```c
struct DebugInfo {
    uint32_t line_count;        // 行号信息数量
    LineInfo lines[line_count]; // 行号映射表
};

struct LineInfo {
    uint32_t pc;                // 程序计数器
    uint32_t line;              // 源代码行号
    uint16_t column;            // 源代码列号
};
```

## 字节序

PyVM字节码使用小端字节序(Little Endian)存储多字节数据。

## 版本兼容性

- 主版本号不同的字节码不兼容
- 次版本号向后兼容
- 虚拟机启动时检查版本兼容性

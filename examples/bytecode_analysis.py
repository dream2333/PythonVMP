# 字节码分析示例
# 用于展示PyVM如何生成和优化字节码

print("=== 字节码分析示例 ===")

# 简单表达式
print("简单表达式:")
x = 5 + 3
print(x)

# 复杂表达式
print("复杂表达式:")
y = (x + 2) * 3
print(y)

# 多重赋值
print("多重赋值:")
a = 10
b = a
c = b
print(c)

# 条件分支
print("条件分支:")
if x > y:
    print("x更大")
else:
    print("y更大")

# 循环操作
print("循环操作:")
i = 0
while i < 3:
    print("迭代:", i)
    i = i + 1

print("=== 分析完成 ===")
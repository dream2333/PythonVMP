# PyVM综合功能测试
print("=== PyVM综合功能测试 ===")

# 1. 基本算术运算
print("1. 算术运算测试")
a = 10
b = 3
print(a + b)  # 13
print(a - b)  # 7
print(a * b)  # 30

# 2. 变量操作
print("2. 变量操作测试") 
x = 42
y = x
print(y)  # 42

# 3. 条件分支
print("3. 条件分支测试")
if a > b:
    print("a大于b")
else:
    print("a不大于b")

# 4. 比较运算
print("4. 比较运算测试")
if a == 10:
    print("a等于10")
if b != 5:
    print("b不等于5")

# 5. 循环控制
print("5. 循环控制测试")
i = 0
while i < 3:
    print(i)
    i = i + 1

# 6. 字符串处理
print("6. 字符串处理测试")
msg = "Hello PyVM"
print(msg)

# 7. 复杂表达式
print("7. 复杂表达式测试")
result = (a + b) * 2
print(result)  # 26

print("=== 测试完成 ===")

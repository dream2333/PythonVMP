# PyVM交互式演示程序
# 展示虚拟机的各种功能

# 演示1：基本变量操作
print("=== PyVM交互式演示 ===")
print("演示1：基本变量操作")

x = 10
y = 20
result = x + y
print(x)
print(y)
print(result)

# 演示2：条件分支
print("演示2：条件分支")
if result > 25:
    print("结果大于25")
else:
    print("结果不大于25")

# 演示3：循环计算
print("演示3：循环计算")
i = 1
sum_value = 0
while i <= 5:
    sum_value = sum_value + i
    print(sum_value)
    i = i + 1

# 演示4：复杂表达式
print("演示4：复杂表达式")
a = 3
b = 4
c = 5
# 计算周长
perimeter = a + b + c
print(perimeter)

# 演示5：嵌套结构
print("演示5：嵌套结构")
outer = 0
while outer < 3:
    inner = 0
    while inner < 2:
        value = outer * 10 + inner
        print(value)
        inner = inner + 1
    outer = outer + 1

print("=== 演示完成 ===")

# PyVM性能基准测试

print("=== PyVM性能基准测试 ===")

# 测试1：算术运算性能
print("测试1：算术运算性能")
i = 0
result = 0
while i < 1000:
    result = result + i * 2
    i = i + 1
print("算术运算完成")
print(result)

# 测试2：循环性能
print("测试2：循环性能")
count = 0
while count < 500:
    count = count + 1
print("循环测试完成")
print(count)

# 测试3：条件分支性能
print("测试3：条件分支性能")
j = 0
positive = 0
negative = 0
while j < 100:
    if j > 50:
        positive = positive + 1
    else:
        negative = negative + 1
    j = j + 1
print("分支测试完成")
print(positive)
print(negative)

# 测试4：变量操作性能
print("测试4：变量操作性能")
a = 1
b = 2
c = 3
k = 0
while k < 200:
    temp = a
    a = b
    b = c
    c = temp
    k = k + 1
print("变量操作完成")

print("=== 基准测试完成 ===")
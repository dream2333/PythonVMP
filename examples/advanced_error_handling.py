# 高级错误处理和边界测试

print("=== 高级错误处理测试 ===")

# 测试1：除零错误处理
print("测试1：数学运算边界")
a = 10
b = 2
result = a / b
print(result)

# 测试2：大数运算
print("测试2：大数运算")
large1 = 999999
large2 = 999999
large_result = large1 * large2
print(large_result)

# 测试3：深度嵌套运算
print("测试3：复杂表达式")
x = 5
y = 3
z = 2
complex_result = ((x + y) * z - 1) / (z + 1)
print(complex_result)

# 测试4：布尔逻辑组合
print("测试4：复杂条件")
flag1 = true
flag2 = false
if flag1:
    if flag2:
        print("两个都为真")
    else:
        print("只有第一个为真")
else:
    print("第一个为假")

# 测试5：循环边界测试
print("测试5：循环边界")
counter = 0
limit = 5
while counter < limit:
    print(counter)
    counter = counter + 1

print("=== 错误处理测试完成 ===")

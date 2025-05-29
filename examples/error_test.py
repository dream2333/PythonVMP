# 错误处理和边界测试

print("=== 错误处理测试 ===")

# 正常情况
print("正常情况测试:")
x = 10
y = 5
result = x + y
print("正常运算结果:", result)

# 边界值测试
print("边界值测试:")
zero = 0
one = 1
big_num = 9999
print("零值:", zero)
print("单位值:", one)
print("大数值:", big_num)

# 条件边界
print("条件边界测试:")
if zero == 0:
    print("零值比较正确")
if one > zero:
    print("大小比较正确")

# 循环边界
print("循环边界测试:")
counter = 0
while counter < 1:
    print("单次循环")
    counter = counter + 1

# 嵌套结构
print("嵌套结构测试:")
outer = 0
while outer < 2:
    print("外层:", outer)
    inner = 0
    while inner < 2:
        print("内层:", inner)
        inner = inner + 1
    outer = outer + 1

print("=== 测试完成 ===")
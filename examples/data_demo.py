# 数据类型和操作演示

print("=== 数据类型演示 ===")

# 整数操作
print("整数操作:")
num1 = 42
num2 = 17
print("加法:", num1 + num2)
print("减法:", num1 - num2)
print("乘法:", num1 * num2)

# 字符串操作
print("字符串操作:")
msg1 = "Hello"
msg2 = "PyVM"
print(msg1)
print(msg2)

# 布尔逻辑（通过比较实现）
print("布尔逻辑:")
if num1 > num2:
    print("num1大于num2")
if num1 == 42:
    print("num1等于42")
if num2 != 20:
    print("num2不等于20")

# 复杂数据操作
print("复杂数据操作:")
data = 100
while data > 0:
    if data > 50:
        data = data - 10
    else:
        data = data - 5
    print("当前值:", data)
    if data < 20:
        break

print("=== 演示完成 ===")
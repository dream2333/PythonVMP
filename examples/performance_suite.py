# PyVM综合性能测试套件（简化版）

print("=== PyVM综合性能测试 ===")

# 测试1：斐波那契数列
print("测试1：斐波那契数列")
n = 10
a = 0
b = 1
count = 0
while count < n:
    if count == 0:
        result = a
    if count == 1:
        result = b
    if count > 1:
        temp = a + b
        a = b
        b = temp
        result = temp
    count = count + 1
print("斐波那契第10项:")
print(result)

# 测试2：质数检测
print("测试2：质数检测")
num = 17
is_prime = 1
if num <= 1:
    is_prime = 0
i = 2
while i * i <= num:
    if num % i == 0:
        is_prime = 0
    i = i + 1

if is_prime:
    print("17是质数")

# 测试3：嵌套循环性能
print("测试3：嵌套循环")
sum = 0
i = 1
while i <= 5:
    j = 1
    while j <= 5:
        sum = sum + i * j
        j = j + 1
    i = i + 1
print("嵌套循环结果:")
print(sum)

# 测试4：阶乘计算
print("测试4：阶乘计算")
n = 6
factorial = 1
i = 1
while i <= n:
    factorial = factorial * i
    i = i + 1
print("6的阶乘:")
print(factorial)

print("=== 综合性能测试完成 ===")

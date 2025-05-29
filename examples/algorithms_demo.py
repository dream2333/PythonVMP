# 高级数据结构和算法演示

print("=== 高级数据结构演示 ===")

# 测试1：冒泡排序算法
print("测试1：冒泡排序算法")
# 模拟数组: [64, 34, 25, 12, 22, 11, 90]
# 简化版本，只排序5个数字
a = 64
b = 34
c = 25
d = 12
e = 22

print("原始数据:")
print(a)
print(b)
print(c)
print(d)
print(e)

# 冒泡排序的简化实现（5个元素）
# 第一轮
if a > b:
    temp = a
    a = b
    b = temp

if b > c:
    temp = b
    b = c
    c = temp

if c > d:
    temp = c
    c = d
    d = temp

if d > e:
    temp = d
    d = e
    e = temp

# 第二轮
if a > b:
    temp = a
    a = b
    b = temp

if b > c:
    temp = b
    b = c
    c = temp

if c > d:
    temp = c
    c = d
    d = temp

# 第三轮
if a > b:
    temp = a
    a = b
    b = temp

if b > c:
    temp = b
    b = c
    c = temp

# 第四轮
if a > b:
    temp = a
    a = b
    b = temp

print("排序后:")
print(a)
print(b)
print(c)
print(d)
print(e)

# 测试2：阶乘计算
print("测试2：阶乘计算")
n = 5
factorial = 1
i = 1
while i <= n:
    factorial = factorial * i
    i = i + 1
print("5的阶乘:")
print(factorial)

# 测试3：最大公约数（欧几里得算法）
print("测试3：最大公约数")
x = 48
y = 18
while y != 0:
    temp = y
    y = x % y
    x = temp
print("48和18的最大公约数:")
print(x)

print("=== 高级算法演示完成 ===")

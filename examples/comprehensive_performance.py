# PyVM综合性能测试套件

print("=== PyVM综合性能测试 ===")

# 测试1：递归斐波那契（迭代版本）
print("测试1：斐波那契数列性能")
start_n = 15
n = start_n
a = 0
b = 1
count = 0
while count < n:
    if count == 0:
        result = a
    else:
        if count == 1:
            result = b
        else:
            temp = a + b
            a = b
            b = temp
            result = temp
    count = count + 1
print("斐波那契第15项:")
print(result)

# 测试2：质数检测
print("测试2：质数检测")
num = 97
is_prime = true
if num <= 1:
    is_prime = false
else:
    i = 2
    while i * i <= num:
        if num % i == 0:
            is_prime = false
            i = num  # 跳出循环
        i = i + 1

if is_prime:
    print("97是质数")
else:
    print("97不是质数")

# 测试3：数组反转模拟
print("测试3：数组反转")
# 模拟5元素数组反转
arr0 = 1
arr1 = 2
arr2 = 3
arr3 = 4
arr4 = 5

print("原数组:")
print(arr0)
print(arr1)
print(arr2)
print(arr3)
print(arr4)

# 反转
temp = arr0
arr0 = arr4
arr4 = temp

temp = arr1
arr1 = arr3
arr3 = temp

print("反转后:")
print(arr0)
print(arr1)
print(arr2)
print(arr3)
print(arr4)

# 测试4：嵌套循环性能
print("测试4：嵌套循环")
sum = 0
i = 1
while i <= 10:
    j = 1
    while j <= 10:
        sum = sum + i * j
        j = j + 1
    i = i + 1
print("嵌套循环结果:")
print(sum)

# 测试5：条件分支密集测试
print("测试5：条件分支测试")
score = 85

if score >= 90:
    print("A级")
else:
    if score >= 80:
        print("B级")
    else:
        print("C级")

print("=== 综合性能测试完成 ===")

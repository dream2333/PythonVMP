# 复杂测试：循环、嵌套条件、函数调用
print("Starting complex test...")

# 测试嵌套条件
x = 15
y = 30

if x > 10:
    print("x is greater than 10")
    if y > 20:
        print("y is also greater than 20")
        result = x + y
        print(result)
    else:
        print("y is not greater than 20")
else:
    print("x is not greater than 10")

# 测试变量计算
a = 5
b = 7
c = a * 2
d = b - 3
final = c + d
print("Final calculation result:")
print(final)

print("Complex test completed!")

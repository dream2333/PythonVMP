# 斐波那契数列程序
print("斐波那契数列前10项")

# 初始化
a = 0
b = 1
count = 0

print(a)
print(b)

# 循环计算
while count < 8:
    c = a + b
    print(c)
    
    # 更新值
    a = b
    b = c
    count = count + 1

print("计算完成")

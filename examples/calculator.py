# 简单计算器程序
print("简单计算器")

# 读取两个数字
print("请输入第一个数字:")
a = input()
print("请输入第二个数字:")
b = input()

# 转换为整数（简化处理）
# 实际应该有错误处理，这里假设输入都是数字

# 执行计算
sum_result = a + b
diff_result = a - b
mul_result = a * b

print("加法结果:")
print(sum_result)
print("减法结果:")
print(diff_result)
print("乘法结果:")
print(mul_result)

# 条件判断
if a > b:
    print("第一个数字更大")
else:
    if a == b:
        print("两个数字相等")
    else:
        print("第二个数字更大")

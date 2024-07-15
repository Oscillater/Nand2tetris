def deci2Bin(symbolstring):
    decimalNum=int(symbolstring)
    padding=16
    binNum=bin(decimalNum)[2:]
    binNum = binNum.zfill(padding)
    return str(binNum)
# 测试代码
input_string = "42"
result = deci2Bin(input_string)
print(result)
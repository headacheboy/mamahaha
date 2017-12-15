'''
file = open("../../../code/output", encoding='utf-8')
loop = 1
fileO = open("../../../code/output_open", "w", encoding='utf-8')
file2 = open("../input", encoding='utf-8').readlines()
outputLS = []
lineNum = 1
for line in file:
    if len(outputLS) == 0:
        outputLS.append(line.replace("\n", "").replace("\r", ""))
    else:
        fileO.write(line)
    if line == "\n":
        print(outputLS[0], loop, file2[loop-1], lineNum)
        if loop != 6878:
            assert outputLS[0] == file2[loop-1].replace("\n", "").replace("\r", "")
        outputLS.clear()
        loop += 1
    lineNum += 1
print(loop)
'''
file = open("../../../code/output_open", encoding='utf-8')
loop = 1
for line in file:
    if line == "\n":
        loop += 1
print(loop)
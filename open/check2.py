import re

file = open("output1", encoding='utf-8')
fileAns = open("open_answers_new4.txt", encoding='utf-8').readlines()
fileOut = open("open_answers_new5.txt", "w", encoding='utf-8')

patternMonthDay = re.compile(r"\d+月\d+日")
patternMonth = re.compile(r"\d+月")
patternDay = re.compile(r"\d+日")

loop = 0
oldLine = None
for line in file:
    if loop % 3 == 0:
        oldLine = line
    if loop % 3 == 1:
        if line.split()[0] != "@@":
            if oldLine.find("几月几日") != -1 or oldLine.find("几月几号") != -1:
                print(re.findall(patternMonthDay, line)[0])
                fileOut.write(re.findall(patternMonthDay, line)[0] + "\n")
            elif oldLine.find("几月") != -1:
                print(re.findall(patternMonth, line)[0])
                fileOut.write(re.findall(patternMonth, line)[0] + "\n")
            elif oldLine.find("几号") != -1:
                print(re.findall(patternDay, line)[0])
                fileOut.write(re.findall(patternDay, line)[0] + "\n")
            else:
                fileOut.write(line)
        else:
            fileOut.write(fileAns[int(loop/3)])
    loop += 1

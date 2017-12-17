import re

fileQ = open("test.txt", encoding='utf-8')
fileG = open("output_time_number", encoding='utf-8')
fileOp = open("open_answers_new2.txt", encoding='utf-8')
fileOut = open("open_answers_new3.txt", "w", encoding='utf-8')

pattern1 = re.compile(r"\d+日")
pattern2 = re.compile(r"\d+月")
pattern3 = re.compile(r"20\d+年")

for lineQ, lineG, lineOp in zip(fileQ, fileG, fileOp):
    if lineG.split()[0] == "testing" or lineG.find("几") != -1 or lineG.split()[0] == "当时" or lineG.split()[0] == "节日"\
            or len(re.findall(pattern1, lineG)) != 0 or len(re.findall(pattern2, lineG)) != 0 or len(re.findall(pattern3, lineG)) != 0\
        or lineG.split()[0] == "多少" or lineG.find(".") != -1 or lineG.split()[0] == "古代" or lineG.split()[0] == "中国" or \
            lineG.split()[0] == "爱问":
        fileOut.write(lineOp)
        continue
    fileOut.write(lineG)
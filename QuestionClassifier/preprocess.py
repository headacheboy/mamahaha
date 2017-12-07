from jpype import *
startJVM(getDefaultJVMPath(), "-Djava.class.path=D:\hanlp\hanlp-1.5.0.jar;D:\hanlp", "-Xms1g",
         "-Xmx1g")
HanLP = JClass("com.hankcs.hanlp.HanLP")
#file = open("question_simplified", encoding='utf-8')
#fileO = open("question", "w", encoding='utf-8')
file = open("input", encoding='utf-8')
fileO = open("testing", "w", encoding='utf-8')

for line in file:
    #ls = line.split('\t', 1)
    #line = ls[1].replace("\n", "")
    line = line.replace("\n", "")
    ls = HanLP.segment(line)
    for ind, ele in enumerate(ls):
        fileO.write(str(ele) + "\t")
    fileO.write("\n")
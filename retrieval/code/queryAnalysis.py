import re
from jpype import *
startJVM(getDefaultJVMPath(), "-Djava.class.path=D:\hanlp\hanlp-1.5.0.jar;D:\hanlp", "-Xms1g",
         "-Xmx1g")
HanLP = JClass("com.hankcs.hanlp.HanLP")

useful = ["n", "v", "a", "d", "b", "t", "m"]

def queryAnalysis():
    file = open("../input", encoding='utf-8')
    for line in file:
        line = line.split()[0]
        ls = list(HanLP.segment(line))
        for ele in ls:
            ele = str(ele)
            pos = ele.rfind("/")
            tag = ele[pos+1:]
            ele = ele[:pos]
            if tag[0] in useful and tag != "vshi":
                print(ele + "." + tag, end=' ')
        print()
    return 0

if __name__ == "__main__":
    queryAnalysis()
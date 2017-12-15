import re
import math
import jieba
from jpype import *

remPattern = re.compile(r"[\d!\"\'！#,?：。，‘’“”（）、？《》]+")
file = open("../zh_stopword.txt", encoding='utf-8')
stop = set()
startJVM(getDefaultJVMPath(), "-Djava.class.path=D:\hanlp\hanlp-1.5.0.jar;D:\hanlp", "-Xms1g",
         "-Xmx1g")
HanLP = JClass("com.hankcs.hanlp.HanLP")
for line in file:
    ls = line.split()
    for word in ls:
        stop.add(word)
dic = dict()
lsTotal = []
s = set()
total = set()
pattern = re.compile(r'<doc id="(.*?)".*?>')
prefix = "../untoken/"
start = 0
sum = 0
currentId = -1
def main(file, fileO):
    global start, currentId, s, lsTotal, dic, inp
    loop = 0
    for line in file:
        loop += 1
        print(loop)
        if line == "\n":
            print(line)
            continue
        ls = re.findall(pattern, line)
        if len(ls) != 0:
            start += 1
            currentId = int(ls[0])
            fileO.write(line)
            assert (start <= 1 or start >= 0)
        elif line == "</doc>\n":
            s.clear()
            start -= 1
            currentId = -1
            fileO.write(line)
            assert start <= 1 or start >= 0
        else:
            try:
                ls = HanLP.segment(line)
                for ind, ele in enumerate(ls):
                    pos = str(ele).rfind('/')
                    ls[ind] = str(ele)[:pos]
                    #print(ls[ind], end=' ')
                #print()
                fileO.write(" ".join(ls) + "\n")
            except UnicodeEncodeError:
                ls = jieba.cut(line)
                fileO.write(" ".join(ls) + "\n")
    return 0

if __name__ == "__main__":
    n = prefix+"zh_wiki_00"
    file = open(n, encoding='utf-8')
    main(file, open("../token/zh_wiki_0_0", "w", encoding='utf-8'))
    file.close()
    print("zh_wiki_00 finished loading")
    n = prefix+"zh_wiki_01"
    file = open(n, encoding='utf-8')
    main(file, open("../token/zh_wiki_0_1", "w", encoding='utf-8'))
    file.close()
    print("zh_wiki_01 finished loading")
    n = prefix+"zh_wiki_02"
    file = open(n, encoding='utf-8')
    main(file, open("../token/zh_wiki_0_2", "w", encoding='utf-8'))
    file.close()
    print("zh_wiki_02 finished loading")
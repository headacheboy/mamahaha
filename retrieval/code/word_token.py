import re
import sqlite3
import math
import json

remPattern = re.compile(r"[\d!\"\'！#,?：。，‘’“”（）、？《》]+")
file = open("../zh_stopword.txt", encoding='utf-8')
dic = dict()
lsTotal = []
s = set()
total = set()
inp = set()
pattern = re.compile(r'<doc id="(.*?)".*?>')
prefix = "../token/"
start = 0
sum = 0
currentId = -1
def main(file):
    global start, currentId, s, lsTotal, dic, inp
    loop = 0
    for line in file:
        loop += 1
        ls = re.findall(pattern, line)
        if len(ls) != 0:
            start += 1
            currentId = int(ls[0])
            assert (start <= 1 or start >= 0)
        elif line == "</doc>\n":
            inp.clear()
            start -= 1
            currentId = -1
            assert start <= 1 or start >= 0
        else:
            line = re.sub(remPattern, "", line)
            ls = line.split()
            for word in ls:
                if word in s:
                    if word not in dic:
                        dic[word] = [[1, currentId]]
                        inp.add(word)
                    elif word in inp:
                        dic[word][-1][0] += 1
                    else:
                        dic[word].append([1, currentId])
                        inp.add(word)
    return 0

if __name__ == "__main__":
    file = open("../words", encoding='utf-8')
    for line in file:
        total.add(line.split()[0])
    ls = list(total)
    ls.sort()
    file.close()
    for loop in range(10):
        s.clear()
        first = loop*250000
        last = min((loop+1)*250000, len(total))
        for i in range(first, last):
            s.add(ls[i])
        n = prefix+"zh_wiki_00"
        file = open(n, encoding='utf-8')
        main(file)
        file.close()
        print("zh_wiki_00 finished loading")
        n = prefix+"zh_wiki_01"
        file = open(n, encoding='utf-8')
        main(file)
        file.close()
        print("zh_wiki_01 finished loading")
        n = prefix+"zh_wiki_02"
        file = open(n, encoding='utf-8')
        main(file)
        file.close()
        fileO = open("../inverted/"+str(loop), "w", encoding='utf-8')
        json.dump(dic, fileO)
        fileO.close()
        dic.clear()
        print("zh_wiki_02 finished loading")
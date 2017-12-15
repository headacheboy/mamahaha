import re
import math

remPattern = re.compile(r"[\d!\"\'！#,?：。，‘’“”（）、？《》]+")
file = open("../zh_stopword.txt", encoding='utf-8')
stop = set()
for line in file:
    ls = line.split()
    for word in ls:
        stop.add(word)
dic = dict()
lsTotal = []
s = set()
total = set()
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
            s.clear()
            start -= 1
            currentId = -1
            assert start <= 1 or start >= 0
        else:
            line = re.sub(remPattern, " ", line)
            ls = line.split()
            for word in ls:
                if word not in stop:#非停用词
                    if word not in dic:
                        dic[word] = 1
                        s.add(word)
                    elif word not in s:
                        dic[word] += 1
                        s.add(word)
    return 0

if __name__ == "__main__":
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
    fileO = open("../words", "w", encoding='utf-8')
    ls = list(dic.values())
    ls.sort(reverse=True)
    ls = list(dic.keys())
    ls.sort()
    for word in ls:
        fileO.write(word + " " + str(dic[word]) + "\n")
    print("zh_wiki_02 finished loading")
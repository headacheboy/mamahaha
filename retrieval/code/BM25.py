import re
import jieba
import db
import time

remPattern = re.compile(r"[\d!\"\'！#,?：。，‘’“”（）、？《》]+")
class BM25():
    def __init__(self):
        self.database = db.DB()
        self.point = {}
        self.k1 = 1.5
        self.b = 0.75
        self.aveLen = 121.45
        self.outputPath = "../output"
        self.inputPath = "../input"
        self.k = 5

    def query(self, sentenceLS, fileO):
        dic = {}
        for word in sentenceLS:
            flag = False
            idf = self.database.search(2, word)
            for line in idf:
                flag = True
                idf = float(line[0])
            if not flag:
                continue
            tfid = self.database.search(1, word)
            test = list(tfid)
            for line in test:
                tf = int(line[0])
                id = int(line[1])
                leng = self.database.search(3, id)
                for t in leng:
                    length = t[0]
                    break
                if id not in dic:
                    dic[id] = idf * (tf * (self.k1+1) / (tf + self.k1 * (1-self.b + self.b * length / self.aveLen)))
                else:
                    dic[id] += idf * (tf * (self.k1+1) / (tf + self.k1 * (1-self.b + self.b * length / self.aveLen)))
        if len(dic) == 0:
            print("搜索失败")
            fileO.write("搜索失败\n\n")
            return
        val = list(dic.values())
        val.sort(reverse=True)
        idSet = set()
        for id in dic:
            loopLen = min(len(val), self.k)
            for i in range(loopLen):
                if dic[id] == val[i]:
                    idSet.add(id)
        if len(idSet) == 0:
            fileO.write("搜索失败\n\n")
            return
        for id in idSet:
            cursor = self.database.c.execute("select text from documents where id='%s'" % str(id))
            for i in cursor:
                fileO.write("".join(i[0].split()) + "\n")
        fileO.write("\n")
        fileO.flush()

    def getInput(self):
        file = open(self.inputPath, encoding='utf-8')
        fileO = open(self.outputPath, "w", encoding='utf-8')
        loop = 0
        start = time.clock()
        for line in file:
            loop += 1
            line = line.split('\t')[0]
            line = re.sub(remPattern, " ", line)
            ls = list(jieba.cut(line))
            self.query(ls, fileO)
            now = time.clock()
            print(now - start)
            start = now

    def test(self):
        file = open(self.inputPath, encoding='utf-8')
        loop = 0
        for line in file:
            loop += 1
            if loop <= 4833:
                continue
            line = re.sub(remPattern, " ", line)
            ls = list(jieba.cut(line))
            if len(ls) <= 3:
                print(ls, loop)

    def testOne(self):
        line = re.sub(remPattern, " ", "道之以政，齐之以刑，民免而无耻；道之以——，齐之以礼，有耻且格。出自：？")
        ls = list(jieba.cut(line))
        self.query(ls, None)

if __name__ == "__main__":
    bm25 = BM25()
    #bm25.testOne()
    bm25.getInput()
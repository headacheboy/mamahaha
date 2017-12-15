import db
import re
import math

punc = ["。", "，", "：", "\.", ",", ]
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
    global start, currentId, s, lsTotal, dic
    loop = 0
    for line in file:
        line = line.replace("\n", "")
        line = line.replace("\r", "")
        loop += 1
        ls = re.findall(pattern, line)
        if len(line) == 0:
            continue
        if len(ls) != 0:
            start += 1
            currentId = int(ls[0])
            assert (start <= 1 or start >= 0)
        elif line == "</doc>":
            s.clear()
            start -= 1
            currentId = -1
            lsTotal.clear()
            assert start <= 1 or start >= 0
        else:
            lsTotal.append(line+" 。")
    return 0

count = 0

if __name__ == "__main__":
    '''
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
    '''
    database = db.DB()
    file = open("tmp", encoding='utf-8')
    count = 0
    for line in file:
        count += 1
        line = line.replace("\n", "")
        line = line.replace("\r", "")
        ls = line.split('\t')
        ls[1] = ls[1].replace("\'", "\'\'")
        database.update(3, ls)
        if count % 100000 == 0:
            print("batch finished")
            count = 0
            database.conn.commit()
    if count != 0:
        database.conn.commit()
    database.c.execute("create index document_index on documents(id)")
    database.conn.commit()
    database.conn.close()
    '''
    for i in range(10):
        print(i)
        with open("../inverted/" + str(i), encoding='utf-8') as file:
            dic = json.load(file)
            for word in dic:
                ls = dic[word]
                for insideLs in ls:
                    count += 1
                    database.update(1, [word, insideLs[0], insideLs[1]])
                    if count == 100000:
                        print("batch finished")
                        database.conn.commit()
                        count = 0
    if count != 0:
        database.conn.commit()
    print("tf insert finished!")
    with open("../words", encoding='utf-8') as file:
        for line in file:
            ls = line.split()
            database.update(2, [ls[0], math.log(documentNum / float(ls[1]), math.e)])
            count += 1
            if count == 100000:
                database.conn.commit()
                count = 0
    if count != 0:
        database.conn.commit()
    database.c.execute("create index tf_index on tf(word)")
    database.c.execute("create index idf_index on idf(word)")
    print("committing...")
    database.conn.commit()
    database.conn.close()
    '''

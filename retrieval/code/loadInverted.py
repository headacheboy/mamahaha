import db
import re

remPattern = re.compile(r"[\d!\"\'！#,?：。，‘’“”（）、？《》]+")
s = set()
aveLen = 0.0
dic = {}

if __name__ == "__main__":
    database = db.DB()
    file = open("../words", encoding='utf-8')
    for line in file:
        s.add(line.split()[0])
    cursor = database.getAll()
    num = 0
    for line in cursor:
        id = int(line[0])
        text = line[1]
        tmpLen = 0
        num += 1
        print(num)
        text = re.sub(remPattern, "", text)
        ls = text.split()
        for word in ls:
            if word in s:
                tmpLen += 1
        dic[id] = tmpLen
        aveLen = aveLen * ((num-1) / num) + tmpLen / num
    #database.conn.commit()
    print(len(dic), aveLen)

    for id in dic:
        database.update(0, [id, dic[id]])
    database.c.execute("create unique index dLen on documentLen(id)")
    database.conn.commit()
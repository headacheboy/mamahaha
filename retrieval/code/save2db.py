import db
import json
import math

documentNum = 968897

count = 0

if __name__ == "__main__":
    database = db.DB()
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

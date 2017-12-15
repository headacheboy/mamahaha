import re
import sqlite3

class DB():
    def __init__(self):
        self.path = "../db/qa.db"
        self.conn = sqlite3.connect(self.path)
        self.c = self.conn.cursor()

    def getAll(self):
        cursor = self.c.execute("select id, text from documents")
        return cursor

    def update(self, ind, ls):
        '''

        :param ind: 0 for article 1 for tf 2 for idf
        :param ls:  ind is 1 ls[0] = word ls[1] = tf ls[2] = id
                     ind is 2 ls[0] = word ls[1] = idf
        :return:
        '''
        if ind == 1:
            self.c.execute("insert into tf (word, tf, id) VALUES ('%s', %d, %d)" % (ls[0], ls[1], ls[2]))
        elif ind == 2:
            self.c.execute("insert into idf (word, idf) VALUES ('%s', %f)" % (ls[0], ls[1]))
        elif ind == 0:
            self.c.execute("insert into documentLen (id, length) values (%d, %d)" % (ls[0], ls[1]))
        elif ind == 3:
            self.c.execute("insert into documents (id, text) values ('%s', '%s')" % (ls[0], ls[1]))

    def search(self, ind, word):
        '''

        :param ind: 1 for tf 2 for idf
        :param word: primary key
        :return: None if nothing.
        '''
        if ind == 0:
            cursor = self.c.execute("select text from documents where id=%d;" % word)
            return cursor
        elif ind == 1:
            cursor = self.c.execute("select tf, id from tf where word='%s';" % word)
            return cursor
        elif ind == 2:
            cursor = self.c.execute("select idf from idf where word='%s';" % word)
            return cursor
        elif ind == 3:
            cursor = self.c.execute("select length from documentLen where id=%d;" % word)
            return cursor
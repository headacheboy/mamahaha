import sqlite3

conn = sqlite3.connect("tt.db")
c = conn.cursor()

ii = None
for i in conn.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='tmp';"):
    print(int(i[0]))
    ii = i
if int(ii[0]) == 0:
    c.execute("create table tmp( \
        id int8, id2 text NOT NULL); \
    ")
    print("success create")
else:
    for i in c.execute("SELECT id FROM tmp WHERE id2 = 50002;"):
        c.execute("UPDATE tmp SET  id = %d where id2=50002" % (2))
        conn.commit()
        print("success update")
        exit(0)
    c.execute("INSERT INTO tmp (id, id2) VALUES (0, '%s');" % ("挑机"))
    conn.commit()
    print("success insert")
import sqlite3 as sq


base = sq.connect('test.db')
cur = base.cursor()


if base:
    print('DB connected')


base.execute(f'CREATE TABLE IF NOT EXISTS info(login PRIMARY KEY, password TEXT)')


try:
    for login_num in range(1, 26):
        cur.execute(f'INSERT INTO info VALUES(?, ?)', (f"login{login_num}", '1111123'))


except Exception as ex:
    print(repr(ex))
    for info in cur.execute('SELECT * FROM info').fetchall():
        print(info)

base.commit()

import sqlite3



db = sqlite3.connect('database.db')
cur = db.cursor()



def execute(sql):

	cur.execute(sql)
	db.commit()

	return cur.fetchall()
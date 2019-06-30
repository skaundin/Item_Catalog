import sqlite3
conn = sqlite3.connect('catalog.db')
c = conn.cursor()
name = "Soccer"
for row in c.execute('SELECT categories.id AS categories_id, categories.name AS categories_name, categories.description AS categories_description FROM categories'):
    print(row)
for x in c.execute('SELECT * from items order by id'):
    print(x)
c.close()

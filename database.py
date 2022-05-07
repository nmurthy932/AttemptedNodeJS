import sqlite3

def get_connection():
  connection = sqlite3.connect("database.db")
  connection.row_factory = dict_factory
  return connection

def dict_factory(cursor, row):
  d = {}
  for index, col in enumerate(cursor.description):
      d[col[0]] = row[index]
  return d

def create_tables():
  with get_connection() as con:
    cursor = con.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS nodejs (id INTEGER PRIMARY KEY, docID TEXT, name TEXT, created TEXT, author TEXT, code TEXT, markdown TEXT)')
    con.commit()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT, firstName TEXT, lastName TEXT, password TEXT, salt TEXT, created TEXT)')
    con.commit()
import subprocess
from flask import Flask, redirect, render_template, url_for, request, jsonify, abort
import re
import logging
import random
import sqlite3
import datetime
import string

logging.basicConfig(level=logging.DEBUG)

##HELPER FUNCTIONS

def getOutput(code):
  file = open('./nodeJS/index.js','w')
  file.write(code);
  file.close()
  error = 'noerror'
  try:
    p = subprocess.check_output(['node', './nodeJS/index.js'], stderr=subprocess.STDOUT)
  except subprocess.CalledProcessError as e:
    p = e.output;
    error = 'error'
  return p, error

def write_compile(input, name, markdown):
  if input == "":
    return render_template('code.html',code=input,output='Please enter some code',errors='error', markdownString=markdown)
  output = getOutput(input)
  codeOutput = output[0].decode()
  return render_template('code.html',output=codeOutput, errors=output[1], code=input, markdownString=markdown, name=name)

def newCodeDocument(user):
  with get_connection() as con:
    cursor = con.cursor()
    docID = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(20))
    while(len(cursor.execute('SELECT * FROM nodejs WHERE docID=?',[docID,]).fetchall()) != 0):
      docID = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(20))
    created = datetime.datetime.now()
    cursor.execute('INSERT INTO nodejs (docID, name, created, author, code, markdown) VALUES (?, ?, ?, ?, ?, ?)', [docID, 'Untitled project', created, user, '', ''])
    con.commit()
    return redirect(url_for('render_code',id=docID))

def getCode(id):
  with get_connection() as con:
    cursor = con.cursor()
    codePage = cursor.execute('SELECT * FROM nodejs WHERE docID=?',[id,]).fetchall()
    if len(codePage) != 0:
      codeInfo = codePage[0]
    else:
      abort(404)
    return codeInfo

##REWRITE THESE!!!!!!
def valid_user(user):
  logging.info("in valid_user")
  try:
      ret = re.search("^[a-zA-z0-9_-]{3,20}$", user).group(0) == user
  except AttributeError:
      ret = False
  return ret


def valid_pass(password):
  logging.info("in valid_pass")
  try:
    ret = re.search('^[\s\S]{3,20}$', password).group(0) == password
  except AttributeError:
    ret = False
  return ret


def valid_email(email):
  logging.info("in valid_email")
  try:
    ret = re.search('^\S+@\S+.\S$', email).group(0) == email
  except AttributeError:
    ret = False
  return ret

##DATABASE STUFF

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
    cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, salt TEXT, created TEXT)')
    con.commit()

##FLASK STUFF BEGINS

app = Flask(
	__name__,
	template_folder='templates',
	static_folder='static'
)

create_tables()

@app.route('/', methods=['POST','GET'])
def redirect_home():
  return redirect(url_for('render_home'))

@app.route('/home', methods=['POST','GET'], strict_slashes=False)
def render_home():
  ##create_tables()
  return render_template('home.html')

@app.route('/login', methods=['POST','GET'])
def login():
  if request.method == 'POST':
    email = request.form['email']
    if not valid_email(email):
      return render_template('login.html')
    password = request.form['password']
    return redirect(url_for('home'))
  else:
    return render_template('login.html')

@app.route('/code',methods=['POST','GET'], strict_slashes=False)
def codeHome():
  if request.method == 'GET':
    with get_connection() as con:
      cursor = con.cursor()
      projects = cursor.execute('SELECT * FROM nodejs ORDER BY created DESC').fetchall()
      return render_template('codeHome.html', projects=projects)
  else:
    return newCodeDocument('Jim')

@app.route('/code/<id>', methods=['POST','GET'],strict_slashes=False)
def render_code(id):
  codePage = getCode(id)
  nodeCode = codePage['code']
  markdownString = codePage['markdown']
  name = codePage['name']
  if request.method == 'GET':
    logging.info("*** Form displayed using GET ***")
    return render_template('code.html',name=name,code=nodeCode,markdownString=markdownString,errors='noerror')
  else:
    return write_compile(str(request.form['code']), name, markdownString)

## AJAX FUNCTIONS

@app.route('/update-code', methods=['POST','GET'])
def udpateCode():
  if request.method == 'POST':
    ##text = request.json('text')
    data = request.get_json()
    if data[0]['Name'] == '':
      data[0]['Name'] = 'Untitled project'
    with get_connection() as con:
      cursor = con.cursor()
      cursor.execute('UPDATE nodejs SET code=? WHERE docID=?', [data[2]['code'], data[1]['docID'],])
      con.commit()
      cursor.execute('UPDATE nodejs SET name=? WHERE docID=?', [data[0]['Name'], data[1]['docID'],])
      con.commit()
    results = {'processed': 'true', 'title': data[0]['Name']}
    return jsonify(results)
  else:
    return None

@app.route('/delete-project', methods=['POST', 'GET'])
def deletDoc():
  if request.method == 'POST':
    data = request.get_json()
    with get_connection() as con:
      cursor = con.cursor()
      cursor.execute('DELETE FROM nodejs WHERE docID=?', [data[0]['docID'],])
      con.commit()
  results = {'processed': 'true'}
  return jsonify(results)

if __name__ == "__main__":
	app.run(
		host='0.0.0.0',
		port=random.randint(2000, 9000)
    )
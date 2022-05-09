import subprocess
from flask import Flask, redirect, render_template, url_for, request, jsonify, abort, make_response
import re
import logging
import random
import datetime
import string
from encrypt import *
from database import *

logging.basicConfig(level=logging.DEBUG)

##HELPER FUNCTIONS

def getOutput(code):
  file = open('./nodeJS/index.js','w')
  file.write(code)
  file.close()
  error = 'noerror'
  try:
    p = subprocess.check_output(['node', './nodeJS/index.js'], stderr=subprocess.STDOUT)
  except subprocess.CalledProcessError as e:
    p = e.output
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
    cursor.execute('INSERT INTO nodejs (docID, name, created, email, code, markdown) VALUES (?, ?, ?, ?, ?, ?)', [docID, 'Untitled project', created, getCookieName(), '', ''])
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

def valid_email(email):
  logging.info("in valid_email")
  try:
    ret = re.search('^\S+@\S+.\S$', email).group(0) == email
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
  
def create_password(email, firstName, lastName, password):
  if not valid_email(email):
    return render_template('register.html',error="Invalid email",email=email, firstName=firstName, lastName=lastName)
  if firstName == "":
    return render_template('register.html',error="You must enter a first name",email=email, firstName=firstName, lastName=lastName)
  if lastName == "":
    return render_template('register.html',error="You must enter a last name",email=email, firstName=firstName, lastName=lastName)
  ##TODO: Add encryption here
  salt = "".join(random.choices(string.ascii_letters+string.digits, k=10))
  if password == "":
    return render_template('register.html',error="You must enter a password",email=email, firstName=firstName, lastName=lastName)
  password = hash_str(password+salt)
  created = datetime.datetime.now()
  with get_connection() as con:
    cursor = con.cursor()
    if len(cursor.execute('SELECT * FROM users WHERE email=?',[email,]).fetchall()) != 0:
      return render_template('register.html',error="That email is already taken",email=email, firstName=firstName, lastName=lastName)
    cursor.execute('INSERT INTO users (email, firstName, lastName, password, salt, created) VALUES (?, ?, ?, ?, ?, ?)', [email, firstName, lastName, password, salt, created,])
    con.commit()
  return render_template('register.html',success=True)

def checkLogin(email, password):
  with get_connection() as con:
    cursor = con.cursor()
    results = cursor.execute('SELECT * FROM users WHERE email=?',[email,]).fetchall()
    if len(results) == 0:
      return False
    results = results[0]
    if check_secure_val(password, results['password'], results['salt']):
      return True
    else:
      return False

def getCookieName():
  with get_connection() as con:
    cursor = con.cursor()
    email = request.cookies.get('user')
    if email and 'None' not in email:
      email = email.split('|')[0]
      results = cursor.execute('SELECT * FROM users WHERE email=?',[email,]).fetchall()
      if len(results) == 0:
        return None
      else:
        results = results[0]
        name = results['firstName']+' '+results['lastName']
        return name
    else:
      return None


##FLASK STUFF BEGINS

app = Flask(
	__name__,
	template_folder='templates',
	static_folder='static'
)

create_tables()

@app.before_request
def ensure_login():
  routes = ['redirect_home','render_home','login','register','static']
  cookie = request.cookies.get('user')
  user = False
  if cookie and 'None' not in cookie:
    user = check_email(cookie)
  if request.endpoint not in routes and not user:
    resp = make_response(redirect(url_for('login')))
    resp.set_cookie('user','None')
    return resp

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
    password = request.form['password']
    if checkLogin(email, password):
      resp = make_response(redirect(url_for('render_home')))
      resp.set_cookie('user',email+'|'+encryptEmail(email))
      return resp
    else:
      return render_template('login.html', error='Invalid email or password', email=email)
  else:
    return render_template('login.html')

@app.route('/register',methods=['POST','GET'])
def register():
  if request.method == 'POST':
    email = request.form['email']
    password = request.form['password']
    firstName = request.form['firstName']
    lastName = request.form['lastName']
    return create_password(email, firstName, lastName, password)
  else:
    return render_template("register.html")

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
    return redirect(url_for('render_home'))

@app.route('/delete-project', methods=['POST', 'GET'])
def deleteDoc():
  if request.method == 'POST':
    data = request.get_json()
    with get_connection() as con:
      cursor = con.cursor()
      cursor.execute('DELETE FROM nodejs WHERE docID=?', [data[0]['docID'],])
      con.commit()
    results = {'processed': 'true'}
    return jsonify(results)
  else:
    return redirect(url_for('render_home'))

if __name__ == "__main__":
	app.run(
		host='0.0.0.0',
		port=3000
    )
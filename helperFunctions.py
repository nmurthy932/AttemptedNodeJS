import subprocess
from flask import render_template, redirect, url_for, abort, request
import re
import logging
import random
import datetime
from database import *
from encrypt import *


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

def newCodeDocument():
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

def getCookieEmail():
  with get_connection() as con:
    cursor = con.cursor()
    email = request.cookies.get('user')
    if email and 'None' not in email:
      email = email.split('|')[0]
      return email
    else:
      return None

def newLesson():
  with get_connection() as con:
    cursor = con.cursor()
    docID = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(20))
    while(len(cursor.execute('SELECT * FROM nodejs WHERE docID=?',[docID,]).fetchall()) != 0):
      docID = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(20))
    created = datetime.datetime.now()
    cursor.execute('INSERT INTO lessons (docID, email, title, content, created) VALUES (?, ?, ?, ?, ?)', [docID, getCookieEmail(), 'Untitled lesson', '', created,])
    con.commit()
    return redirect(url_for('render_code',id=docID))

def getLesson(id):
  with get_connection() as con:
    cursor = con.cursor()
    lessonPage = cursor.execute('SELECT * FROM lessons WHERE docID=?',[id,]).fetchall()
    if len(lessonPage) != 0:
      lessonInfo = lessonPage[0]
    else:
      abort(404)
    return lessonInfo
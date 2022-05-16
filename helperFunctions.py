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

def write_compile(input, name, markdown, id, html, title, isLesson, permissions, published):
  if input == "":
    return render_template('code.html',code=input,output='Please enter some code',errors='error', markdownString=markdown, name=name, id=id,html=html,title=title,isLesson=isLesson,role=getRole(getCookieEmail()), permissions=permissions, published=published)
  output = getOutput(input)
  codeOutput = output[0].decode()
  return render_template('code.html',output=codeOutput, errors=output[1], code=input, markdownString=markdown, name=name, id=id,html=html,title=title,isLesson=isLesson,role=getRole(getCookieEmail()), permissions=permissions, published=published)

def newCodeDocument(name="Untitled project", code="", markdown="", linkedLesson="",published=0):
  with get_connection() as con:
    if linkedLesson != "" and getLesson(linkedLesson)['published']:
      published = 1
    cursor = con.cursor()
    docID = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(20))
    while(len(cursor.execute('SELECT * FROM nodejs WHERE docID=?',[docID,]).fetchall()) != 0):
      docID = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(20))
    created = datetime.datetime.now()
    cursor.execute('INSERT INTO nodejs (docID, name, created, email, code, markdown, linkedLesson, published) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', [docID, name, created, getCookieEmail(), code, markdown, linkedLesson,published,])
    con.commit()
    return redirect(url_for('render_code',id=docID))

def getCode(id, linked=False):
  with get_connection() as con:
    cursor = con.cursor()
    codePage = cursor.execute('SELECT * FROM nodejs WHERE docID=?',[id,]).fetchall()
    if len(codePage) != 0:
      codeInfo = codePage[0]
    elif linked:
      codeInfo = None
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
  
def create_password(email, firstName, lastName, password, role):
  if not valid_email(email):
    return render_template('register.html',error="Invalid email",email=email, firstName=firstName, lastName=lastName,role=role)
  if firstName == "":
    return render_template('register.html',error="You must enter a first name",email=email, firstName=firstName, lastName=lastName,role=role)
  if lastName == "":
    return render_template('register.html',error="You must enter a last name",email=email, firstName=firstName, lastName=lastName,role=role)
  if role != "student" and role != "teacher":
    return render_template('register.html',error="You must select an existing role",email=email,firstName=firstName,lastName=lastName,role=role)
  ##TODO: Add encryption here
  salt = "".join(random.choices(string.ascii_letters+string.digits, k=10))
  if password == "":
    return render_template('register.html',error="You must enter a password",email=email, firstName=firstName, lastName=lastName,role=role)
  password = hash_str(password+salt)
  created = datetime.datetime.now()
  with get_connection() as con:
    cursor = con.cursor()
    if len(cursor.execute('SELECT * FROM users WHERE email=?',[email,]).fetchall()) != 0:
      return render_template('register.html',error="That email is already taken",email=email, firstName=firstName, lastName=lastName,role=role)
    cursor.execute('INSERT INTO users (email, firstName, lastName, password, salt, created, role) VALUES (?, ?, ?, ?, ?, ?, ?)', [email, firstName, lastName, password, salt, created,role,])
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

def newLesson(id=None, title="Untitled lesson", content="", linked='False', published=0):
  with get_connection() as con:
    if linked != 'False' and getCode(id)['published'] == 1:
      published = 1
    cursor = con.cursor()
    docID = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(20))
    while(len(cursor.execute('SELECT * FROM nodejs WHERE docID=?',[docID,]).fetchall()) != 0):
      docID = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(20))
    created = datetime.datetime.now()
    cursor.execute('INSERT INTO lessons (docID, email, title, content, created, linked, published) VALUES (?, ?, ?, ?, ?, ?, ?)', [docID, getCookieEmail(), title, content, created,linked,published,])
    con.commit()
    if id!=None and linked=='True':
      cursor.execute('UPDATE nodejs SET linkedLesson=? WHERE docID=?',[docID, id,])
      con.commit()
      cursor.execute('UPDATE lessons SET linked=? WHERE docID=?',['True',docID,])
      con.commit()
    return redirect(url_for('render_lesson_edit',id=docID))

def getLesson(id, linked=False):
  with get_connection() as con:
    cursor = con.cursor()
    lessonPage = cursor.execute('SELECT * FROM lessons WHERE docID=?',[id,]).fetchall()
    if len(lessonPage) != 0:
      lessonInfo = lessonPage[0]
    elif not linked:
      abort(404)
    else:
      lessonInfo = None
    return lessonInfo

def getRole(email):
  with get_connection() as con:
    cursor = con.cursor()
    role = cursor.execute('SELECT role FROM users WHERE email=?',[email,]).fetchall()
    if role != []:
      return role[0]['role']
    else:
      return 'student'

def getEmail(docID):
  with get_connection() as con:
    cursor = con.cursor()
    email = cursor.execute('SELECT email FROM nodejs WHERE docID=?',[docID,]).fetchall()
    if email != []:
      return email[0]['email']
    else:
      email = cursor.execute('SELECT email FROM lessons WHERE docID=?',[docID,]).fetchall()
      if email == []:
        return None
      else:
        return email[0]['email']
    
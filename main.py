import subprocess
from flask import Flask, redirect, render_template, url_for, request, jsonify, abort, make_response
import re
import logging
import random
import datetime
import string
from encrypt import *
from database import *
from helperFunctions import *

logging.basicConfig(level=logging.DEBUG)

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
    return newCodeDocument()

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

@app.route('/lesson',methods=['POST','GET'],strict_slashes=False)
def lessonHome():
  getLesson()
  return render_template('lessonHome.html')

@app.route('/lesson/<id>',methods=['POST','GET'],strict_slashes=False)
def render_lesson():
  lessonPage = getLesson(id)
  if request.method == "GET":
    return render_template('lessonEditor.html',email=lessonPage['email'],title=lessonPage['title'],content=lessonPage['content'])

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
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
    if request.cookies.get('user') != None and check_email(request.cookies.get('user')):
      return redirect(url_for('render_home'))
    return render_template('login.html')

@app.route('/logout',methods=['POST','GET'])
def logout():
  resp = make_response(redirect(url_for('render_home')))
  resp.set_cookie('user','None')
  return resp

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

@app.route('/lessons',methods=['POST','GET'],strict_slashes=False)
def lessonHome():
  if request.method == 'GET':
    with get_connection() as con:
      cursor = con.cursor()
      lessons = cursor.execute('SELECT * FROM lessons ORDER BY created DESC').fetchall()
      return render_template('lessonHome.html',lessons=lessons)
  else:
    return newLesson()

@app.route('/lessons/<id>',strict_slashes=False)
def redirect_lesson(id):
  return redirect(url_for('render_lesson',id=id))

@app.route('/lessons/<id>/view',methods=['POST','GET'],strict_slashes=False)
def render_lesson(id):
  lessonPage = getLesson(id)
  if request.method == 'GET':
    return render_template('lesson.html',title=lessonPage['title'],html=lessonPage['content'])

@app.route('/lessons/<id>/edit',methods=['POST','GET'],strict_slashes=False)
def render_lesson_edit(id):
  lessonPage = getLesson(id)
  if request.method == "GET":
    return render_template('lessonEditor.html',title=lessonPage['title'],content=lessonPage['content'])

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
      cursor.execute('UPDATE nodejs SET markdown=? WHERE docID=?', [data[3]['markdown'], data[1]['docID'],])
      con.commit()
    results = {'processed': 'true'}
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

@app.route('/update-lesson',methods=['POST','GET'])
def updateLesson():
  if request.method == 'POST':
    data = request.get_json()
    if data[0]['title'] == '':
      data[0]['title'] = 'Untitled lesson'
    with get_connection() as con:
      cursor = con.cursor()
      cursor.execute('UPDATE lessons SET title=? WHERE docID=?',[data[0]['title'],data[1]['docID'],])
      con.commit()
      cursor.execute('UPDATE lessons SET content=? WHERE docID=?',[data[2]['content'],data[1]['docID'],])
      con.commit()
    results = {'processed':data[2]['content']}
    return jsonify(results)
  else:
    return redirect(url_for('render_home'))

@app.route('/delete-lesson', methods=['POST', 'GET'])
def deleteLesson():
  if request.method == 'POST':
    data = request.get_json()
    with get_connection() as con:
      cursor = con.cursor()
      cursor.execute('DELETE FROM lessons WHERE docID=?', [data[0]['docID'],])
      con.commit()
    results = {'processed': url_for('lessonHome')}
    return jsonify(results)
  else:
    return redirect(url_for('render_home'))

if __name__ == "__main__":
	app.run(
		host='0.0.0.0',
		port=3000
    )
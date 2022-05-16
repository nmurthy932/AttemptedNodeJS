from flask import Flask, redirect, render_template, url_for, request, jsonify, abort, make_response
import logging
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

@app.before_first_request
def beforeFirstRequest():
  create_tables()

@app.before_request
def ensure_login():
  routes = ['redirect_home','render_home','login','register','static']
  teacherRoutes = ['unlinkLesson','linkLesson','deleteLesson','updateLesson','render_lesson_edit']
  cookie = request.cookies.get('user')
  user = False
  if cookie and 'None' not in cookie:
    user = check_email(cookie)
    if not check_role(cookie) and request.endpoint in teacherRoutes:
      resp = make_response(redirect(url_for('render_home')))
      resp.set_cookie('user',getCookieEmail()+'|'+encryptEmail(getCookieEmail())+'|'+'student'+'|'+encryptRole('student'))
      return resp
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
      resp.set_cookie('user',email+'|'+encryptEmail(email)+'|'+getRole(email)+'|'+encryptRole(getRole(email)), max_age=60*60*24*3)
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
  resp.set_cookie('user','None',max_age=0)
  return resp

@app.route('/register',methods=['POST','GET'])
def register():
  if request.method == 'POST':
    role = request.form['role']
    email = request.form['email']
    password = request.form['password']
    firstName = request.form['firstName']
    lastName = request.form['lastName']
    return create_password(email, firstName, lastName, password, role)
  else:
    if request.cookies.get('user') != None and check_email(request.cookies.get('user')):
      return redirect(url_for('render_home'))
    return render_template("register.html")

##Logged in routes

@app.route('/code',methods=['POST','GET'], strict_slashes=False)
def codeHome():
  if request.method == 'GET':
    with get_connection() as con:
      cursor = con.cursor()
      projects = cursor.execute('SELECT * FROM nodejs WHERE email=? OR published=? ORDER BY created DESC',[getCookieEmail(),1,]).fetchall()
      return render_template('codeHome.html', projects=projects, role=getRole(getCookieEmail()), email=getCookieEmail())
  else:
    if request.form['submit'] == 'Create New Linked Code Document' and check_role(request.cookies.get('user')):
      return newCodeDocument(linkedLesson=request.form['id'])
    return newCodeDocument()

##TODO: Fix that weird unlink problem when you unlink in lesson
@app.route('/code/<id>', methods=['POST','GET'],strict_slashes=False)
def render_code(id):
  codePage = getCode(id)
  if codePage['email'] != getCookieEmail() and codePage['published'] == 0:
    return redirect(url_for('render_home'))
  if codePage['email'] == getCookieEmail():
    permissions = "author"
  else:
    permissions = "visitor"
  nodeCode = codePage['code']
  markdownString = codePage['markdown']
  name = codePage['name']
  lesson = getLesson(codePage['linkedLesson'], True)
  if lesson != None:
    html = lesson['content']
    title = lesson['title']
    isLesson = lesson['docID']
  else:
    with get_connection() as con:
      cursor = con.cursor()
      lessons = cursor.execute('SELECT * FROM lessons WHERE linked=? ORDER BY created DESC',['False',]).fetchall()
      html = render_template('lessonSelect.html',lessons=lessons, role=getRole(getCookieEmail()))
      title = 'Choose a lesson to link'
      isLesson = ''
  if request.method == 'GET':
    logging.info("*** Form displayed using GET ***")
    return render_template('code.html',name=name,id=id,code=nodeCode,markdownString=markdownString,errors='noerror',html=html,title=title,isLesson=isLesson,role=getRole(getCookieEmail()), permissions=permissions, published=codePage['published'])
  else:
    return write_compile(str(request.form['code']), name, markdownString, id, html, title, isLesson, permissions, codePage['published'])

@app.route('/lessons',methods=['POST','GET'],strict_slashes=False)
def lessonHome():
  if request.method == 'GET':
    with get_connection() as con:
      cursor = con.cursor()
      lessons = cursor.execute('SELECT * FROM lessons WHERE email=? OR published=? ORDER BY created DESC',[getCookieEmail(), 1,]).fetchall()
      return render_template('lessonHome.html',lessons=lessons,role=getRole(getCookieEmail()))
  elif check_role(request.cookies.get('user')):
    if request.form['submit'] == 'Create New Linked Lesson':
      return newLesson(request.form['id'], linked='True')
    return newLesson()
  else:
    return redirect(url_for('render_home'))

@app.route('/lessons/<id>',strict_slashes=False)
def redirect_lesson(id):
  return redirect(url_for('render_lesson',id=id))

@app.route('/lessons/<id>/view',methods=['POST','GET'],strict_slashes=False)
def render_lesson(id):
  lessonPage = getLesson(id)
  if lessonPage['email'] != getCookieEmail() and lessonPage['published'] == 1:
    permissions = "visitor"
  elif lessonPage['email'] != getCookieEmail() and lessonPage['published'] == 0:
    return redirect(url_for('render_home'))
  else:
    permissions = "author"
  if lessonPage['linked'] == 'True':
    with get_connection() as con:
      cursor = con.cursor()
      codeLink = cursor.execute('SELECT docID FROM nodejs WHERE linkedLesson=?',[id,]).fetchall()
      if codeLink != []:
        codeLink = codeLink[0]['docID']
      else:
        codeLink = None
  else:
    codeLink = None
  if request.method == 'GET' and (lessonPage['published'] == 1 or check_role(request.cookies.get('user'))):
    return render_template('lesson.html',title=lessonPage['title'],html=lessonPage['content'],codeID=codeLink,lessonID=id,role=getRole(getCookieEmail()),permissions=permissions)
  else:
    return redirect(url_for('render_home'))

@app.route('/lessons/<id>/edit',methods=['POST','GET'],strict_slashes=False)
def render_lesson_edit(id):
  lessonPage = getLesson(id)
  if lessonPage['email'] != getCookieEmail():
    return redirect(url_for('render_home'))
  if request.method == "GET":
    with get_connection() as con:
      cursor = con.cursor()
      linkedCode = cursor.execute('SELECT docID FROM nodejs WHERE linkedLesson=? AND email=?', [id,getCookieEmail(),]).fetchall()
      if linkedCode != []:
        linkedCode = linkedCode[0]['docID']
        html = ''
        name = ''
      else:
        linkedCode = None
        projects = cursor.execute('SELECT * FROM nodejs WHERE linkedLesson=? ORDER BY created DESC',['',]).fetchall()
        html = render_template('codeSelect.html',projects=projects, role=getRole(getCookieEmail()))
        name = 'Choose a lesson to link'
      return render_template('lessonEditor.html',title=lessonPage['title'],content=lessonPage['content'],codeID=linkedCode,html=html,name=name,lessonID=id,published=lessonPage['published'])

## AJAX FUNCTIONS

@app.route('/update-code', methods=['POST','GET'])
def udpateCode():
  if request.method == 'POST':
    data = request.get_json()
    if getEmail(data[1]['docID']) != getCookieEmail():
        return redirect(url_for('render_home'))
    if data[0]['Name'] == '':
      data[0]['Name'] = 'Untitled project'
    with get_connection() as con:
      cursor = con.cursor()
      cursor.execute('UPDATE nodejs SET code=? WHERE docID=?', [data[2]['code'], data[1]['docID'],])
      con.commit()
      cursor.execute('UPDATE nodejs SET name=? WHERE docID=?', [data[0]['Name'], data[1]['docID'],])
      con.commit()
      if getRole(getCookieEmail()):
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
    if getEmail(data[0]['docID']) != getCookieEmail():
        return redirect(url_for('render_home'))
    with get_connection() as con:
      cursor = con.cursor()
      email = cursor.execute('SELECT email FROM nodejs WHERE docID=?',[data[0]['docID'],]).fetchall()
      if email != [] and email[0]['email'] == getCookieEmail():
        linkedLesson = cursor.execute('SELECT linkedLesson FROM nodejs WHERE docID=?',[data[0]['docID'],]).fetchall()
        if linkedLesson != []:
          linkedLesson = linkedLesson[0]['linkedLesson']
          cursor.execute('UPDATE lessons SET linked=? WHERE docID=?',['False',linkedLesson,])
        cursor.execute('DELETE FROM nodejs WHERE docID=?', [data[0]['docID'],])
        con.commit()
        results = {'processed': 'true'}
        return jsonify(results)
      return redirect(url_for('render_home'))
  else:
    return redirect(url_for('render_home'))

@app.route('/update-lesson',methods=['POST','GET'])
def updateLesson():
  if request.method == 'POST':
    data = request.get_json()
    if getEmail(data[1]['docID']) != getCookieEmail():
        return redirect(url_for('render_home'))
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
    if getEmail(data[0]['docID']) != getCookieEmail():
        return redirect(url_for('render_home'))
    with get_connection() as con:
      cursor = con.cursor()
      cursor.execute('DELETE FROM lessons WHERE docID=?', [data[0]['docID'],])
      con.commit()
      cursor.execute('UPDATE nodejs SET linkedLesson=? WHERE linkedLesson=?', ['',data[0]['docID'],])
      con.commit()
    results = {'processed': url_for('lessonHome')}
    return jsonify(results)
  else:
    return redirect(url_for('render_home'))

@app.route('/link-lesson', methods=['POST','GET'])
def linkLesson():
  if request.method == 'POST':
    data = request.get_json()
    if getEmail(data[1]['codeID']) != getCookieEmail() or getEmail(data[0]['lessonID']) != getCookieEmail():
        return redirect(url_for('render_home'))
    with get_connection() as con:
      cursor = con.cursor()
      cursor.execute('UPDATE nodejs SET linkedLesson=? WHERE docID=?',[data[0]['lessonID'], data[1]['codeID'],])
      con.commit()
      cursor.execute('UPDATE lessons SET linked=? WHERE docID=?',['True',data[0]['lessonID'],])
      con.commit()
    lesson = getLesson(data[0]['lessonID'], True)
    if lesson != None:
      results = {'title': lesson['title'], 'content': lesson['content']}
    else:
      results = {'title': None, 'content': None}
    return jsonify(results)
  else:
    return redirect(url_for('render_home'))

@app.route('/unlink-lesson', methods=['POST','GET'])
def unlinkLesson():
  if request.method == 'POST':
    data = request.get_json()
    if getEmail(data[1]['lessonID']) != getCookieEmail() or getEmail(data[0]['codeID']) != getCookieEmail():
        return redirect(url_for('render_home'))
    with get_connection() as con:
      cursor = con.cursor()
      cursor.execute('UPDATE lessons SET linked=? WHERE docID=?',['False', data[1]['lessonID'],])
      con.commit()
      cursor.execute('UPDATE nodejs SET linkedLesson=? WHERE docID=?',['', data[0]['codeID'],])
      con.commit()
      lessons = cursor.execute('SELECT * FROM lessons ORDER BY created DESC').fetchall()
      html = render_template('lessonSelect.html',lessons=lessons)
      title = 'Choose a lesson to link'
      isLesson = ''
      results = {'title': title, 'html': html, 'isLesson': isLesson}
      return jsonify(results)
  else:
    return redirect(url_for('render_home'))

@app.route('/set-published',methods=['POST','GET'])
def setPublish():
  if request.method == 'POST':
    data = request.get_json()
    if data[2]['published'] == True:
      data[2]['published'] = 1
    elif data[2]['published'] == False:
      data[2]['published'] = 0
    if data[0]['document'] == 'lesson':
      if getEmail(data[1]['lessonID']) != getCookieEmail():
        return redirect(url_for('render_home'))
      else:
        with get_connection() as con:
          cursor = con.cursor()
          cursor.execute('UPDATE lessons SET published=? WHERE docID=? AND email=?',[data[2]['published'],data[1]['lessonID'],getCookieEmail(),])
          con.commit()
          if getLesson(data[1]['lessonID'])['linked'] == 'True':
            cursor.execute('UPDATE nodejs SET published=? WHERE linkedLesson=? AND email=?',[data[2]['published'],data[1]['lessonID'],getCookieEmail(),])
            con.commit()
    else:
      if getEmail(data[1]['codeID']) != getCookieEmail():
        return redirect(url_for('render_home'))
      else:
        with get_connection() as con:
          cursor = con.cursor()
          cursor.execute('UPDATE nodejs SET published=? WHERE docID=? AND email=?',[data[2]['published'],data[1]['codeID'],getCookieEmail()])
          con.commit()
          if getCode(data[1]['codeID'])['linkedLesson'] != '':
            cursor.execute('UPDATE lessons SET published=? WHERE docID=? AND email=?',[data[2]['published'],getCode(data[1]['codeID'])['linkedLesson'],getCookieEmail(),])
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
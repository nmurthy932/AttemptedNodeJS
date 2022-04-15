import subprocess
from flask import Flask, redirect, render_template, url_for, request
import re
import logging
import random

logging.basicConfig(level=logging.DEBUG)

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

def write_compile(input, markdown):
  if input == "":
    return render_template('home.html',code=input,output='Please enter some code',errors='error', markdownString=markdown)
  output = getOutput(input)
  codeOutput = output[0].decode()
  return render_template('home.html',output=codeOutput, errors=output[1], code=input, markdownString=markdown)

app = Flask(
	__name__,
	template_folder='templates',
	static_folder='static'
)

@app.route('/', methods=['POST','GET'])
def base_page():
  nodeCode = open('./nodeJS/index.js','r').read()
  markdownString = str(open('./nodeJS/Readme.md','r').read())
  if request.method == 'GET':
    logging.info("*** Form displayed using GET ***")
    return render_template('home.html',code=nodeCode,markdownString=markdownString,errors='noerror')
  else:
    return write_compile(str(request.form['code']), markdownString)


if __name__ == "__main__":
	app.run(
		host='0.0.0.0',
		port=random.randint(2000, 9000)
    )
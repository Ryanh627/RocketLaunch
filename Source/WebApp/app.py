from flask import Flask, redirect, url_for, request, render_template
import random
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/success')
def success():
    return 'Login success'

@app.route('/failure')
def failure():
    return 'Login failure'

@app.route('/login',methods = ['POST', 'GET'])
def login():
   if request.method == 'POST':
      rand = bool(random.getrandbits(1))
      if rand:
          return redirect(url_for('success'))
      else:
          return redirect(url_for('failure'))
   else:
      return render_template('login.html')

if __name__ == '__main__':
   app.run(debug = True)

#Developed and owned by Benjamin Eckert, Peter Gifford, and Ryan Hansen of Western Michigan University.

#app.py controls the flow of web traffic and backend functionality.

#This module uses Flask and was developed by referencing Flask documentation. Methods and classes that are used as a part of Flask are not owned by the aforementioned individuals.

#Imports and Initialization----------------------------------------------------

from flask import Flask, redirect, url_for, request, render_template, session
import random
from pad import *
from database import *
from launch import *
from multiprocessing import Process

app = Flask(__name__)
app.secret_key = b'1\xcd/a\x88\x9fV5\x07|q\x91\xfa`\xc1y'

db_init()
pads = pads_setup()

#App routes--------------------------------------------------------------------

@app.route('/')
def index():
    if logged_in():
        return redirect(url_for('mission_control'))
    else:
        return redirect(url_for('login'))

@app.route('/mission_control')
def mission_control():
    if not logged_in():
        return redirect(url_for('login'))
    
    for pad in pads:
        pad.check_connection()

    return render_template('mission_control.html', pads = pads)

def pads_setup():
    pads = []
    stream = open('pad.conf', 'r')
    lines = stream.readlines()
    i = 0

    for line in lines:
        args = line.split(' ')
        pads.append(Pad('Pad ' + str(i), arg[0], arg[1]))

    stream.close()
    return pads

@app.route('/my_account')
def my_account():
    if not logged_in():
        return redirect(url_for('login'))

    return render_template('my_account.html')

@app.route('/login', methods = ['POST', 'GET'])
def login():
    login_message = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if db_login(username, password):
            session['username'] = username
            return redirect(url_for('mission_control'))
        else:
            login_message = "Login failure. Please try again!"
    
    return render_template('login.html', login_message = login_message)

@app.route('/sign_up', methods = ['POST', 'GET'])
def sign_up():
    signup_message = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if db_signup(username, password):
            session['username'] = username
            return redirect(url_for('mission_control'))
        else:
            signup_message = "Sign up failure. Please try again!"

    return render_template('sign_up.html', signup_message = signup_message)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/launch')
def launch():
    p = Process(target = test)
    p.start()
    return "Launched"

#Methods-----------------------------------------------------------------------
def logged_in():
    try:
        return session['username']
    
    except:
        session['username'] = False
        return False

if __name__ == '__main__':
    app.run(debug = True)

#Developed and owned by Benjamin Eckert, Peter Gifford, and Ryan Hansen of Western Michigan University.

#app.py controls the flow of web traffic and backend functionality.

#This module uses Flask and was developed by referencing Flask documentation. Methods and classes that are used as a part of Flask are not owned by the aforementioned individuals.

#Imports and Initialization----------------------------------------------------

from flask import Flask, redirect, url_for, request, render_template, session
import random
from pad import *
from database import *
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

@app.route('/mission_control/<option>', methods = ['POST', 'GET'])
def pad_selection(option):
    if not logged_in():
        return redirect(url_for('login'))

    if request.method != 'POST':
        return redirect(url_for('mission_control'))

    if 'selectedpads' not in session:
        session['selectedpads'] = []

    if option == 'select':
        pad = request.form['select']
        session['selectedpads'].append(pad)
        session.modified = True

    elif option == 'deselect':
        pad = request.form['deselect']
        session['selectedpads'].remove(pad)
        session.modified = True

    return redirect(url_for('mission_control'))

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
    session.clear()
    return redirect(url_for('login'))

@app.route('/launch', methods = ['POST', 'GET'])
def launch():
    if request.method == 'POST':
        for pad in pads:
            if pad.name in session['selectedpads'] and pad.connected:
                pad.launch()

        session.pop('selectedpads', None)

    return redirect(url_for('mission_control'))

#Methods-----------------------------------------------------------------------
def logged_in():
    try:
        return session['username']
    
    except:
        session['username'] = False
        return False

def get_pad(name):
    for pad in pads:
        if pad.name == name:
            return pad
    return None

if __name__ == '__main__':
    app.run(debug = True)

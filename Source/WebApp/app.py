#Developed and owned by Benjamin Eckert, Peter Gifford, and Ryan Hansen of Western Michigan University.

#app.py controls the flow of web traffic and backend functionality.

#This module uses Flask and was developed by referencing Flask documentation. Methods and classes that are used as a part of Flask are not owned by the aforementioned individuals.

#Imports and Initialization----------------------------------------------------

from flask import Flask, redirect, url_for, request, render_template, session
import random, sqlite3
from launch import *
from multiprocessing import Process

app = Flask(__name__)

app.secret_key = b'1\xcd/a\x88\x9fV5\x07|q\x91\xfa`\xc1y'

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

    return render_template('mission_control.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/sign_up')
def sign_up():
    return render_template('standard.html')

@app.route('/launch')
def launch():
    p = Process(target = test)
    p.start()
    return "Launched"

#Methods-----------------------------------------------------------------------
def logged_in():
    try:
        return session['logged_in']
    
    except:
        session['logged_in'] = False
        return False        

if __name__ == '__main__':
    app.run(debug = True)

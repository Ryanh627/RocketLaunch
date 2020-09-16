from flask import Flask, redirect, url_for, request, render_template
import random
from launch import *
from multiprocessing import Process

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/launch')
def launch():
    p = Process(target = test)
    p.start()
    return "Launched"

if __name__ == '__main__':
   app.run(debug = True)
#Developed and owned by Benjamin Eckert, Peter Gifford, and Ryan Hansen of Western Michigan University.

#app.py controls the flow of web traffic and backend functionality.

#This module uses Flask and was developed by referencing Flask documentation. Methods and classes that are used as a part of Flask are not owned by the aforementioned individuals.

#Imports and Initialization----------------------------------------------------

from flask import Flask, redirect, url_for, request, render_template, session
import random, os
from pad import *
from database import *
from multiprocessing import Process
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = b'1\xcd/a\x88\x9fV5\x07|q\x91\xfa`\xc1y'

UPLOAD_FOLDER = os.path.join('static', 'media/profile_pictures')
ALLOWED_PICTURE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

pads = pads_setup()
db_init(len(pads))
authorization_timeout = Process(target=db_authorization_timeout)

#App routes--------------------------------------------------------------------

@app.route('/')
def index():
    if logged_in() and is_admin():
        return redirect(url_for('mission_control'))
    
    elif logged_in() and not is_admin():
        return redirect(url_for('my_account'))
    
    else:
        return redirect(url_for('login'))

@app.route('/mission_control')
def mission_control():
    if not logged_in():
        return redirect(url_for('login'))

    if not is_admin():
        return redirect(url_for('my_account'))

    for pad in pads:
        pad.check_connection()

    return render_template('mission_control.html', pads = pads)

@app.route('/mission_control/<option>', methods = ['POST', 'GET'])
def pad_selection(option):
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

@app.route('/my_account', methods = ['POST', 'GET'])
def my_account():
    if not logged_in():
        return redirect(url_for('login'))
    
    picture = db_get_picture(session['username'])
    filename = os.path.join(app.config['UPLOAD_FOLDER'], picture)

    return render_template('my_account.html', picture=filename)

@app.route('/my_account/<option>', methods = ['POST', 'GET'])
def changeUserInfo(option):
    if request.method != 'POST':
        return redirect(url_for('my_account'))

    if option == "change_username":
        if db_change_username(session['username'], request.form['current'], request.form['new']):
            session['username'] = request.form['new']
            session['success'] = "Username changed!"
        else:
            session['error'] = "Failed to change username!"

    elif option == "change_password":
        if db_change_password(session['username'], request.form['current'], request.form['new']):
            session['success'] = "Password changed!"
        else:
            session['error'] = "Failed to change password!"

    return redirect(url_for('my_account'))

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        success, admin = db_login(username, password)
            
        if success:
            session['username'] = username
            session['success'] = "Logged in successfully! Welcome, " + username + "!"
            session['admin'] = admin
            
            if session['admin']:
                return redirect(url_for('mission_control'))

            else:
                return redirect(url_for('my_account'))
        
        else:
            session['error'] = "Login failure. Please try again!"
    
    return render_template('login.html')

@app.route('/sign_up', methods = ['POST', 'GET'])
def sign_up():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        success, admin = db_signup(username, password)

        if success:
            session['username'] = username
            session['success'] = "Signed up successfully! Welcome, " + username + "!"
            session['admin'] = admin

            if session['admin']:
                return redirect(url_for('mission_control'))

            else:
                return redirect(url_for('my_account'))

        else:
            session['error'] = "Sign up failure. Please try again!"

    return render_template('sign_up.html')

@app.route('/authorize', methods = ['POST'])
def authorize():
    if request.method != 'POST':
        if not logged_in():
            return redirect(url_for('login'))
        if is_admin():
            return redirect(url_for('mission_control'))
        
        return redirect(url_for('my_account'))
    
    global authorization_timeout

    if authorization_timeout.is_alive():
        authorization_timeout.terminate()
    
    authorization_timeout = Process(target=db_authorization_timeout)   
    authorization_timeout.start()

    error = False
    authorized_users_duplicates = []
    authorized_users = []
    data = request.form

    for key in data:
        user = data[key]
        authorized_users_duplicates.append(user)
    
    for i in authorized_users_duplicates:
        if i not in authorized_users:
            authorized_users.append(i)
        else:
            authorized_users.append("None")

    if db_erase_authorized_users() == False:
        error = True

    db_authorized_users_init(len(pads))

    for user in authorized_users:
        if db_insert_authorized_user(user) == False:
            error = True
    
    if error:
        session['error'] = "Failed to authorize users!"

    else:
        session['success'] = "Successfully authorized users!"

    return redirect(url_for('launch_config'))

@app.route('/settings', methods = ['GET', 'POST'])
def settings():
    if request.method != 'POST':
        if not logged_in():
            return redirect(url_for('login'))
        if is_admin():
            return redirect(url_for('mission_control'))
        
        return redirect(url_for('my_account'))

    error = False
    data = request.form
    try:
        request.form['record_launch']
        record_launch = True
    
    except:
        record_launch = False

    recording_duration = request.form['recording_duration']

    if db_update_setting('RECORDLAUNCH', record_launch) == False:
        error = True

    if db_update_setting('RECORDINGDURATION', recording_duration) == False:
        error = True

    if error:
        session['error'] = "Failed to save settings!"

    else:
        session['success'] = "Settings saved!"

    return redirect(url_for('launch_config'))

@app.route('/logout')
def logout():
    session.clear()
    session['error'] = "Logged out!"
    return redirect(url_for('login'))

@app.route('/delete', methods = ['POST', 'GET'])
def delete():
    if request.method == 'POST':
        db_delete(session['username'])
        session.clear()
        session['error'] = "Deleted account!"

    return redirect(url_for('login'))

@app.route('/picture_upload', methods = ['POST', 'GET'])
def picture_upload():
    if request.method != 'POST':
        if not logged_in():
            return redirect(url_for('login'))
        if is_admin():
            return redirect(url_for('mission_control'))

    picture = request.files['file']
    
    if picture.filename == '':
        session['error'] = "No file selected! Please select a file!"
        return redirect(url_for('my_account'))
    
    if verify_picture(picture.filename):
        filename = secure_filename(picture.filename)
        picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        db_change_picture(session['username'], filename)
        session['success'] = "Profile picture changed!"
        return redirect(url_for('my_account'))

    else:
        session['error'] = "Invalid image! Please select a different image!"
        return redirect(url_for('my_account'))

@app.route('/launch', methods = ['POST', 'GET'])
def launch():
    if request.method == 'POST':
        for pad in pads:
            if pad.name in session['selectedpads'] and pad.connected:
                pad.launch()

        session.pop('selectedpads', None)

    return redirect(url_for('mission_control'))

@app.route('/verify/<frompage>/<topage>/<prompt>', methods = ['POST', 'GET'])
def verify(frompage, topage, prompt):
    if request.method != 'POST':
        if not logged_in():
            return redirect(url_for('login'))
        if is_admin():
            return redirect(url_for('mission_control'))

    return render_template('verify.html', frompage=frompage, topage=topage, prompt=prompt)

@app.route('/launch_config')
def launch_config():
    if not logged_in():
        return redirect(url_for('login'))
    if not is_admin():
        return redirect(url_for('my_account'))

    users = db_get_usernames()
    authorized_users = db_get_authorized_users()
    record_launch = db_get_setting('RECORDLAUNCH')
    recording_duration = db_get_setting('RECORDINGDURATION')

    return render_template('launch_config.html', pads = pads, users = users, authorized_users = authorized_users, record_launch = record_launch, recording_duration = recording_duration)

#Methods-----------------------------------------------------------------------
def logged_in():
    try:
        val = session['username']
        return True

    except:
        return False

def is_admin():
    if 'username' not in session:
        return False

    if 'admin' not in session:
        return False

    return session['admin']

def get_pad(name):
    for pad in pads:
        if pad.name == name:
            return pad
    return None

def verify_picture(filename):
    for extension in ALLOWED_PICTURE_EXTENSIONS:
        if filename.lower().endswith(extension):
            return True
    
    return False

if __name__ == '__main__':
    app.run(debug = True)

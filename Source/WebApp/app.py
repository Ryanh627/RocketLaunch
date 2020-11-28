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

app = Flask(__name__, static_url_path = '/static')
app.secret_key = b'1\xcd/a\x88\x9fV5\x07|q\x91\xfa`\xc1y'

UPLOAD_FOLDER = '/home/pi/RocketLaunch/Source/WebApp/static/media/profile_pictures'
ALLOWED_PICTURE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

pads = pads_setup()
db_init(len(pads))
authorization_timeout = Process(target=db_authorization_timeout)

def placeholder():
    return

launch_process = Process(target=placeholder)

#App routes--------------------------------------------------------------------

@app.route('/')
def index():

    #Redirects
    if logged_in() and is_admin():
        return redirect(url_for('mission_control'))
    
    elif logged_in() and not is_admin():
        return redirect(url_for('my_account'))
    
    else:
        return redirect(url_for('login'))

@app.before_request
def session_init():

    #Have session data clear when browser is closed
    session.permanent = False

@app.route('/mission_control')
def mission_control():

    #Redirects
    if not logged_in():
        return redirect(url_for('login'))

    if not is_admin():
        return redirect(url_for('my_account'))

    #Update pad connection data
    for pad in pads:
        pad.check_connection()

    #Render the mission control page
    return render_template('mission_control.html', pads = pads)

@app.route('/mission_control/<option>', methods = ['POST', 'GET'])
def pad_selection(option):

    #Redirect on GET
    if request.method != 'POST':
        return redirect(url_for('mission_control'))
    
    #Select or de-select on POST 
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

    #Redirects
    if not logged_in():
        return redirect(url_for('login'))
    
    #Get profile picture from database
    picture = db_get_picture(session['username'])
    filename = url_for('static', filename = 'media/profile_pictures/' + picture)

    #Render My Account page
    return render_template('my_account.html', picture=filename)

@app.route('/my_account/<option>', methods = ['POST', 'GET'])
def changeUserInfo(option):
    
    #Redirect on GET
    if request.method != 'POST':
        return redirect(url_for('my_account'))

    #Update username in database
    if option == "change_username":
        #If no errors
        if db_change_username(session['username'], request.form['current'], request.form['new']):
            session['username'] = request.form['new']
            session['success'] = "Username changed!"
        #Otherwise, denote errors
        else:
            session['error'] = "Failed to change username!"
    
    #Update password in database
    elif option == "change_password":
        #If no errors
        if db_change_password(session['username'], request.form['current'], request.form['new']):
            session['success'] = "Password changed!"

        #Otherwise, denote error
        else:
            session['error'] = "Failed to change password!"

    return redirect(url_for('my_account'))

@app.route('/login', methods = ['POST', 'GET'])
def login():
    #On POST method
    if request.method == 'POST':

        #Get data from forms
        username = request.form['username']
        password = request.form['password']
        success, admin = db_login(username, password)
            
        #If no errors and password matches
        if success:

            #Update session data
            session['username'] = username
            session['success'] = "Logged in successfully! Welcome, " + username + "!"
            session['admin'] = admin
            
            #Redirects
            if session['admin']:
                return redirect(url_for('mission_control'))

            else:
                return redirect(url_for('my_account'))
        
        else:
            session['error'] = "Login failure. Please try again!"
    
    return render_template('login.html')

@app.route('/sign_up', methods = ['POST', 'GET'])
def sign_up():

    #On POST
    if request.method == 'POST':

        #Get data from forms
        username = request.form['username']
        password = request.form['password']
        success, admin = db_signup(username, password)

        #If no errors
        if success:

            #Set session data
            session['username'] = username
            session['success'] = "Signed up successfully! Welcome, " + username + "!"
            session['admin'] = admin


            #Redirects
            if session['admin']:
                return redirect(url_for('mission_control'))

            else:
                return redirect(url_for('my_account'))

        else:
            session['error'] = "Sign up failure. Please try again!"

    return render_template('sign_up.html')

@app.route('/authorize', methods = ['POST'])
def authorize():

    #Redirects
    if request.method != 'POST':
        if not logged_in():
            return redirect(url_for('login'))
        if is_admin():
            return redirect(url_for('mission_control'))
        
        return redirect(url_for('my_account'))
    
    #If the authorization timeout process is still going, stop it
    global authorization_timeout

    if authorization_timeout.is_alive():
        authorization_timeout.terminate()
    
    #Start a new authorization timeout process
    authorization_timeout = Process(target=db_authorization_timeout)   
    authorization_timeout.start()

    error = False
    authorized_users_duplicates = []
    authorized_users = []
    data = request.form

    #Remove duplicate authorized users, replace with "None"

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

    #Make sure an authorized_users table is set up 
    #that is the same length as the number of launch pads
    db_authorized_users_init(len(pads))

    #Insert authorized users into database
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
    
    #Redirects
    if request.method != 'POST':
        if not logged_in():
            return redirect(url_for('login'))
        if is_admin():
            return redirect(url_for('mission_control'))
        
        return redirect(url_for('my_account'))

    error = False
    data = request.form

    #Get form data
    try:
        request.form['record_launch']
        record_launch = True
    
    except:
        record_launch = False

    recording_duration = request.form['recording_duration']

    #Update settings in database, denote errors
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
    #Clear session data
    session.clear()
    session['error'] = "Logged out!"
    return redirect(url_for('login'))

@app.route('/delete', methods = ['POST', 'GET'])
def delete():
    if request.method == 'POST':
        
        #Delete user in database and clear session data
        db_delete(session['username'])
        session.clear()
        session['error'] = "Deleted account!"

    return redirect(url_for('login'))

@app.route('/picture_upload', methods = ['POST', 'GET'])
def picture_upload():

    #Redirects
    if request.method != 'POST':
        if not logged_in():
            return redirect(url_for('login'))
        if is_admin():
            return redirect(url_for('mission_control'))

    picture = request.files['file']
    
    #Error if no filename given
    if picture.filename == '':
        session['error'] = "No file selected! Please select a file!"
        return redirect(url_for('my_account'))
    
    #If the picture is a correct file type
    if verify_picture(picture.filename):

        #Insert filename into database
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
        
        #Only enable launch if the launch process is not alive
        global launch_process

        if not launch_process.is_alive():
            session['error'] = "Launch failure! There is already a launch in progress!"
            return redirect(url_for('mission_control'))

        #Add selected pads to launch list
        launch_list = []
        for pad in pads:
            if pad.name in session['selectedpads'] and pad.connected:
                launch_list.append(pad)

        #Launch the qualified pads
        launch_process = Process(target=process_launch, args=(launch_list,))
        session.pop('selectedpads', None)

    return redirect(url_for('mission_control'))

@app.route('/user_launch/<index>', methods = ['GET', 'POST'])
def user_launch(index):

    #Redirects
    if request.method != 'POST':
        if not logged_in():
            return redirect(url_for('login'))
        if is_admin():
            return redirect(url_for('mission_control'))
        else:
            return redirect(url_for('my_account'))

    #Only enable launch if the launch process is not alive
    global launch_process

    if not launch_process.is_alive():
        session['error'] = "Launch failure! There is already a launch in progress!"
        return redirect(url_for('user_launch_page'))
    
    #Add the pad associated with the index associated with the user to the launch list
    launch_list = []
    index = int(index)
    pad = pads[index]
    launch_list.append(pad)
    
    #Launch qualified pads
    launch_process = Process(target=process_launch, args=(launch_list,))

    return redirect(url_for('user_launch_page'))
    
@app.route('/user_launch_page', methods = ['POST', 'GET'])
def user_launch_page():

    #Redirects
    if not logged_in():
        return redirect(url_for('login'))
    if is_admin():
        return redirect(url_for('mission_control'))
    
    #Get authorized users list
    rocket_connected = False
    authorized = False
    authorized_users = db_get_authorized_users()

    index = -1
    for i in range(len(authorized_users)):
        if session['username'] == authorized_users[i]:
            index = i
    
    #Get whether or not rocket is connected and user is authorized
    if index != -1:
        pads[index].check_connection()
        if pads[index].connected:
            rocket_connected = True
    
    if session['username'] in authorized_users:
        authorized = True

    #Render user launch page    
    return render_template('launch.html', rocket_connected = rocket_connected, authorized = authorized, index = index)

@app.route('/verify/<frompage>/<topage>/<prompt>', methods = ['POST', 'GET'])
def verify(frompage, topage, prompt):
    
    #Redirects
    if request.method != 'POST':
        if not logged_in():
            return redirect(url_for('login'))
        if is_admin():
            return redirect(url_for('mission_control'))
        else:
            return redirect(url_for('my_account'))

    #Render verify page
    return render_template('verify.html', frompage=frompage, topage=topage, prompt=prompt)

@app.route('/launch_config')
def launch_config():

    #Redirects
    if not logged_in():
        return redirect(url_for('login'))
    if not is_admin():
        return redirect(url_for('my_account'))

    #Get: all users, all authorized users, the record launch setting,
    #and the recording duration setting
    users = db_get_usernames()
    authorized_users = db_get_authorized_users()
    record_launch = db_get_setting('RECORDLAUNCH')
    recording_duration = db_get_setting('RECORDINGDURATION')

    #Render launch configuration page
    return render_template('launch_config.html', pads = pads, users = users, authorized_users = authorized_users, record_launch = record_launch, recording_duration = recording_duration)

@app.route('/videos', methods = ['GET', 'POST'])
def videos():

    #Get videos from database
    videos = db_get_videos()
    videos_temp = videos

    empty_user = False
    user = 'all'

    if request.method == 'POST':
        user = request.form['search-bar']
    
    video_list = []

    if user == '':
        user = 'all'
    else:
        for video in videos:
            if user in video.users:
                video_list.append(video)
        
        videos = video_list
        
    if len(video_list) == 0 and user != 'all':
        user = 'all'
        session['error'] = "Specified user not found. Please try again!"
    
    if user != 'all':
        session['success'] = "Showing results for: " + user
    else:
        videos = videos_temp
    
    #Fill matrix with video objects
    for i in range(len(videos)):
        videos[i].name = url_for('static', filename = 'media/videos/' + videos[i].name)
        for j in range(len(videos[i].pictures)):
            videos[i].pictures[j] = url_for('static', filename = 'media/profile_pictures/' + videos[i].pictures[j])

    #Render video page
    return render_template('videos.html', videos = videos)

@app.route('/privacy')
def privacy():
    #Render privacy page
    return render_template('privacy.html')

#Methods-----------------------------------------------------------------------
#Get whether a user is logged in
def logged_in():
    try:
        val = session['username']
        return True

    except:
        return False

#Get whether a user is an admin
def is_admin():
    if 'username' not in session:
        return False

    if 'admin' not in session:
        return False

    return session['admin']

#Get pad object from given name
def get_pad(name):
    for pad in pads:
        if pad.name == name:
            return pad
    return None

#Check if file ends with an allowed extension
def verify_picture(filename):
    for extension in ALLOWED_PICTURE_EXTENSIONS:
        if filename.lower().endswith(extension):
            return True
    
    return False

#Launch rockets
def process_launch(provided_pads):
    #Get authorized users
    authorized_users = db_get_authorized_users()

    #Get if all are "None"
    no_users = True

    for user in authorized_users:
        if user != "None":
            no_users = False 

    #Start video thread before launches
    if not no_users:
        Thread(target=take_video, args=()).start()
    
    #Launch each pad
    for pad in provided_pads:
        if pad.connected:
            pad.launch()

    #Deauthorize any users associated with the provided pads
    user_list = []

    for i in range(len(pads)):
        if pads[i] in provided_pads:
            user_list.append(authorized_users[i])

    for user in users_list:
        db_update_authorized_user(user, 'None')

if __name__ == '__main__':
    app.run(debug=True, use_reloader = False)

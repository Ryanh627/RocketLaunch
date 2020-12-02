#Developed and owned by Benjamin Eckert, Peter Gifford, and Ryan Hansen of Western Michigan University.

#database.py controls database functionality

#Functions written in this module were developed by referencing sqlite3 documentation. sqlite3 nor the information provided by its documentation are owned by the aforementioned individuals.

import sqlite3, secrets, hashlib, time
from queries import *
from video import *

DIR = "/home/pi/RocketLaunch/Source/WebApp/"
DB_NAME = "rocketlaunch.db"

def db_init(num_pads):
    #Create database if it does not exist
    db = db_connect()

    #Create tables if they do not exist
    db.execute(QUERY_CREATE_TABLE_USERS)
    db.execute(QUERY_CREATE_TABLE_SETTINGS)
    db.execute(QUERY_CREATE_TABLE_AUTHORIZEDUSERS)
    db.execute(QUERY_CREATE_TABLE_VIDEOS)

    #Close connection
    db.close()

    #Create admin user if it does not exist
    if not db_admin_exists():
        db_signup("admin", "admin")

    #Create settings if they do not exist
    db_settings_init()

    #Clear any lingering authorized users
    db_erase_authorized_users()

def db_connect():
    try:
        con = sqlite3.connect(DIR + DB_NAME, isolation_level = None)
    except:
        print("An error has occurred!")

    finally:
        return con

def db_admin_exists():
    try:
        #Connect to database
        con = db_connect()
        db = con.cursor()

        #Get all users in database and check for an admin
        admins = db.execute(QUERY_USERS_GET_ISADMIN_ANY).fetchall()
        
        if len(admins) != 0:
            return True
        else:
            return False

    except Exception as e:
        print(e)
        if con is not None:
            con.close()
        return None

def db_login(username, password):
    try:
        #Error if username or password is empty
        if username == "" or password == "":
            return False, False

        #Connect to database
        con = db_connect()
        db = con.cursor()

        #Get salt for user in database
        params = [username]
        fetch = db.execute(QUERY_USERS_GET_SALT, params).fetchone()
        dbSalt = fetch[0]

        #Generate local hash of password
        localHash = db_hash(password, dbSalt)

        #Get hash in database
        params = [username]
        dbHash = db.execute(QUERY_USERS_GET_PASSWORD, params).fetchone()[0]

        #Get admin status
        params = [username]
        admin = db.execute(QUERY_USERS_GET_ISADMIN, params).fetchone()[0]
        if admin == 1:
            admin = True
        else:
            admin = False

        #Close database
        con.close()

    except:
        #Login fails if there are any errors
        if con is not None:
            con.close()
        return False, False
    
    #Login either fails or doesn't depending on if the hashes match
    return localHash == dbHash, admin

def db_signup(username, password):
    try:
        #Error if username or password is empty
        if username == "" or password == "":
            return False, False

        #Error if username is "None", "all", or contains "&"
        if username == "None" or username == "all" or '&' in username:
            return False, False

        #Connect to database
        con = db_connect()
        db = con.cursor()

        #Generate salt for password
        localSalt = secrets.token_urlsafe(32)

        #Generate hash for password
        localHash = db_hash(password, localSalt)

        #Insert password hash, username, and salt
        admin = False
        if username == "admin":
            admin = True

        params = [username, admin, localHash, localSalt]
        db.execute(QUERY_USERS_INSERT, params)

        #Close database
        con.close()
    
        return True, admin

    except Exception as e:
        print(e)
        if con is not None:
            con.close()
        return False, False

def db_change_password(username, current_password, new_password):
    #Error if current or new password are empty
    if current_password == "" or new_password == "":
        return False

    try:
        #Connect to database
        con = db_connect()
        db = con.cursor()

        #Get salt for user in database
        params = [username]
        fetch = db.execute(QUERY_USERS_GET_SALT, params).fetchone()
        dbSalt = fetch[0]

        #Generate local hash of password
        localHash = db_hash(current_password, dbSalt)

        #Get hash in database
        params = [username]
        dbHash = db.execute(QUERY_USERS_GET_PASSWORD, params).fetchone()[0]
        
        #Error if passwords do not match
        if localHash != dbHash:
            return False
        
        #Generate new password hash
        localHash = db_hash(new_password, dbSalt)

        #Update hash in database
        params = [localHash, username]
        db.execute(QUERY_USERS_UPDATE_PASSWORD, params)
        
        #Close database
        con.close()

        return True

    except:
        if con is not None:
            con.close()
        return False

def db_change_username(actual_username, current_username, new_username):
    #Error if current or new username are empty
    if current_username == "" or new_username == "":
        return False

    try:
        #Connect to database
        con = db_connect()
        db = con.cursor()
        
        #Error if actual_username and current_username do not match
        if actual_username != current_username:
            return False
        
        #Update username in USERS database table
        params = [new_username, actual_username]
        db.execute(QUERY_USERS_UPDATE_USERNAME, params)

        #Update username in AUTHORIZEDUSERS database table
        db.execute(QUERY_AUTHORIZEDUSERS_UPDATE_USERNAME, params)

        #Update username in VIDEOS database table
        users_matrix = []
        videos = db.execute(QUERY_VIDEOS_GET_USERS).fetchall()
        for video in videos:
            old_users_str = video[0]
            users_arr = video[0].split('&')
            new_users_str = ''
            
            for i in range(len(users_arr)):
                if users_arr[i] == actual_username:
                    users_arr[i] = new_username
                new_users_str = new_users_str + users_arr[i]
                if i != len(users_arr) - 1:
                    new_users_str = new_users_str + '&'
            
            users_matrix.append([new_users_str, old_users_str])

        for user in users_matrix:
            params = [user[0], user[1]]
            db.execute(QUERY_VIDEOS_UPDATE_USERS, params)

        #Close database
        con.close()

        return True

    except Exception as e:
        print(e)
        if con is not None:
            con.close()
        return False
 

def db_delete(username):
    try:
        #Connect to database
        con = db_connect()
        db = con.cursor()

        #Delete user from USERS table
        params = [username]
        db.execute(QUERY_USERS_DELETE, params)

        #Delete user from AUTHORIZEDUSERS table
        db.execute(QUERY_AUTHORIZEDUSERS_DELETE, params)

        #Delete user in VIDEOS database table
        users_matrix = []
        videos = db.execute(QUERY_VIDEOS_GET_USERS).fetchall()
        for video in videos:
            old_users_str = video[0]
            users_arr = video[0].split('&')
            new_users_str = ''
            new_users_arr = []
            
            for i in range(len(users_arr)):
                if users_arr[i] != username:
                    new_users_arr.append(users_arr[i])

            for user in new_users_arr:
                new_users_str = new_users_str + user + '&'
            new_users_str = new_users_str[:-1]
            
            users_matrix.append([new_users_str, old_users_str])

        for user in users_matrix:
            params = [user[0], user[1]]
            db.execute(QUERY_VIDEOS_UPDATE_USERS, params)

        #Delete any videos without users
        db.execute(QUERY_VIDEOS_DELETE_EMPTY)

        #Close database
        con.close()

        return True

    except:
        if con is not None:
            con.close()
        return False

def db_change_picture(username, filename):
    try:
        #Connect to database
        con = db_connect()
        db = con.cursor()

        #Update picture path in database
        params = [filename, username]
        db.execute(QUERY_USERS_UPDATE_PICTURE, params)

        #Close database
        con.close()

        return True

    except:
        if con is not None:
            con.close()
        return False

def db_get_picture(username):
    try:
        #Connect to database
        con = db_connect()
        db = con.cursor()
        
        #Get picture for specified user in database
        params = [username]
        picture = db.execute(QUERY_USERS_GET_PICTURE, params).fetchone()[0]

        #Close database
        con.close()

        return picture

    except:
        if con is not None:
            con.close()
        return None

def db_get_setting(setting):
    try:
        #Connect to database
        con = db_connect()
        db = con.cursor()
        
        #Get value for specified setting in database
        if setting == "RECORDLAUNCH":
            setting_val = db.execute(QUERY_SETTINGS_GET_RECORDLAUNCH).fetchone()[0]
        
        elif setting == "RECORDINGDURATION":
            setting_val = db.execute(QUERY_SETTINGS_GET_RECORDINGDURATION).fetchone()[0]

        #Close database
        con.close()

        return setting_val

    except:
        if con is not None:
            con.close()
        return None

def db_update_setting(setting, val):
    try:
        #Connect to database
        con = db_connect()
        db = con.cursor()
        
        #Update setting value for specified setting
        params = [val]

        if setting == "RECORDLAUNCH":
            db.execute(QUERY_SETTINGS_UPDATE_RECORDLAUNCH, params)
        elif setting == "RECORDINGDURATION":
            db.execute(QUERY_SETTINGS_UPDATE_RECORDINGDURATION, params)

        #Close database
        con.close()

        return True

    except Exception as e:
        print(e)
        if con is not None:
            con.close()
        return False

def db_get_usernames():
    try:
        #Connect to database
        con = db_connect()
        db = con.cursor()
        
        #Get all users in database
        users = db.execute(QUERY_USERS_GET_USERNAMES).fetchall()

        userlist = []
        for user in users:
            userlist.append(user[0])

        #Close database
        con.close()

        return userlist

    except:
        if con is not None:
            con.close()
        return None

def db_settings_init():
    try:
        #Connect to database
        con = db_connect()
        db = con.cursor()
        
        #Get all settings columns from the database
        settings = db.execute(QUERY_SETTINGS_GET_ALL).fetchall()

        exists = False
        if len(settings) != 0:
            exists = True

        if exists:
            return False

        db.execute(QUERY_SETTINGS_INSERT)

        #Close database
        con.close()

        return True

    except:
        if con is not None:
            con.close()
        return False

def db_get_authorized_users():
    try:
        #Connect to database
        con = db_connect()
        db = con.cursor()
        
        #Get all authorized users from the database
        authorized_users = db.execute(QUERY_AUTHORIZEDUSERS_GET_USERNAMES).fetchall()
        
        authorized_usernames = []
        
        for user in authorized_users:
            authorized_usernames.append(user[0])

        #Close database
        con.close()

        return authorized_usernames

    except:
        if con is not None:
            con.close()
        return None

def db_update_authorized_user(username, new):
    try:
        #Connect to database
        con = db_connect()
        db = con.cursor()
        
        #Update authorized username in the database
        params = [new, username]
        db.execute(QUERY_AUTHORIZEDUSERS_UPDATE_USERNAME, params)

        #Close database
        con.close()

        return True

    except Exception as e:
        print(e)
        if con is not None:
            con.close()
        return False

def db_insert_authorized_user(user):
    try:
        #Connect to database
        con = db_connect()
        db = con.cursor()

        #Insert authorized user into database
        params = [user]
        db.execute(QUERY_AUTHORIZEDUSERS_INSERT, params)

        #Close database
        con.close()

        return True

    except Exception as e:
        print(e)
        if con is not None:
            con.close()
        return False

def db_clear_authorized_users():
    try:
        #Connect to database
        con = db_connect()
        db = con.cursor()
        
        #Clear all authorized users from the database
        db.execute(QUERY_AUTHORIZEDUSERS_CLEAR)

        #Close database
        con.close()

        return True

    except Exception as e:
        print(e)
        if con is not None:
            con.close()
        return False

def db_erase_authorized_users():
    try:
        #Connect to database
        con = db_connect()
        db = con.cursor()
        
        #Delete all authorized users from database
        db.execute(QUERY_AUTHORIZEDUSERS_ERASE)

        #Close database
        con.close()

        return True

    except:
        if con is not None:
            con.close()
        return False

def db_insert_video(users, path):
    try:
        #Connect to database
        con = db_connect()
        db = con.cursor()
        
        #Place users into single string
        users_str = ''
        for i in range(len(users)):
            users_str = users_str + users[i]
            if i != len(users):
                users_str = users_str + '&'

        #Insert video path into database
        params = [path, users_str]
        db.execute(QUERY_VIDEOS_INSERT, params)

        #Close database
        con.close()

        return True

    except Exception as e:
        print(e)
        if con is not None:
            con.close()
        return False

def db_get_videos():
    try:
        #Connect to database
        con = db_connect()
        db = con.cursor()
        
        #Get all authorized users from the database
        videos = db.execute(QUERY_VIDEOS_GET_ALL).fetchall()

        #Format values into a video object for parsing
        video_list = []
        for video in videos:
            picture_list = []
            name = video[0]
            user_list = video[1].split('&')
            timestamp = video[2]
            for user in user_list:
                picture_list.append(db_get_picture(user))
            video_list.append(Video(name, user_list, picture_list, timestamp))

        #Close database
        con.close()

        return video_list

    except:
        if con is not None:
            con.close()
        return None


def db_authorization_timeout():
    wait_time = 60
    time.sleep(wait_time)
    db_erase_authorized_users()

def db_hash(password, salt):
    ret = hashlib.sha512((salt + password).encode())
    ret = ret.digest()
    return ret

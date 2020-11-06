import sqlite3, secrets, hashlib
from queries import *

DIR = "/home/pi/RocketLaunch/Source/WebApp/"
DB_NAME = "rocketlaunch.db"

def db_init():
    #Create database if it does not exist
    db = db_connect()

    #Create tables if they do not exist
    db.execute(QUERY_CREATE_TABLE_USERS)

    #Close connection
    db.close()

    #Create admin user if it does not exist
    db_signup("admin", "admin")

def db_connect():
    try:
        con = sqlite3.connect(DIR + DB_NAME, isolation_level = None)
    except:
        print("An error has occurred!")

    finally:
        return con

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

        authorized = False

        params = [username, admin, localHash, localSalt, authorized]
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

        #Update username in database
        params = [new_username, actual_username]
        db.execute(QUERY_USERS_UPDATE_USERNAME, params)

        #Close database
        con.close()

        return True

    except:
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

def db_get_authorized(username):
    try:
        #Connect to database
        con = db_connect()
        db = con.cursor()
        
        #Get authorization for specified user in database
        params = [username]
        authorized = db.execute(QUERY_USERS_GET_AUTHORIZED, params).fetchone()[0]

        #Close database
        con.close()

        return authorized

    except:
        if con is not None:
            con.close()
        return False

def db_update_authorized(username, val):
    try:
        #Connect to database
        con = db_connect()
        db = con.cursor()
        
        #Update authorization of specified user
        params = [val, username]
        db.execute(QUERY_USERS_UPDATE_AUTHORIZED, params)

        #Close database
        con.close()

        return True

    except:
        if con is not None:
            con.close()
        return False


def db_hash(password, salt):
    ret = hashlib.sha512((salt + password).encode())
    ret = ret.digest()
    return ret

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
        
        params = [admin, username, localHash, localSalt]
        db.execute(QUERY_USERS_INSERT, params)

        #Close database
        con.close()
    
        return True, admin

    except:
        return False, False

def db_hash(password, salt):
    ret = hashlib.sha512((salt + password).encode())
    ret = ret.digest()
    return ret

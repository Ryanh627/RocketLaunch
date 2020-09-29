import sqlite3
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

def db_connect():
    try:
        con = sqlite3.connect(DIR + DB_NAME)
    except:
        print("An error has occurred!")

    finally:
        return con

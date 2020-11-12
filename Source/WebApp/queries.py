QUERY_CREATE_TABLE_USERS = "CREATE TABLE IF NOT EXISTS USERS (USERNAME NVARCHAR(255) PRIMARY KEY, ISADMIN INTEGER NOT NULL, PASSWORD VARBINARY(255) NOT NULL, SALT NVARCHAR(255) NOT NULL, PICTURE NVARCHAR(1024) DEFAULT 'default.png');"

QUERY_CREATE_TABLE_SETTINGS = '''CREATE TABLE IF NOT EXISTS SETTINGS (RECORDLAUNCH INTEGER DEFAULT 0, RECORDINGDURATION FLOAT DEFAULT 5);'''

QUERY_SETTINGS_INSERT = '''INSERT INTO SETTINGS (RECORDLAUNCH, RECORDINGDURATION) VALUES (0, 5);'''

QUERY_CREATE_TABLE_AUTHORIZEDUSERS = '''CREATE TABLE IF NOT EXISTS AUTHORIZEDUSERS (USERNAME NVARCHAR(255));'''

QUERY_CREATE_TABLE_VIDEOS = '''CREATE TABLE IF NOT EXISTS VIDEOS (NAME NVARCHAR(1024) PRIMARY KEY, USERS NVARCHAR(1024) NOT NULL);'''

QUERY_USERS_GET_USERNAMES = '''SELECT USERNAME FROM USERS WHERE 1==1;'''

QUERY_USERS_GET_SALT = '''SELECT SALT FROM USERS WHERE USERNAME == ?;'''

QUERY_USERS_GET_PASSWORD = '''SELECT PASSWORD FROM USERS WHERE USERNAME == ?;'''

QUERY_USERS_INSERT = '''INSERT INTO USERS (USERNAME, ISADMIN, PASSWORD, SALT) VALUES (?, ?, ?, ?);'''

QUERY_USERS_DELETE = '''DELETE FROM USERS WHERE USERNAME == ?;'''

QUERY_USERS_GET_ISADMIN = '''SELECT ISADMIN FROM USERS WHERE USERNAME == ?;'''

QUERY_USERS_GET_LOGGEDIN = '''SELECT LOGGEDIN FROM USERS WHERE USERNAME == ?;'''

QUERY_USERS_UPDATE_PASSWORD = '''UPDATE USERS SET PASSWORD = ? WHERE USERNAME == ?;'''

QUERY_USERS_UPDATE_USERNAME = '''UPDATE USERS SET USERNAME = ? WHERE USERNAME == ?;'''

QUERY_USERS_UPDATE_PICTURE = '''UPDATE USERS SET PICTURE = ? WHERE USERNAME == ?;'''

QUERY_USERS_UPDATE_LOGGEDIN = '''UPDATE USERS SET LOGGEDIN = ? WHERE USERNAME ==?;'''

QUERY_USERS_GET_PICTURE = '''SELECT PICTURE FROM USERS WHERE USERNAME == ?;'''

QUERY_SETTINGS_GET_RECORDLAUNCH = '''SELECT RECORDLAUNCH FROM SETTINGS WHERE 1==1;'''

QUERY_SETTINGS_GET_RECORDINGDURATION = '''SELECT RECORDINGDURATION FROM SETTINGS WHERE 1==1;'''

QUERY_SETTINGS_UPDATE = '''UPDATE SETTINGS SET ? = ? WHERE 1==1;'''

QUERY_SETTINGS_GET_ALL = '''SELECT * FROM SETTINGS WHERE 1==1;'''

QUERY_SETTINGS_UPDATE_RECORDLAUNCH = '''UPDATE SETTINGS SET RECORDLAUNCH = ? WHERE 1==1;'''

QUERY_SETTINGS_UPDATE_RECORDINGDURATION = '''UPDATE SETTINGS SET RECORDINGDURATION = ? WHERE 1==1;'''

QUERY_AUTHORIZEDUSERS_CLEAR = '''UPDATE AUTHORIZEDUSERS SET USERNAME = 'None' WHERE 1==1;'''

QUERY_AUTHORIZEDUSERS_INSERT = '''INSERT INTO AUTHORIZEDUSERS (USERNAME) VALUES (?);'''

QUERY_AUTHORIZEDUSERS_ERASE = '''DELETE FROM AUTHORIZEDUSERS WHERE 1==1;'''

QUERY_AUTHORIZEDUSERS_GET_USERNAMES = '''SELECT USERNAME FROM AUTHORIZEDUSERS WHERE 1==1;'''

QUERY_VIDEOS_INSERT = '''INSERT INTO VIDEOS (NAME, USERS) VALUES (?, ?);'''

QUERY_VIDEOS_GET_ALL = '''SELECT * FROM VIDEOS WHERE 1==1;'''

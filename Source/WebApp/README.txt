Information about this directory:

1) app.py contains the start of the python code and manages the flow of the entire
   application

2) templates is a folder for storing html files for use with app.py

3) static is a folder for storing 'static' files for use with the templates such as 
   css and js files

4) launch.py manages the launch process when called from app.py

6) database.py handles all database functionality when called from app.py

7) queries.py is a library of string constants for representing queries meant for
   use by database.py

8) rocketlaunch.wsgi is a file used by apache2 to work with Flask used with app.py

9) rocketlaunch.db (if it exists) is the database used with database.py

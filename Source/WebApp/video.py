#Developed and owned by Benjamin Eckert, Peter Gifford, and Ryan Hansen of Western Michigan University.

#video.py facilitates the creation of video objects that hold video information

class Video:
    def __init__(self, name, users, pictures, timestamp):
        self.name = name
        self.users = users
        self.pictures = pictures
        self.timestamp = timestamp

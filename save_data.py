import os
import getpass
import csv

class save_data():
    def __init__(self):
        self.last_status = 0
        username = getpass.getuser()
        self.path = "C:/Users/"+username+"/Desktop/data/"
        if not(os.path.isdir(self.path)):
            os.makedirs((os.path.join(self.path)))

    def save_data(self, values):
        if values[0] != 0:
            if self.last_status != values[0]:
                self.last_status = values[0]
            # else if 
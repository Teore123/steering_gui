import os
import getpass
import csv
from datetime import datetime

class save_data():
    mcu_mode = {"Setup":0,"Standby":1,"Emergency_stop":2,
                "R2Z":3,"pause":4,"L2L":5,"constStr":6,"SineStr":7}
    def __init__(self):
        self.last_status = 0
        username = getpass.getuser()
        self.path = "C:/Users/"+username+"/Desktop/data/"
        if not(os.path.isdir(self.path)):
            os.makedirs((os.path.join(self.path)))

    def save_data(self, status):
        if status[0] != 0:                                                                                            # Motor On
            if status[2] == self.mcu_mode["constStr"] or status[2] == self.mcu_mode["SineStr"]:
                if self.last_status != status[2]:                                                                       # Init
                    self.last_status = status[2]
                    now = datetime.now()
                    file_name = self.path + now.strftime('%y%m%d_%H%M%S') + list(self.mcu_mode.keys())[status[2]] + '.csv'
                    self.f = open(file_name,'w', newline='')
                    self.wr = csv.writer(self.f)
                    self.wr.writerow(["Angle(deg)","Torque(Nm)"])
                    self.wr.writerow([status[3], status[4]])
                else:
                    self.wr.writerow([status[3], status[4]])
            elif status[2] == self.mcu_mode["pause"]:
                pass
            else:
                try:
                    self.f.close()
                except:
                    pass
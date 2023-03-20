import serial
import serial.tools.list_ports as sp
import numpy as np
import threading
from multiprocessing import Queue
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QMessageBox
from Steer_Status import Steer_Status

class Serial_Comm(QObject):
    params = pyqtSignal(list)
    
    def __init__(self, status):
        super().__init__()
        self.status = status
        self.flag = threading.Event()
        self.q = Queue()

    def set_comoprt(self):
        list = sp.comports()
        com_port = {}

        for port, desc, _ in sorted(list):
            com_port[desc] = port
        return com_port

    def set_baudrate(self):
        return ['9600', '19200', '38400', '57600', '115200']

    def connect_serial(self, port, baud):
        return serial.Serial(port, baud)
    
    def write(self, data):
        self.ser.write(data)
    
    def start(self, port, baud):
        t=threading.Thread(target=self.read_from_arduino, args=(port, baud), daemon=True)
        t.start()

    def read_from_arduino(self, port, baud):
        self.ser = self.connect_serial(port, baud)
        # self.ser.close()
        # self.ser.open()
        while self.ser.is_open:
            if self.ser.readable():
                try:
                    values = self.set_status(self.ser.read(9))
                    self.params.emit(values)
                except:
                    self.q.put(False)
                    self.ser.close()
    
    def set_status(self, data):
        a = self.set_MCU_status(data[:1])
        b = self.set_Motor_status(data[1:])
        return list(a) + list(b)

    def set_MCU_status(self, data):
        data = data[0]
        motor_status = data // 0x80
        BLE_status = (data & 0x40) // 0x40
        MCU_status = data & 0x3F
        return motor_status, BLE_status, MCU_status
        
    def set_Motor_status(self, data):
        torque = self.cal_bytes(data[2:4]) / 0x800 * self.status.Kt * 33
        encoder = self.cal_bytes(data[6:]) / self.status.enc_counter * 360
        return encoder, torque
        
    def cal_bytes(self, data):
        return np.array((data[1] << 8) | data[0]).astype(np.int16)
    
    def send_str(self, mode, speed, cycle, offset, amp):
        self.ser.write(bytes([mode, speed, cycle, offset, amp]))
        
    def send_mode(self, mode):
        self.send_str(mode, 0, 0, 0, 0)

def main():
    status = Steer_Status()
    test = Serial_Comm(status)
    # ser = test.connect_serial()
    test.read_from_arduino()

if __name__ == '__main__':
    main()
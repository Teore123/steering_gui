import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
import numpy as np
import time
import threading

from Steer_Status import Steer_Status
from Serial_Comm import Serial_Comm
from qml_plot import qml_Chart
from save_data import save_data

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self): 
        self.center()
        self.status = Steer_Status()
        self.Serial = Serial_Comm(self.status)
        self.Serial.params.connect(self.update_list)
        self.save_data = save_data()
        self.setWindowTitle('Steering Robot')
        
        grid = QGridLayout(self)
        grid.addLayout(self.setting_layout(),1,0)
        grid.addLayout(self.plot_layout(),1,1)
        grid.setColumnStretch(1,1)
        self.set_btn_disable()
        self.serial_refresh()
    
    def center(self): # Mack GUI Center
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

###################### Setting Tab Layout ###################### 
    def setting_layout(self): # Setting Layout vbox
        lbl_confirm = QLabel('<Confirmation before Testing>')
        lbl_font = lbl_confirm.font()
        lbl_font.setPointSize(12)
        lbl_font.setBold(True)
        lbl_confirm.setFont(lbl_font)
        
        self.Check1 = QCheckBox('Vehicle Start-Up')
        self.Check2 = QCheckBox('Equipment Installation')

        check_vbox = QVBoxLayout()
        check_vbox.addWidget(lbl_confirm)
        check_vbox.addWidget(self.Check1)
        check_vbox.addWidget(self.Check2)

        check_group = QGroupBox("Check List")
        check_group.setLayout(check_vbox)
        check_group.setStyleSheet("background-color: #ffffff")

        self.folder_btn= QPushButton("Folder Select", self)
        self.folder_btn.clicked.connect(self.directory_select)

        self.lbl_path = QLabel()
        self.lbl_path.setText(self.save_data.path)
        
        test_name_hbox = QVBoxLayout()
        test_name_hbox.addWidget(self.lbl_path)
        test_name_hbox.addWidget(self.folder_btn)
        path_group = QGroupBox("Path")
        path_group.setLayout(test_name_hbox)

        vbox = QVBoxLayout()
        
        vbox.addWidget(check_group)
        vbox.addWidget(self.serial_select())
        vbox.addWidget(self.ble_select())
        vbox.addWidget(path_group)
        vbox.addWidget(self.mtr_mode_select())
        vbox.addStretch(1)
        vbox.addLayout(self.set_btn())
        
        return vbox
    
    def serial_select(self):# Select Serial device and baudrate
        self.port_cb = QComboBox(self)
        self.baud_cb = QComboBox(self)

        self.port_dict = self.Serial.set_comoprt()
        
        lbl_Comport = QLabel('Port : ')
        
        port_hbox = QHBoxLayout()
        port_hbox.addWidget(lbl_Comport)
        port_hbox.addWidget(self.port_cb)
                
        lbl_Baud = QLabel('Baudrate : ')
        self.baud_cb.addItems(self.Serial.set_baudrate())
        self.baud_cb.setCurrentText('115200')

        self.btn_connect = QPushButton("Connect")
        self.btn_connect.clicked.connect(self.serial_connect)
        
        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.clicked.connect(self.serial_refresh)
        
        baud_hbox = QHBoxLayout()
        baud_hbox.addWidget(lbl_Baud)
        baud_hbox.addWidget(self.baud_cb)
        
        groupbox = QGroupBox('Serial Connect') 
        vbox = QVBoxLayout()
        vbox.addLayout(port_hbox)
        vbox.addLayout(baud_hbox)
        vbox.addWidget(self.btn_refresh)
        vbox.addWidget(self.btn_connect)
        
        groupbox.setLayout(vbox)
        
        return groupbox
    
    def serial_refresh(self):
        self.port_cb.clear()
        self.port_dict = self.Serial.set_comoprt()
        if len(self.port_dict) != 0:
            self.port_cb.addItems(self.port_dict.keys())
    
    def serial_connect(self):
        if self.port_cb.currentText()=='':
            msg = 'Connect your device and Push the refresh button!'
            QMessageBox.about(self, "Connecting", msg)
        else:
            port = self.port_dict[self.port_cb.currentText()]
            baud = self.baud_cb.currentText()            
            msg = f'Device Inform Correct?\
                    \nComoprt : {port}\
                    \nBaudrate : {baud}'
            reply = QMessageBox.question(self, 'Message', msg,
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                self.Serial.start(port, baud)
                self.serial_isconnected()
    
    def serial_isconnected(self):
        self.btn_connect.setDisabled(True)
        t = threading.Thread(target=self.ser_isconnected, args=(), daemon=True)
        t.start()

    def ser_isconnected(self): # Serial connect Select Port & baudrate
        flag = True
        while flag:
            if not self.Serial.q.empty():
                flag = self.Serial.q.get()
                self.update_gui([0,0,-1,0,0])
                self.serial_refresh()
                self.btn_connect.setDisabled(False)
            time.sleep(1)
        QApplication.processEvents()
    
    def ble_select(self): # Select BLE device and Open Button
        self.BLE_cb = QComboBox()
        self.BLE_cb.addItem('COM1')
        self.BLE_cb.addItem('COM2')
        self.BLE_cb.addItem('COM3')
        self.BLE_cb.addItem('COM4')
        
        self.btn_BLE= QPushButton("Open", self)
        self.btn_BLE.clicked.connect(self.BLE_open)
        
        groupbox = QGroupBox('BLE Connect') 
        hbox = QHBoxLayout()
        hbox.addWidget(self.BLE_cb)
        hbox.addWidget(self.btn_BLE)
        groupbox.setLayout(hbox)
        
        return groupbox
    
    def BLE_open(self): # Connect BLE device
        msg = "BLE is not yet implemented."
        QMessageBox.about(self, "BLE Connect", msg)
    
    def mtr_mode_select(self): # select Motor mode // Setting(L2L), Const Str, Sine Str
        mode_tab = QTabWidget()
        mode_tab.addTab(self.Setting_tab(), "Setting")
        mode_tab.addTab(self.Const_Str_tab(), "Const Str")
        mode_tab.addTab(self.Sine_Str_tab(), "Sine Str")
        
        return mode_tab
    
    def Setting_tab(self): # Setting(L2L) Tab // CSV File location, Check list, Motor On/Off, L2L
        # self.btn_mtrOn = QPushButton('Motor ON')
        # self.btn_mtrOn.clicked.connect(self.mtrOn)

        # self.btn_mtrOff = QPushButton('Motor OFF')
        # self.btn_mtrOff.clicked.connect(self.mtrOff)
        
        # mtr_select_hbox = QHBoxLayout()
        # mtr_select_hbox.addWidget(self.btn_mtrOn)
        # mtr_select_hbox.addWidget(self.btn_mtrOff)
        
        self.btn_L2L = QPushButton('Measure Lock to Lock')
        self.btn_L2L.clicked.connect(self.L2L)
        
        self.btn_L2L_pause = QPushButton('Pause / Restart')
        self.btn_L2L_pause.clicked.connect(self.pause)
        
        setting_vbox = QVBoxLayout()
        # setting_vbox.addLayout(mtr_select_hbox)
        setting_vbox.addWidget(self.btn_L2L)
        setting_vbox.addWidget(self.btn_L2L_pause)
        
        tab = QWidget()
        tab.setLayout(setting_vbox)
        
        return tab
    
    def directory_select(self):
        self.directory_path = QFileDialog.getExistingDirectory(self, "select Directory")
        self.lbl_path.setText(self.directory_path + '/')
        self.lbl_path.setWordWrap(True)
        self.save_data.path = self.lbl_path.text()
        
    def mtrOn(self): # Motor On button
        self.Serial.send_mode(self.status.mtrOn) # mode
    
    def mtrOff(self): # Motor Off button
        self.Serial.send_mode(self.status.mtrOff) # mode
        
    def set_btn_disable(self):
        self.btn_BLE.setDisabled(True)
        self.btn_r2z.setDisabled(True)

        # self.btn_mtrOff.setDisabled(True)
        # self.btn_mtrOn.setDisabled(True)
        self.btn_L2L.setDisabled(True)
        self.btn_L2L_pause.setDisabled(True)

        self.btn_ConstStr_start.setDisabled(True)
        self.btn_ConstStr_pause.setDisabled(True)

        self.btn_SineStr_start.setDisabled(True)
        self.btn_SineStr_pause.setDisabled(True)
    
    def Const_Str_tab(self): # Const Str Tab // Velocity, Range, Start, Pause
        vel_lbl = QLabel('Velocity(0.5 ~ 1.8) :')
        self.Const_RPS = QDoubleSpinBox(self)
        self.Const_RPS.setRange(0.5, 1.8)
        self.Const_RPS.setSingleStep(0.1)
        self.Const_RPS.setValue(self.status.const_vel)

        rps_lbl = QLabel('RPS')
        vel_hbox = QHBoxLayout()
        vel_hbox.addWidget(vel_lbl)
        vel_hbox.addStretch(1)
        vel_hbox.addWidget(self.Const_RPS)
        vel_hbox.addWidget(rps_lbl)
        
        lbl_range = QLabel('Range(0%s ~ 450%s) :'%(chr(176),chr(176)))

        self.constStr_range = QSpinBox(self)
        self.constStr_range.setRange(0, 450)
        self.constStr_range.setValue(50)

        lbl_range2 = QLabel(chr(176))

        range_hbox = QHBoxLayout()
        range_hbox.addWidget(lbl_range)
        range_hbox.addStretch(1)
        range_hbox.addWidget(self.constStr_range)
        range_hbox.addWidget(lbl_range2)

        cycle_lbl = QLabel('Number of Cycle(1 ~ 256) : ')

        self.constStr_cycle = QSpinBox(self)
        self.constStr_cycle.setMaximum(256)
        self.constStr_cycle.setMinimum(1)
        self.constStr_cycle.setValue(self.status.const_cycle)

        cycle_unit_lbl = QLabel('Time')

        cycle_hbox = QHBoxLayout()
        cycle_hbox.addWidget(cycle_lbl)
        cycle_hbox.addStretch(1)
        cycle_hbox.addWidget(self.constStr_cycle)
        cycle_hbox.addWidget(cycle_unit_lbl)
        
        self.btn_ConstStr_start = QPushButton('Start Steering')
        self.btn_ConstStr_start.clicked.connect(self.constStr)
        
        self.btn_ConstStr_pause = QPushButton('Pause / Restart')
        self.btn_ConstStr_pause.clicked.connect(self.pause)
        
        constStr_vbox = QVBoxLayout()
        constStr_vbox.addLayout(vel_hbox)
        constStr_vbox.addLayout(range_hbox)
        constStr_vbox.addLayout(cycle_hbox)
        constStr_vbox.addWidget(self.btn_ConstStr_start)
        constStr_vbox.addWidget(self.btn_ConstStr_pause)
        
        tab = QWidget()
        tab.setLayout(constStr_vbox)
        
        return tab  
    
    def L2L(self): # send msg L2L to MCU
        self.Serial.send_mode(self.status.L2L) # mode

    def constStr(self): # send msg Const Str to MCU 
        # self.constStr_cycle.value()
        print("not yet4")
    
    def pause(self): # send msg Pause to MCU
        if self.is_pause:
            self.Serial.send_mode(self.status.Restart) # mode
        else:
            self.Serial.send_mode(self.status.pause) # mode
    
    def Sine_Str_tab(self): # Sine Str Tab // Initial Angle, Amplitude, Frequency, Cycle, Start, Pause
        Sine_Str_setting = ["Initial Angle(225%s ~ 675%s)"%(chr(176),chr(176)), "Sine Amplitude(0%s ~ 450%s)"%(chr(176),chr(176)),
                            "Sine Frequency(0 ~ 2)","Number of Cycle(1 ~ 256)" ]
        Sine_Str_set_unit = [chr(176), chr(176), "Hz", "Time" ]
        Sine_Str_set_value = [self.status.sine_angle, self.status.sine_amp, self.status.sine_freq, self.status.sine_cycle]
        Sine_Str_set_value_min = [225,0,0.1,1]
        Sine_Str_set_value_max = [675,450,2,256]
        
        SineStr_vbox = QVBoxLayout()
        self.Sine_Str_value = []
        for i in range(len(Sine_Str_setting)):
            if i != 2:
                self.Sine_Str_value.append(QSpinBox(self))
            else:
                self.Sine_Str_value.append(QDoubleSpinBox(self))
                self.Sine_Str_value[i].setSingleStep(0.1)
            self.Sine_Str_value[i].setMaximum(Sine_Str_set_value_max[i])
            self.Sine_Str_value[i].setMinimum(Sine_Str_set_value_min[i])
            self.Sine_Str_value[i].setValue(Sine_Str_set_value[i])
            
            Sine_Str_setting_lbl = QLabel(Sine_Str_setting[i] + " : ")
            Sine_Str_set_unit_lbl = QLabel(Sine_Str_set_unit[i])
            
            SineStr_hbox = QHBoxLayout()
            SineStr_hbox.addWidget(Sine_Str_setting_lbl)
            SineStr_hbox.addStretch(1)
            SineStr_hbox.addWidget(self.Sine_Str_value[i])
            SineStr_hbox.addWidget(Sine_Str_set_unit_lbl)
            
            SineStr_vbox.addLayout(SineStr_hbox)

        self.btn_SineStr_start = QPushButton('Start Steering')
        self.btn_SineStr_start.clicked.connect(self.sineStr)
        
        self.btn_SineStr_pause = QPushButton('Pause / Restart')
        self.btn_SineStr_pause.clicked.connect(self.pause)
        
        sineStr_vbox = QVBoxLayout()
        sineStr_vbox.addLayout(SineStr_vbox)
        sineStr_vbox.addWidget(self.btn_SineStr_start)
        sineStr_vbox.addWidget(self.btn_SineStr_pause)
        
        tab = QWidget()
        tab.setLayout(sineStr_vbox)
        
        return tab   
    
    def sineStr(self): # send msg Sine Str to MCU
        mode = self.status.SineStr
        data = []
        for value in self.Sine_Str_value:
            data.append(value.value())
        # data[0] = 
        data = data[2:] + data[:2]

        print(data)
        if data[0] + data[1] > 900 or data[0] - data[1] < 0:
            msg = 'Please adjust the range of Init Angle and Amplitude to be Small.'
            QMessageBox.about(self, "Connecting", msg)
        else:
            self.Serial.send_str(mode, data)
        print("not yet6")
    
    def set_btn(self): # make Button Return2zero & Emergency stop
        self.btn_r2z = QPushButton("Return to Zero")
        self.btn_r2z.clicked.connect(self.return2zero)
        
        self.emergency_btn = QPushButton("Motor OFF")
        self.emergency_btn.clicked.connect(self.emergency_stop)

        self.emergency_btn.setStyleSheet("background-color : red")
        font_stop = self.emergency_btn.font()
        font_stop.setPointSize(12)
        font_stop.setBold(True)
        self.emergency_btn.setFont(font_stop)
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.btn_r2z)
        vbox.addWidget(self.emergency_btn)
        
        return vbox
        
    def return2zero(self): # send msg Return2zero to MCU
        self.Serial.send_mode(self.status.R2Z)
    
    def emergency_stop(self): # send msg Emergency stop to MCU
        self.Serial.send_mode(self.status.mtrOff)
        
###################### Plot Layout ###################### 
    def plot_layout(self): # Setting Layout vbox
        self.status_lbl = QLabel()
        font = self.status_lbl.font()
        font.setPointSize(10)
        self.status_lbl.setFont(font)
        self.text_para = QLabel()
        self.text_para.setFixedHeight(62)
        self.text_para.setFont(font)
        status_hbox = QHBoxLayout()
        status_hbox.addWidget(self.status_lbl)
        status_hbox.addWidget(self.text_para)
        
        self.update_gui([0,0,-1,0,0])
        self.last_status = -1
        plot_vbox = QVBoxLayout()
        plot_vbox.addLayout(status_hbox)
        self.plot_title = ["Angle","Torque","CAN"]
        self.plot = []
        for i,name in enumerate(self.plot_title):
            self.plot.append(qml_Chart(name, i))
            plot_vbox.addWidget(self.plot[i].widget)
        return plot_vbox

###################### update backend ######################
    @pyqtSlot(list)
    def update_list(self, status):
        try:
            self.update_gui(status)
            self.append_data(status)
            self.btn_able(status)
                # self.save_data(values)
        except:
            self.Serial.q.put(True)
            self.Serial.ser.close()
    
    def update_gui(self, status): # Update Status in GUI
        self.status_lbl.setText(\
        "Motor Status        : " + self.status.disp_MS[status[0]] + "\n"
        "BLE Connection   : " + self.status.disp_BLE[status[1]] + "\n"
        "Mode in Progress : " + self.status.disp_Mode[status[2]])

        self.text_para.setText(\
        "<Real-time Parameters> \n"\
        "Angle  : %.2f "%status[3] + chr(176) + "\n"
        "Torque : %.2f  Nm" %status[4])
        self.text_para.setStyleSheet("background-color: #ffffff")
        self.is_pause = status[2] == 4
    
    def append_data(self,status):
        for i in range(2):
            self.status.data[i] = np.append(self.status.data[i][1:], status[i + 3])
        self.status.data[2] = np.append(self.status.data[2][1:], 0)
    
    def btn_able(self, status):
        if self.last_status != status[2]:
            self.set_btn_disable()
            for btn in self.status.able_list[status[2]]:
                exec("self.btn_" + btn + ".setDisabled(False)")
        self.last_status = status[2]

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    ex.show()
    app.exec_()
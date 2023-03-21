import numpy as np
class Steer_Status():
    mtrOff = 0
    mtrOn = 1
    R2Z = 2
    pause = 3
    Restart = 4
    L2L = 5
    ConstStr = 6
    SineStr = 7
    
    # Plot parameter
    time_interval = 10 / 1000  # ms
    plot_range = 10  # 10 sec data display
    
    # [xmin, xmax, ymin, ymax]    
    axis_limit = [[-5,5,0,360],[-5,5,-10,10],[-5,-5,-5,5]] 
    
    num = int(plot_range / time_interval)
    tor_data = np.zeros(num)
    ang_data = np.zeros(num)
    can_data = np.zeros(num)
    data = [tor_data,ang_data,can_data]
    
    # Display Status
    disp_MS = ['OFF', 'ON'] # Motor Status
    disp_BLE = ['OFF', 'ON']
    disp_Mode = ['Set Up','Stand by', 'Emergency Stop', 'Return to Zero',\
                        'Pause', 'L2L', 'Const Str', 'Sine Str', 'Not Connected']
    
    # MCU Status
    motor_status = 0
    BLE_status = 0
    MCU_status = 0

    # MCU Reply
    encoder = 0
    torque = 1
    can = 2
    
    # Const Str Status
    const_vel = 0.5
    const_range = [-50,50]
    const_cycle = 1

    # Sine Str Status
    sine_angle = 20
    sine_amp = 30
    sine_freq = 1
    sine_cycle = 1

    # Motor Parameter
    Kt = 0.31 # 0.31 Nm
    enc_counter = 2**14 # Encoder counter 14bit encoder 16384 = 360 degree
    angle = 0
    
                                                                # Activate button When state
    able_list = [["L2L"],                                       # Set Up 
                 ["SineStr_start","ConstStr_start"],            # Stand by
                 [],                                            # Emergency Stop
                 [],                                            # Return to Zero
                 ["ConstStr_pause","SineStr_pause"],            # Pause
                 ["L2L_pause"],                                 # L2L
                 ["ConstStr_pause"],                            # Const Str
                 ["SineStr_pause"]]                             # Sine Str
    
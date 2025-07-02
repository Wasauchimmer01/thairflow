from gpiozero import InputDevice

# GPIO-Pin für den OUT-Pin des RCWL-0516
motion_sensor = InputDevice(6)  # GPIO6 # 31

def monitor_motion():
    if motion_sensor.is_active and not motion:
        motion = True
    elif not motion_sensor.is_active and motion:
        motion = False
    return motion
    

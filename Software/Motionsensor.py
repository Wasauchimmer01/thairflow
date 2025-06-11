from gpiozero import InputDevice
from time import sleep

# GPIO-Pin für den OUT-Pin des RCWL-0516
motion_sensor = InputDevice(31)  # GPIO6

def monitor_motion():
    while True:
        if motion_sensor.is_active and not motion:
            motion = True
        elif not motion_sensor.is_active and motion:
           motion = False
        return motion
    
def send_data():
     if monitor_motion==True:
          motion_sensor.on()
     else:
          motion_sensor.off()  
             
def Start_Motionsensor():
    #print("Starte Bewegungserkennung (RCWL-0516)...")
    #try:
        monitor_motion()
       
    #except KeyboardInterrupt:
        #print("\nBeendet durch Benutzer.")

Start_Motionsensor()
sleep(10)
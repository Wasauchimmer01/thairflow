from gpiozero import InputDevice, Device
from gpiozero.pins.mock import MockFactory, MockPin
from time import sleep
#from signal import pause

Device.pin_factory = MockFactory()
# GPIO-Pin für den OUT-Pin des RCWL-0516
motion_sensor = InputDevice(17)  # GPIO20
pin = motion_sensor.pin
motion_sensor.is_active=True

#def on_motion_detected()
    #print("Bewegung erkannt!")

#def on_no_motion():
    #print("Keine Bewegung mehr.")

# Wiederhole alle 100ms den Status
def monitor_motion():
    was_motion = False
    while True:
        if motion_sensor.is_active and not was_motion:
            #on_motion_detected()
            was_motion = True
            pin.drive_low()
            print(motion_sensor.is_active)
            sleep(10)
        elif not motion_sensor.is_active and was_motion:
            #on_no_motion() 
            was_motion = False
            pin.drive_high()
            print(motion_sensor.is_active)
            sleep(10)


def Start_Motionsensor():
    #print("Starte Bewegungserkennung (RCWL-0516)...")
    #try:
        monitor_motion()
       
    #except KeyboardInterrupt:
        #print("\nBeendet durch Benutzer.")

Start_Motionsensor()
sleep(10)
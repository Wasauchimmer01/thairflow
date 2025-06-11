import Gassensor
import Differenzdruck_610
import Formaldehyd
import Gyroskop_Fenster
import Gyroskop_Tuer
import Motionsensor
import gpiozero
import datetime

def Initialisieren():

    Gassensor.start_measurement()
    Formaldehyd.start_up
    Gyroskop_Fenster.start_up
    Gyroskop_Tuer.start_up

def Messdaten_generieren():

    if Gassensor.check_data==True:
       gas_data = Gassensor.read_measurement    

    differenz_data = Differenzdruck_610.read_measurement

    formaldehyd_data = Formaldehyd.read_measurement

    if Motionsensor.monitor_motion==True:
        motion_data = True
    else: 
        motion_data = False

    gyro_fenster_data = Gyroskop_Fenster.get_sensor_data

    gyro_tuer_data = Gyroskop_Tuer.get_sensor_data

    measurement_Time = datetime.datetime

    data_string = measurement_Time,gas_data,formaldehyd_data,differenz_data,motion_data,gyro_fenster_data,gyro_tuer_data

    return data_string
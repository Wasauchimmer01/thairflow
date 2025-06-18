import Gassensor
import Differenzdruck_610
import Differenzdruck_810
import Formaldehyd
import Gyroskop_Fenster
import Gyroskop_Tuer
import Motionsensor
import gpiozero
import datetime
import Config

def Initialisieren():
    #Nummer bitte nach Reihenfolge vergeben
    Config.add_sensor(Gassensor.start_up(1))
    Config.add_sensor(Formaldehyd.start_up(2))
    Config.add_sensor(Gyroskop_Fenster.start_up(3))
    Config.add_sensor(Gyroskop_Tuer.start_up(4))
    Config.add_sensor(Differenzdruck_610.start_up(5))
    Config.add_sensor(Differenzdruck_810.start_up(6))

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
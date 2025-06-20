import Gassensor
import Differenzdruck_610
import Differenzdruck_810
import Formaldehyd
import Gyroskop_Fenster
import Gyroskop_Tuer
import Motionsensor
import gpiozero
from datetime import datetime
import Config
import csv



sensor_anzahl=7
startline=0
init_completed = 0 #wird 1 wenn das initialisieren abgeschlossen ist
messdaten_counter =0 #wird bei jeder Messung erhöht

def Initialisieren():
    #Nummer nach Reihenfolge vergeben
    Config.add_sensor(Gassensor.start_up(1))
    Config.add_sensor(Formaldehyd.start_up(2))
    Config.add_sensor(Gyroskop_Fenster.start_up(3))
    Config.add_sensor(Gyroskop_Tuer.start_up(4))
    Config.add_sensor(Differenzdruck_610.start_up(5))
    Config.add_sensor(Differenzdruck_810.start_up(6))

    with open('config.csv') as csvdatei:
        csv_reader_object = csv.reader(csvdatei)
        for row in csv_reader_object:
            print(row)
            if row[2]!='0':
                #print("Initialisieren failed")
                return 1
            else:
                #print('Initialisieren complete')
                return 0

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

    measurement_Time = datetime.now().isoformat()

    gasdata= measurement_Time,'Gas','OFF',1,'XXX'
    formdata= measurement_Time,'Form','ON',2,'XVX'

    data=[ gasdata,formdata]
    
    with open('Daten.csv', "r", newline="") as f:
        lines = list(csv.reader(f)) 
    while len(lines) < (startline+messdaten_counter*sensor_anzahl):
        lines.append([])
    for x in data:    
        lines[(startline+messdaten_counter*sensor_anzahl) - 1+x] = data[x]
        with open('Daten.csv', "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(lines)


while True:
    if init_completed!=1:
        if Initialisieren!=0:
            print('Initialisieren fehlgeschlagen')
            break

    allData=Messdaten_generieren 
    messdaten_counter=messdaten_counter+1






import gassensor
import differenzdruck_610
import differenzdruck_810
import formaldehyd
import gyroskop_fenster
import gyroskop_tuer
import motionsensor
import gpiozero
from datetime import datetime
import config
import csv
from time import sleep

sensor_anzahl=7
startline=0
init_completed = 0 #wird 1 wenn das initialisieren abgeschlossen ist
messdaten_counter =0 #wird bei jeder Messung erhöht

def initialisieren():
    #Nummer nach Reihenfolge vergeben
    # config.add_sensor(gassensor.start_up(1))
    # config.add_sensor(formaldehyd.start_up(2))
    # config.add_sensor(gyroskop_fenster.start_up(3))
    # config.add_sensor(gyroskop_tuer.start_up(4))
    config.add_sensor(differenzdruck_610.start_up(1))
    # config.add_sensor(differenzdruck_810.start_up(6))

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

def messdaten_generieren():

    # if gassensor.check_data==True:
    #    gas_data = gassensor.read_measurement    

    differenz_data = differenzdruck_610.read_measurement

    # formaldehyd_data = formaldehyd.read_measurement

    # if motionsensor.monitor_motion==True:
    #     motion_data = True
    # else: 
    #     motion_data = False

    # gyro_fenster_data = gyroskop_Fenster.get_sensor_data

    # gyro_tuer_data = gyroskop_Tuer.get_sensor_data

    # measurement_Time = datetime.now().isoformat()

    # data=[measurement_Time,gas_data,formaldehyd_data,differenz_data,motion_data,gyro_fenster_data,gyro_tuer_data]
    
    xlsx_data(differenz_data)

def xlsx_data(data):
    y=1
    while y <len(data):  
        with open('daten.xlsx', "r", newline="") as f:
                lines = list(csv.reader(f)) 
        # while len(lines) < (y*2):
        #         lines.append([])
        x =0
        while x<len(data):    
            lines.append (data[x])
            with open('daten.xlsx', "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(lines)
            x=x+1
        y=y+len(data)
    sleep(1)



if __name__ == "__main__":
    while True:
        if init_completed!=1:
            if initialisieren!=0:
                print('Initialisieren fehlgeschlagen')
                break
            else:
                init_completed=1        
                print('Initialisieren erfolgreich')

        messdaten_generieren 
        messdaten_counter=messdaten_counter+1
        sleep(10)
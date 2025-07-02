import csv
from datetime import datetime
from time import sleep
#import Archivierung

measurement_Time = datetime.now().isoformat()

gasdata= measurement_Time,'Gas','OFF',0,'XXX'
formdata= measurement_Time,'Form','ON',0,'XVX'
co2data= measurement_Time,'CO2','ON',0,'XZX'
co2data1= measurement_Time,'CO21','ON',0,'XZX'
co2data2= measurement_Time,'CO22','ON',0,'XZX'
co2data3= measurement_Time,'CO23','ON',0,'XZX'

data = [gasdata,formdata,co2data,co2data1,co2data2,co2data3]


def xlsx_data():
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

xlsx_data()

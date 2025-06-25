import csv
from datetime import datetime
from time import sleep
#import Archivierung

measurement_Time = datetime.now().isoformat()

gasdata= measurement_Time,'Gas','OFF',0,'XXX'
formdata= measurement_Time,'Form','ON',0,'XVX'
co2data= measurement_Time,'CO2','ON',0,'XZX'

data=[gasdata,formdata,co2data]
y=1
x=0

def write_data_xlsx(data):
    while y <len(data):  
        with open('Daten.xlsx', "r", newline="") as f:
                lines = list(csv.reader(f)) 
        while len(lines) < (y*2):
                lines.append([])
        x =0
        while x<3:    
            lines[y+x-(len(data)-2)] = data[x]
            with open('Daten.xlsx', "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(lines)
            x=x+1
        y=y+len(data)
    sleep(1)



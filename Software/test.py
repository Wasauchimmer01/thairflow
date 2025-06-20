import csv
from datetime import datetime
from time import sleep

measurement_Time = datetime.now().isoformat()

gasdata= measurement_Time,'Gas','OFF',0,'XXX'
formdata= measurement_Time,'Form','ON',0,'XVX'

data=[ gasdata,formdata]
y=1
while y <1000:  
    with open('Daten.csv', "r", newline="") as f:
            lines = list(csv.reader(f)) 
    while len(lines) < (y*2):
            lines.append([])
    x =0
    while x<2:    
        lines[(y) - 1+x] = data[x]
        with open('Daten.csv', "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(lines)
        x=x+1
    y=y+1

sleep(1)

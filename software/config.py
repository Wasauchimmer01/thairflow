import csv


sensordata = ['Name', 'Status','Error', 'Adresse']
data = []

 
with open('config.csv', 'w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=sensordata)
    writer.writeheader()
    writer.writerows(data)

def add_sensor(name,status,error,adresse,nummer):
    data[nummer]= {'Name': name, 'Status': status,'Error':error, 'Adresse': adresse},

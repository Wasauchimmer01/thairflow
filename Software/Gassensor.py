import smbus2
import time

SEN66_ADDRESS = 0x6B
bus = smbus2.SMBus(1)
command = [0x0021, 0x0202, 0x0300]  #(muss aus Datenblatt entnommen werden) (Starten,Status,Lesen)

def start_measurement():
    bus.write_i2c_block_data(SEN66_ADDRESS, command[0])
    time.sleep(0.1)

def read_measurement():
    try:
        # Lese 27 Bytes (z. B. 2 Byte CO2, 1 CRC, 2 Byte Temp, 1 CRC, 2 Byte RH, 1 CRC)
        data = bus.read_i2c_block_data(SEN66_ADDRESS, command[2], 27)

        def convert(high, low):
            return (high << 8) | low

        pm10_raw = convert(data[0], data[1])
        pm25_raw = convert(data[3], data[4])
        pm40_raw = convert(data[6], data[7])
        pm100_raw= convert(data[9], data[10])
        hum_raw = convert(data[12], data[13])
        temp_raw = convert(data[15], data[16])
        voc_raw = convert(data[18], data[19])
        nox_raw = convert(data[21], data[22])
        co2_raw = convert(data[24], data[25])

        # Werte je nach Datenblatt umrechnen
        pm10 = pm10_raw/10
        pm25 = pm25_raw/10
        pm40 = pm40_raw/10
        pm100 = pm100_raw/10
        humidity = hum_raw/100
        temperature = temp_raw/200
        voc = voc_raw/10
        nox = nox_raw/10
        co2 = co2_raw
        
        return pm1,pm25,pm40,pm100,humidity,temperature,voc,nox,co2
    
    except Exception as e:
        return None, None, None,None,None,None,None,None,None

# Fürs Hauptprogramm

start_measurement() #einmalig um kontinuierliche Messung zu starten

if bus.read_i2c_block_data(SEN66_ADDRESS,command[1])==True:
    pm1,pm2,pm4,pm10,hum,temp,voc,nox,co2 = read_measurement()


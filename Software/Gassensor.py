import smbus2

name = 'Gassensor'
SEN66_ADDRESS = 0x6B
bus = smbus2.SMBus(1)
command = [0x0021, 0x0202, 0x0300]  #(muss aus Datenblatt entnommen werden) (Starten,Status,Lesen)
errorcode=[12,11,9,7,6]  # CO2,PM,CO2,Gas,RH&T

def start_up(nummer):
    bus.write_i2c_block_data(SEN66_ADDRESS, command[0])
    status='ON'
    for x in errorcode:
        if get_bit(bus.read_i2c_block_data(SEN66_ADDRESS),x)==1:
         status='OFF'
         error = x
         break
    return name, status, error, SEN66_ADDRESS, nummer


def check_data():
    if bus.read_i2c_block_data(SEN66_ADDRESS,command[1])==True:
        return True
    else:
        return False

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
        
        return pm10,pm25,pm40,pm100,humidity,temperature,voc,nox,co2
    
    except Exception as e:
        return None, None, None,None,None,None,None,None,None
    
def get_bit(register, bit_number):
  mask = 1 << bit_number  # Erstellt eine Bitmaske für das gewünschte Bit
  return (register & mask) >> bit_number
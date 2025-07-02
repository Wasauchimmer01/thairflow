import time
import smbus2 

name = 'SFA30'
SFA30_ADDRESS = 0x5D
errorcode=[1,2,3,4,32,67,68,127]
bus=smbus2.SMBus(1)

# Befehl zum Starten der Messung
CMD_START_CONTINUOUS_MEASUREMENT = [0x00, 0x10]

# Befehl zum Lesen der Messwerte
CMD_READ_MEASUREMENT = [0x03, 0x00]

def start_up(nummer):
    bus.write_i2c_block_data(SFA30_ADDRESS, CMD_START_CONTINUOUS_MEASUREMENT[0], CMD_START_CONTINUOUS_MEASUREMENT[1])
    if get_bit-(bus.read_i2c_block_data(SFA30_ADDRESS,0xD0),0)==1:
        status='OFF'
        for x in errorcode:
            if get_bit-(bus.read_i2c_block_data(SFA30_ADDRESS,0xD0),errorcode[x])==1:
                error = x
                break
    time.sleep(1)
    return name, status, error, SFA30_ADDRESS, nummer

def measure():

    bus.write_i2c_block_data(SFA30_ADDRESS, CMD_READ_MEASUREMENT[0])

    time.sleep(0.05)

    data = bus.read_i2c_block_data(SFA30_ADDRESS, CMD_READ_MEASUREMENT, 9)


    def convert(high, low):
        return (high << 8) | low

    hcho_raw = convert(data[0],data[1])
    temp_raw = convert(data[3],data[4])
    hum_raw  = convert(data[6],data[7])

    hcho = hcho_raw / 5.0      # ppb
    temp = temp_raw / 200.0    # °C
    hum  = hum_raw / 100.0     # % rel. Feuchte

    return hcho, temp, hum

def read_measurement():
        hcho, temp, hum = measure()
        return hcho, temp, hum 

def get_bit(register, bit_number):
  mask = 1 << bit_number  # Erstellt eine Bitmaske für das gewünschte Bit
  return (register & mask) >> bit_number
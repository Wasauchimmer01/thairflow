import smbus2

name = 'Gassensor'
SEN66_ADDRESS = 0x6B
bus = smbus2.SMBus(1)
command = [0x0021, 0x0202, 0x0300]  #(Starten,Status,Lesen)
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

########################################################################

import time
from sensirion_i2c_driver import LinuxI2cTransceiver, I2cConnection, CrcCalculator
from sensirion_driver_adapters.i2c_adapter.i2c_channel import I2cChannel
from sensirion_i2c_sen66.device import Sen66Device
from software.utils import get_args

# !!!Check what PM1p0 means, check units

class Sen66Sensor:
    def __init__(self, address):
        self.name = 'Sen66'
        self.values = ["PM1p0", "PM2p5", "PM4p0", "PM10p0", "Rh", "temp", "voc", "nox", "co2"]
        self.units = ["mass concentration ppm", "mass concentration ppm", "mass concentration ppm", "mass concentration ppm", "%", "C", "0-500", "0-100", "ppm"]
        self.address = address
        self.args = get_args()
        self.i2c_port = self.args.i2c_port
        self.sensor, self.i2ctransceiver = self.init_sensor(self.i2c_port)

    def init_sensor(self, i2c_port):
        """Initialisiert den Sensor und gibt das Sensorobjekt zurück."""
        i2c_transceiver = LinuxI2cTransceiver(i2c_port)
        channel = I2cChannel(
            I2cConnection(i2c_transceiver),
            slave_address=0x6B,
            crc=CrcCalculator(8, 0x31, 0xff, 0x0)
        )
        sensor = Sen66Device(channel)
        sensor.device_reset()
        time.sleep(1.2)
        serial_number = sensor.get_serial_number()
        print(f"Serial Number: {serial_number}")
        sensor.start_continuous_measurement()
        return sensor, i2c_transceiver

    def read_measurements(self):
        """Liest Messwerte in einem Intervall aus."""
        try:
            # (
            #     mass_concentration_pm1p0,
            #     mass_concentration_pm2p5,
            #     mass_concentration_pm4p0,
            #     mass_concentration_pm10p0,
            #     humidity,
            #     temperature,
            #     voc_index,
            #     nox_index,
            #     co2
            # ) = sensor.read_measured_values()
            # print(f"PM1.0: {mass_concentration_pm1p0}, "
            #         f"PM2.5: {mass_concentration_pm2p5}, "
            #         f"PM4.0: {mass_concentration_pm4p0}, "
            #         f"PM10.0: {mass_concentration_pm10p0}, "
            #         f"Humidity: {humidity}, "
            #         f"Temperature: {temperature}, "
            #         f"VOC Index: {voc_index}, "
            #         f"NOx Index: {nox_index}, "
            #         f"CO2: {co2}")
            data = self.sensor.read_measured_values()
            data = (str(d) for d in data)
            data = (float(d) for d in data)
            return data
        except Exception as e:
            print(f"Error during measurement: {e}")

    def stop_sensor(self):
        """Stoppt die Messung und schließt die Verbindung."""
        self.sensor.stop_measurement()
        self.i2ctransceiver.close()
        print("Measurement stopped and connection closed.")

    def data_printout(self, data):
        """Gibt die Messdaten in einem lesbaren Format aus."""
        if data is None:
            print("No data available.")
            return
        pm10, pm25, pm40, pm100, humidity, temperature, voc, nox, co2 = data
        print(f"PM10: {pm10}, PM2.5: {pm25}, PM4.0: {pm40}, PM100: {pm100}, "
            f"Humidity: {humidity}, Temperature: {temperature}, "
            f"VOC Index: {voc}, NOx Index: {nox}, CO2: {co2}")

def test_run(adress=0x6B):

    sensor = Sen66Sensor(adress)
    i = 0
    while True:
        try:
            data = sensor.read_measurements()
            i += 1
            print(f"Measurement {i}")
            sensor.data_printout(data)
            time.sleep(1)
        except KeyboardInterrupt:
            print("Measurement stopped by user.")
            break
    sensor.stop_sensor()
    print("Measurement stopped.")

if __name__ == "__main__":
    
    test_run(adress=0x6B)
    pass
import time
import smbus2
from sensirion_i2c_driver import LinuxI2cTransceiver, I2cConnection, CrcCalculator
from sensirion_driver_adapters.i2c_adapter.i2c_channel import I2cChannel
from sensirion_i2c_sfa3x.device import Sfa3xDevice
from software.utils import get_args

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

####################################################################
class SFA30Sensor:
    def __init__(self, address):
        self.name = 'SFA30'
        self.values = ["Hcho", "Rm", "Temp"]
        self.units = ["ppb", "%", "C"]
        self.address = address
        self.args = get_args()
        self.i2c_port = self.args.i2c_port
        self.sensor, self.i2ctransceiver = self.init_sensor(self.i2c_port, address)

    def init_sensor(self, i2c_port, slave_address=0x5D):
        """Initialisiert den Sensor und gibt das Sensorobjekt zurück."""
        i2c_transceiver = LinuxI2cTransceiver(self.i2c_port)
        channel = I2cChannel(
            I2cConnection(i2c_transceiver),
            slave_address=self.address,
            crc=CrcCalculator(8, 0x31, 0xff, 0x0)
        )
        sensor = Sfa3xDevice(channel)
        sensor.device_reset()
        time.sleep(1.2)
        device_marking = sensor.get_device_marking()
        print(f"device_marking: {device_marking};")
        sensor.start_continuous_measurement()
        return sensor, i2c_transceiver

    def read_measurements(self):
        try:
            (hcho, humidity, temperature) = self.sensor.read_measured_values()
            hcho = str(hcho)
            humidity = str(humidity)
            temperature = str(temperature)
            hcho = float(hcho)
            humidity = float(humidity)
            temperature = float(temperature)
            return hcho, humidity, temperature
        except Exception as e:
            print(f"Error reading measurement: {e}")
            self.read_measurements(sensor)
            # not a fan. change error handling


    def data_printout(self, data, show_temp=False, show_humidity=False):
        """Gibt die Messdaten aus."""
        hcoh, rh, temperature = data
        string = str(f"HCOH: {hcoh} ppb?")
        # einheit herrausfinden ppb ist nicht sicher
        if show_temp:
            string += str(f"Temperature: {temperature} °C")
        if show_humidity:
            string += str(f"Humidity: {rh} %")
        print(string)

    def stop_sensor(self):
        """Stoppt die Messung und schließt die Verbindung."""
        self.sensor.stop_measurement()
        self.i2ctransceiver.close()
        #print("Measurement stopped and connection closed.")

    def test_run(self, slave_address=0x5D):
        args = get_args()
        sensor, i2c_transceiver = self.init_sensor(args.i2c_port, slave_address=0x5D)
        i= 0
        while True:
            try:
                data = self.read_measurements(sensor)
                i += 1
                print(f"Measurement {i}")
                self.data_printout(data, show_temp = False, show_humidity=False)
                time.sleep(1)
            except KeyboardInterrupt:
                print("Measurement stopped by user.")
                break
        self.stop_sensor(sensor, i2c_transceiver)
        print("Measurement stopped.")

if __name__ == "__main__":
    import argparse
    import time
    from sensirion_i2c_driver import LinuxI2cTransceiver, I2cConnection, CrcCalculator
    from sensirion_driver_adapters.i2c_adapter.i2c_channel import I2cChannel
    from sensirion_i2c_sfa3x.device import Sfa3xDevice

    from software.utils import get_args
    sensor = SFA30Sensor(address=0x5D)

    sensor.test_run(slave_address=0x5D)


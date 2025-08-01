import time
from sensirion_i2c_driver import LinuxI2cTransceiver, I2cConnection, CrcCalculator
from sensirion_driver_adapters.i2c_adapter.i2c_channel import I2cChannel
from sensirion_i2c_sen66.device import Sen66Device
from software.utils import get_args

class Sen66Sensor:
    def __init__(self, address):
        self.name = 'Sen66'
        self.values = ["PM1p0", "PM2p5", "PM4p0", "PM10p0", "Rh", "Temp", "VOC", "NOx", "CO2", "ErrorCount"]
        self.units = ["mass concentration ppm", "mass concentration ppm", "mass concentration ppm", "mass concentration ppm", "%", "C", "0-500", "0-500", "ppm", "0-50"]
        self.address = address
        self.args = get_args()
        self.i2c_port = self.args.i2c_port
        self.sensor, self.i2ctransceiver = self.init_sensor(self.i2c_port)
        self._error_count = 0

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
        time.sleep(1)
        # serial_number = sensor.get_serial_number()
        sensor.start_continuous_measurement()
        return sensor, i2c_transceiver
    
    def reset_measurement(self):
        print(f"Sensor {self.name}, address {self.address} restarted due to high error count")
        # self.stop_sensor() #maybe needed. needs testing
        self.sensor, self.i2ctransceiver = self.init_sensor(self.i2c_port)
        self._error_count = 0

    def read_measurements(self):
        """Liest Messwerte in einem Intervall aus."""
        try:
            data = self.sensor.read_measured_values()
            data = [float(str(d)) for d in data]
            data.append(self._error_count) 
            # data = (str(d) for d in data)
            # data = (float(d) for d in data)
            self._error_count = 0
            # data += self._error_count
            return data
        except Exception as e:
            print(f"Error during measurement: {e}")
            self._error_count += 1
            if self._error_count > 50:
                self.reset_measurement()
            return (None,None,None,None,None,None,None,None,None, self._error_count)

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
        pm10, pm25, pm40, pm100, humidity, temperature, voc, nox, co2, ec = data
        print(f"PM10: {pm10}, PM2.5: {pm25}, PM4.0: {pm40}, PM100: {pm100}, "
            f"Humidity: {humidity}, Temperature: {temperature}, "
            f"VOC Index: {voc}, NOx Index: {nox}, CO2: {co2}, ErrorCount: {ec}")

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
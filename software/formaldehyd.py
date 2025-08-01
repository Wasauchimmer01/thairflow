import time
import smbus2
from sensirion_i2c_driver import LinuxI2cTransceiver, I2cConnection, CrcCalculator
from sensirion_driver_adapters.i2c_adapter.i2c_channel import I2cChannel
from sensirion_i2c_sfa3x.device import Sfa3xDevice
from software.utils import get_args


class SFA30Sensor:
    def __init__(self, address):
        self.name = 'SFA30'
        self.values = ["Hcho", "Rh", "Temp", "ErrorCount"]
        self.units = ["ppb", "%", "C", "0-50"]
        self.address = address
        self.args = get_args()
        self.i2c_port = self.args.i2c_port
        self.sensor, self.i2ctransceiver = self.init_sensor(self.i2c_port, address)
        self._error_count = 0

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
        time.sleep(1)
        device_marking = sensor.get_device_marking()
        print(f"device_marking: {device_marking};")
        sensor.start_continuous_measurement()
        return sensor, i2c_transceiver
    
    def restart_measurement(self):
        print(f"Sensor {self.name}, address {self.address} restarted due to high error count")
        # self.stop_sensor() # test if needed
        self.sensor, self.i2ctransceiver = self.init_sensor(self.i2c_port, self.address)
        self._error_count = 0

    def read_measurements(self):
        try:
            (hcho, humidity, temperature) = self.sensor.read_measured_values()
            hcho = str(hcho)
            humidity = str(humidity)
            temperature = str(temperature)
            hcho = float(hcho)
            humidity = float(humidity)
            temperature = float(temperature)
            self._error_count = 0
            return hcho, humidity, temperature, self._error_count
        except Exception as e:
            print(f"Error reading measurement: {e}")
            self._error_count += 1
            if self._error_count > 50:
                self.restart_measurement()
            return None, None, None, self._error_count


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


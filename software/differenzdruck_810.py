import time
from sensirion_i2c_driver.linux_i2c_transceiver import LinuxI2cTransceiver
from sensirion_i2c_driver import I2cConnection
from sensirion_i2c_sdp import SdpI2cDevice
from sensirion_driver_adapters.i2c_adapter.i2c_channel import I2cChannel
from software.utils import get_args, error_handler
import statistics
import threading

class SdpSensor:
    def __init__(self, address):
        self.name = 'Differenzdrucksensor'
        self.values = ["DifferentialPressure", "Temp", "ErrorCount"]
        self.units = ["Pa", "C", "0-50"]
        self.address = address
        self.args = get_args()
        self.i2c_port = self.args.i2c_port
        self.sensor, self.i2ctransceiver = self.init_sensor(self.i2c_port, address)
        
        self._dp_value_log = []
        self._temp_log = []
        self._error_count = 0
        self._running = True
        self._thread = threading.Thread(target=self.conti_measure, daemon=True)
        self._thread.start()


    def restart_messurement(self):
        print(f"Sensor {self.name}, address {self.address} restarted due to high error count")
        self.stop_sensor()
        self.sensor, self.i2ctransceiver = self.init_sensor(self.i2c_port, self.address)
        self._dp_value_log = []
        self._temp_log = []
        self._error_count = 0
        self._running = True
        self._thread = threading.Thread(target=self.conti_measure, daemon=True)
        self._thread.start()

    def conti_measure(self):
        while self._running:
            try:
                differential_pressure, temperature = self.sensor.read_measurement()
                self._dp_value_log.append(differential_pressure.pascal)
                self._temp_log.append(temperature.degrees_celsius)
            except Exception as e:
                pass
    
    def read_measurements(self):
        if self._dp_value_log:
            mean_dp = statistics.mean(self._dp_value_log)
            mean_t = statistics.mean(self._temp_log)
            self._dp_value_log = []
            self._temp_log = []
            self._error_count = 0
        else:
            mean_dp, mean_t = None, None
            self._error_count += 1
        if self._error_count > 50:
            self.restart_messurement()
        return mean_dp, mean_t, self._error_count

    def init_sensor(self, i2c_port, slave_address=0x25):
        """Initialisiert den Sensor und gibt das Sensorobjekt zurück."""
        i2c_transceiver = LinuxI2cTransceiver(i2c_port)
        sensor = SdpI2cDevice(I2cConnection(i2c_transceiver), slave_address=slave_address)
        sensor.stop_continuous_measurement()
        sensor.start_continuous_measurement_with_mass_flow_t_comp()
        return sensor, i2c_transceiver


    def stop_sensor(self):
        """Stoppt die Messung und schließt die Verbindung."""
        self._running = False
        self.sensor.stop_continuous_measurement()
        self.i2ctransceiver.close()


    def data_printout(self, data, show_temp=True):
        """Gibt die Messdaten aus."""
        differential_pressure, temperature = data
        string = str(f"Differential Pressure: {differential_pressure} Pa")
        if show_temp:
            string += str(f" Temperature: {temperature} °C")
        print(string)



    def rolling_mean(self, sensor, window_size, store):
        data = self.read_measurements(sensor)
        store.append(data)
        if len(store) > window_size:
            store.pop(0)
        avg_pressure = sum([d[0].pascal for d in store]) / len(store)
        return avg_pressure


    def rolling_median(self, sensor, window_size, store):
        data = self.read_measurements(sensor)
        store.append(data)
        if len(store) > window_size:
            store.pop(0)
        avg_pressure = statistics.median([d[0].pascal for d in store])
        return avg_pressure
        


    def test_run(self, slave_address=0x25):
        global ERROR_COUNT
        args = get_args()
        sensor, i2c_transceiver = self.init_sensor(args.i2c_port, slave_address=slave_address)
        i= 0
        data_save = []
        store = []
        while True:
            try:
                for _ in range(10):
                    data, _ = error_handler(sensor.read_measurement, [], sensor.start_continuous_measurement_with_mass_flow_t_comp, error_retries=60, error_delay=0.5)
                    store.append(data)
                    time.sleep(1)
                    i += 1
                print(f"Measurement {i}")
                avg_pressure = sum([d.pascal for d in store]) / len(store)
                print(f"Average Differential Pressure: {avg_pressure} Pa")
                
                #######
                # avg = rolling_median(sensor, window_size=100, store=store)
                # print(f"Measurement {i}")
                # print(f"Average Differential Pressure: {avg} Pa")
                # i += 1
                # time.sleep(0.1)
                # data_save.append(avg)
                
            except KeyboardInterrupt:
                print("Measurement stopped by user.")
                break
    
        self.stop_sensor(sensor, i2c_transceiver)
        print("Measurement stopped.")

    # data_save = data_save[1000:]

    # import matplotlib.pyplot as plt

    # plt.figure(figsize=(10, 5))
    # plt.plot(data_save, label='Average Differential Pressure (Pa)')
    # plt.xlabel('Measurement Number')
    # plt.ylabel('Differential Pressure (Pa)')
    # plt.title('Differential Pressure Over Time')
    # plt.legend()
    # plt.grid(True)
    # plt.show()
    # plt.savefig("differential_pressure_median_100window.png")

if __name__ == "__main__":
    sdp = SdpSensor(0x25)
    sdp.test_run()

    # since the sensor is very fast, we can use a rolling window smoothing to at least whatever global time interval we want
    # or like adapt it to the ramp up and down of the fan

    # mean or median does not seem to matter (at least not for a 1000 sample window)

    # 0.3Pa ~ 50m^3/h
    # 1Pa ~ 100m^3/h
    # 3.5Pa ~ 200m^3/h
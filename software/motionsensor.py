import time
import smbus2
from ads1015 import ADS1015
from software.utils import get_args
import threading
import statistics

class MotionSensor:
    def __init__(self, address, test = False):
        self.name = 'Motionsensor/Reedsensor'
        self.values = ["Motion", "DoorOpen"]
        self.units = ["Bool", "Bool"]
        self.address = address
        self.args = get_args()
        self.i2c_port = self.args.i2c_port
        self._ref_v = None
        self.ads1015 = self.setup_sensor(self.i2c_port, self.address)
        self.channels = ["in0/ref", "in1/ref"]  # Define the channels you want to use

        self._v_occ_log = []
        self._v_open_log = []
        self._running = True
        if test:
            self._running = False
        self._thread = threading.Thread(target=self.conti_measure, daemon=True)
        self._thread.start()

    
    def setup_sensor(self, i2c_port=1, slave_address=0x48):
        """Initializes the ADS1015 sensor and returns the sensor object."""
        bus = smbus2.SMBus(i2c_port)

        max_errors = 50
        error_count = 0

        ads1015 = ADS1015(slave_address)
        try:
            ads1015.set_mode("single")
        except Exception as e:
            error_count += 1
            if error_count > max_errors:
                raise f"Sensor couldnt be setup after {max_errors} retries"
        try:
            ads1015.set_programmable_gain(6.144)
        except Exception as e:
            error_count += 1
            if error_count > max_errors:
                raise f"Sensor couldnt be setup after {max_errors} retries"
        try:
            ads1015.set_sample_rate(1600)
        except Exception as e:
            error_count += 1
            if error_count > max_errors:
                raise f"Sensor couldnt be setup after {max_errors} retries"
        try:
            self._ref_v = ads1015.get_reference_voltage()
        except Exception as e:
            error_count += 1
            if error_count > max_errors:
                raise f"Sensor couldnt be setup after {max_errors} retries"
            
        print(self._ref_v)

        return ads1015
        
    
    def conti_measure(self):
        while self._running:
            for channel in self.channels:
                try:
                    voltage = self.ads1015.get_voltage(channel=channel)
                except Exception as e:
                    continue
                if channel == "in0/ref":
                    self._v_occ_log.append(voltage)
                if channel == "in1/ref":
                    self._v_open_log.append(voltage)
            time.sleep(0.1)



    def read_measurements(self):
        """Reads voltage values from the specified channels."""
        motion = None
        open = None

        if statistics.mean(self._v_occ_log)>2.3:
            motion = True
        elif statistics.mean(self._v_occ_log)<2:
            motion = False
        else:
            motion = False
            print("FOOOOOOOOOOOOOOOOOOOOOOOO")
        # if any(v > 2.5 for v in self._v_occ_log):
        #     motion = True
        # else:
        #     motion = False
        
        # if any(v < 0.1 for v in self._v_open_log):
        #     open = True
        # else:
        #     open = False

        if statistics.mean(self._v_open_log)>2.3:
            open = True
        elif statistics.mean(self._v_open_log)<2:
            open = False
        else:
            open = False
            print("FUUUUUUUUUUUUUUUUUUUUUU")



        self._v_occ_log = []
        self._v_open_log = []

        return motion, open


    def data_printout(self, data):
        """Prints the sensor data."""
        motion, open = data
        print(f"Motion:{motion}, Door Open: {open}")

    def test_output_status(self, values, interval=0.5, obs_time=120, on_off=False, obs_values=[], txt_output=False):
        """Outputs the status of the sensor readings at specified intervals."""
        num_samples = int(obs_time / interval)

        for _ in range(num_samples):
            time.sleep(interval)
            voltage = values["in0/ref"]["voltage"]
            obs_values.append(voltage)

            if len(obs_values) > num_samples:
                obs_values.pop(0)

            if any(v > 2 for v in obs_values):
                if not on_off:
                    on_off = True
                    print("Motion detected!")
                    if txt_output:
                        with open("output.txt", "a") as f:
                            f.write(f"Motion detected at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            else:
                if on_off:
                    on_off = False
                    print("No motion detected.")
                    if txt_output:
                        with open("output.txt", "a") as f:
                            f.write(f"No motion detected at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        return on_off, obs_values


    def stop_sensor(self):
        self._running = False
        self._thread.join()

    def test_run(self, slave_adress):
        sensor = self.setup_sensor(i2c_port=1, slave_address=slave_adress)
        channels = ["in0/ref"]#, "in1/ref", "in2/ref"]

        print(f"Sensor initialized at address {slave_adress}.")
        while True:
            for channel in channels:
                values = self.ads1015.get_voltage(channel)
                on_off, obs_values = self.test_output_status(values, interval=0.5, obs_time=120, on_off=False, obs_values=[], txt_output=True)


if __name__ == "__main__":

    # ms = MotionSensor(0x48)  # Replace with the actual I2C address of your sensor
    # ms.test_run(slave_adress=0x48)
    address = [72]
    sensors = []
    for a in address:
        sensor = MotionSensor(a, test = False)
        sensors.append(sensor)
        #time.sleep(2)
    
    while True:
        try:
            for sensor in sensors:
                try:
                    value1 = sensor.ads1015.get_voltage("in0/ref")
                    value2 = sensor.ads1015.get_voltage("in1/ref")
                    data = sensor.read_measurements()
                    time.sleep(1)
                    print(value1, value2, sensor.address)
                    print(data, sensor.address)
                except Exception as e:
                    print(f"Error reading sensor: {e}")
                    time.sleep(1)
        except KeyboardInterrupt:
            print("Measurement stopped by user.")
            break

    for sensor in sensors:
        sensor.stop_sensor()
        print(f"{sensor.name} stopped.")

    # put vdd pin into addr pin for adress 0x49

    # could ether save data as is (observation window like 1sec) and calculate afterwards
    # or calculate based on observation time (like was there movement in the last 120 seconds)
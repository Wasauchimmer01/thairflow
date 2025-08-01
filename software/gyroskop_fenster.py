import smbus2
from mpu6050 import mpu6050
import math
import statistics
import time
import threading


class GyroSensor:
    def __init__(self, address):
        self.name = 'Gyroskop'
        self.values = ["TiltAngle", "OpenAngle", "ErrorCount"]
        self.units = ["angle degree", "angle degree","0-50"]
        self.address = address
        self.sensor = mpu6050(address)
        self.last_time = time.time()
        self.x_ref, self.y_ref, self.z_ref, self.a_off, self.b_off, self.c_off = self.calibrate_gyro()
        self.open_angle = 0.0
        self.a_angle, self.b_angle, self.c_angle = 0.0, 0.0, 0.0
        self.v_ref = [self.x_ref, self.y_ref, self.z_ref]

        self._acc_log = []
        self._open_angle_log = []
        self._error_count = 0
        self._running = True
        self._thread = threading.Thread(target=self.conti_measure, daemon=True)
        self._thread.start()


    def restart_messurement(self):
        print(f"Sensor {self.name}, address {self.address} restarted due to high error count")
        self.stop_sensor()
        self._error_count = 0
        self._running = True
        self._thread = threading.Thread(target=self.conti_measure, daemon=True)
        self._thread.start()
        self.last_time = time.time()
        self._v_occ_log = []
        self._v_open_log = []
    
    def conti_measure(self):
        while self._running:
            try:
                acc = self.sensor.get_accel_data()
                self._acc_log.append(acc)
                gyro = self.sensor.get_gyro_data()
                self.get_open_angle(gyro['y'])
            except Exception as e:
                pass


    def get_tilt_angle(self, x, y, z):
        # Normalize both vectors
        def normalize(v):
            mag = math.sqrt(sum(i**2 for i in v))
            return [i / mag for i in v]

        ref = normalize(self.v_ref)
        curr = normalize([x, y, z])

        # Compute dot product
        dot = sum(r * c for r, c in zip(ref, curr))
        dot = max(min(dot, 1.0), -1.0)  # Clamp to avoid domain errors

        # Angle between vectors (in radians)
        angle_rad = math.acos(dot)

        # Convert to degrees
        angle_deg = math.degrees(angle_rad)

        # highpassfiler
        if abs(angle_deg) < 0.5:
            angle_deg = 0
        return angle_deg


    def read_measurements(self):
        if self._acc_log:
            acc_x_list = (v['x'] for v in self._acc_log)
            acc_y_list = (v['y'] for v in self._acc_log)
            acc_z_list = (v['z'] for v in self._acc_log)
            acc_x = statistics.mean(acc_x_list)
            acc_y = statistics.mean(acc_y_list)
            acc_z = statistics.mean(acc_z_list)
            tilt = self.get_tilt_angle(acc_x, acc_y, acc_z)
            self._error_count = 0
        else:
            tilt = None
            self._error_count += 1
        if self._open_angle_log:
            open_angle = statistics.mean(self._open_angle_log)
            self._error_count = 0
        else:
            open_angle = None
            self._error_count += 1

        self._acc_log = []
        self._open_angle_log = []

        if self._error_count > 50:
            self.restart_messurement()

        return tilt, open_angle, self._error_count

    def data_printout(self, data):
        """Prints the sensor data."""
        tilt, open_angle = data
        if not tilt or not open_angle:
            pass
        else:
            print(f"Tilt Angle: {tilt:.2f}° Open Angle: {open_angle:.2f}°")

    def test_messure(self, sensor):
        try:
            accelerometer_data = sensor.get_accel_data()
            temp = sensor.get_temp()
            gyro_data = sensor.get_gyro_data()
        except Exception as e:
            # print(f"Error reading gyro sensor data: {e}")
            # redo = test_messure()
            return None, None, None

        return accelerometer_data, gyro_data, temp


    def calibrate_gyro(self, num_samples=5000):
        print("Calibrating gyroscope...this takes like 2 minutes")
        gyro_x_sum = []
        gyro_y_sum = []
        gyro_z_sum = []
        acc_x_sum = []
        acc_y_sum = []
        acc_z_sum = []

        for _ in range(num_samples):
            gyro = self.sensor.get_gyro_data()
            acc = self.sensor.get_accel_data()
            gyro_x_sum.append(gyro['x'])
            gyro_y_sum.append(gyro['y'])
            gyro_z_sum.append(gyro['z'])
            acc_x_sum.append(acc['x'])
            acc_y_sum.append(acc['y'])
            acc_z_sum.append(acc['z'])
        acc_x = statistics.mean(acc_x_sum)
        acc_y = statistics.mean(acc_y_sum)
        acc_z = statistics.mean(acc_z_sum)
        gyro_x = statistics.mean(gyro_x_sum)
        gyro_y = statistics.mean(gyro_y_sum)
        gyro_z = statistics.mean(gyro_z_sum)

        # reset
        self.open_angle = 0.0
        self.last_time = time.time()

        return acc_x, acc_y,acc_z,gyro_x, gyro_y, gyro_z


    def get_open_angle(self, anglespeed):
        delta_t = time.time() - self.last_time

        # Calculate the change in angle (in degrees) using the gyroscope's Z axis (c)
        # Gyroscope values are in degrees per second, so multiply by delta_t to get degrees
        delta_angle = (anglespeed- self.b_off) * delta_t
        if abs(delta_angle) < 0.7:
            delta_angle = 0.0  # Highpassfilter
        self.open_angle += delta_angle
        self.last_time = time.time()

        self._open_angle_log.append(self.open_angle)

    def stop_sensor(self):
        """Stops the sensor and closes the connection."""
        self._running = False
        self._thread.join()


if __name__ == "__main__":
    gyro = GyroSensor(0x68)

    while True:
        data = gyro.read_measurements()
        gyro.data_printout(data)
        time.sleep(1)
    



    # put vdd pin into AD0 pin for address 0x69


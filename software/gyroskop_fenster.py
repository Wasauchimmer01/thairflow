import smbus2
from mpu6050 import mpu6050
import math
import statistics
import time
import threading

# name = 'Gyro-Fenster'
# MPU6050_ADDR = 0x68
# bus=smbus2.SMBus(1)

# # Register-Adressen
# PWR_MGMT_1   = 0x6B
# ACCEL_XOUT_H = 0x3B
# GYRO_XOUT_H  = 0x43
# TEMP_OUT_H   = 0x41

# def start_up(nummer):
#         # Sensor aktivieren
#         bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0) 
#         status='OFF'
#         error=1
#         who_am_i = bus.read_byte_data(MPU6050_ADDR, 0x75)
#         if who_am_i == MPU6050_ADDR:
#              status ='ON'
#              error=0
#         return name,status,error,MPU6050_ADDR,nummer

# def read_word(bus, addr, reg):
#     high = bus.read_byte_data(addr, reg)
#     low = bus.read_byte_data(addr, reg + 1)
#     value = (high << 8) + low
#     if value >= 0x8000:
#         value = -((65535 - value) + 1)
#     return value

# def get_sensor_data():
#     accel_x = read_word(bus, MPU6050_ADDR, ACCEL_XOUT_H)/ 16384.0
#     accel_y = read_word(bus, MPU6050_ADDR, ACCEL_XOUT_H + 2)/ 16384.0
#     accel_z = read_word(bus, MPU6050_ADDR, ACCEL_XOUT_H + 4)/ 16384.0
    
#     temp_raw = read_word(bus, MPU6050_ADDR, TEMP_OUT_H)
#     temperature = temp_raw / 340.0 + 36.53
    
#     gyro_x = read_word(bus, MPU6050_ADDR, GYRO_XOUT_H)/ 131.0
#     gyro_y = read_word(bus, MPU6050_ADDR, GYRO_XOUT_H + 2)/ 131.0
#     gyro_z = read_word(bus, MPU6050_ADDR, GYRO_XOUT_H + 4)/ 131.0
    
#     return accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,temperature

class GyroSensor:
    def __init__(self, address):
        self.name = 'Gyroskop'
        self.values = ["TiltAngle", "OpenAngle"]
        self.units = ["angle degree", "angle degree"]
        self.address = address
        self.sensor = mpu6050(address)
        #self.sensor.set_accel_range(mpu6050.ACCEL_RANGE_2G)
        #self.sensor.set_gyro_range(mpu6050.GYRO_RANGE_250DEG)
        self.last_time = time.time()
        self.x_ref, self.y_ref, self.z_ref, self.a_off, self.b_off, self.c_off = self.calibrate_gyro()
        self.open_angle = 0.0
        self.a_angle, self.b_angle, self.c_angle = 0.0, 0.0, 0.0
        #self.a_time, self.b_time, self.c_time = last_time, last_time, last_time
        self.v_ref = [self.x_ref, self.y_ref, self.z_ref]

        self._acc_log = []
        self._open_angle_log = []
        self._running = True
        self._thread = threading.Thread(target=self.conti_measure, daemon=True)
        self._thread.start()

    
    def conti_measure(self):
        while self._running:
            acc = self.sensor.get_accel_data()
            self._acc_log.append(acc)
            gyro = self.sensor.get_gyro_data()
            self.get_open_angle(gyro['y'])


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
        else:
            tilt = None
        if self._open_angle_log:
            open_angle = statistics.mean(self._open_angle_log)
        else:
            open_angle = None

        self._acc_log = []
        self._open_angle_log = []

        return tilt, open_angle, 

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
        if abs(delta_angle) < 0.35:
            delta_angle = 0.0  # Highpassfilter
        self.open_angle += delta_angle
        self.last_time = time.time()

        self._open_angle_log.append(self.open_angle)

    def stop_sensor(self):
        """Stops the sensor and closes the connection."""
        self._running = False
        pass


if __name__ == "__main__":
    gyro = GyroSensor(0x68)

    while True:
        data = gyro.read_measurements()
        gyro.data_printout(data)
        time.sleep(1)
    



    # put vdd pin into AD0 pin for address 0x69


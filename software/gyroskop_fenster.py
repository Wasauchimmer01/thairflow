import smbus2
from mpu6050 import mpu6050
import math
import statistics
import time

name = 'Gyro-Fenster'
MPU6050_ADDR = 0x68
bus=smbus2.SMBus(1)

# Register-Adressen
PWR_MGMT_1   = 0x6B
ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H  = 0x43
TEMP_OUT_H   = 0x41

def start_up(nummer):
        # Sensor aktivieren
        bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0) 
        status='OFF'
        error=1
        who_am_i = bus.read_byte_data(MPU6050_ADDR, 0x75)
        if who_am_i == MPU6050_ADDR:
             status ='ON'
             error=0
        return name,status,error,MPU6050_ADDR,nummer

def read_word(bus, addr, reg):
    high = bus.read_byte_data(addr, reg)
    low = bus.read_byte_data(addr, reg + 1)
    value = (high << 8) + low
    if value >= 0x8000:
        value = -((65535 - value) + 1)
    return value

def get_sensor_data():
    accel_x = read_word(bus, MPU6050_ADDR, ACCEL_XOUT_H)/ 16384.0
    accel_y = read_word(bus, MPU6050_ADDR, ACCEL_XOUT_H + 2)/ 16384.0
    accel_z = read_word(bus, MPU6050_ADDR, ACCEL_XOUT_H + 4)/ 16384.0
    
    temp_raw = read_word(bus, MPU6050_ADDR, TEMP_OUT_H)
    temperature = temp_raw / 340.0 + 36.53
    
    gyro_x = read_word(bus, MPU6050_ADDR, GYRO_XOUT_H)/ 131.0
    gyro_y = read_word(bus, MPU6050_ADDR, GYRO_XOUT_H + 2)/ 131.0
    gyro_z = read_word(bus, MPU6050_ADDR, GYRO_XOUT_H + 4)/ 131.0
    
    return accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,temperature


def get_tilt_angle(x_ref, y_ref, z_ref, x, y, z):
    # Normalize both vectors
    def normalize(v):
        mag = math.sqrt(sum(i**2 for i in v))
        return [i / mag for i in v]

    ref = normalize([x_ref, y_ref, z_ref])
    curr = normalize([x, y, z])

    # Compute dot product
    dot = sum(r * c for r, c in zip(ref, curr))
    dot = max(min(dot, 1.0), -1.0)  # Clamp to avoid domain errors

    # Angle between vectors (in radians)
    angle_rad = math.acos(dot)

    # Convert to degrees
    angle_deg = math.degrees(angle_rad)
    return angle_deg


def test_messure():
    try:
        sensor = mpu6050(0x68)
        accelerometer_data = sensor.get_accel_data()
        temp = sensor.get_temp()
        gyro_data = sensor.get_gyro_data()
    except Exception as e:
        print(f"Error reading gyro sensor data: {e}")
        redo = test_messure()
        return redo
    return accelerometer_data, gyro_data, temp


def calibrate_gyro(sensor, num_samples=10000):
    print("Calibrating gyroscope...this takes like 2 minutes")
    gyro_x_sum = []
    gyro_y_sum = []
    gyro_z_sum = []
    acc_x_sum = []
    acc_y_sum = []
    acc_z_sum = []

    for _ in range(num_samples):
        gyro = sensor.get_gyro_data()
        acc = sensor.get_accel_data()
        gyro_x_sum.append(gyro['x'])
        gyro_y_sum.append(gyro['y'])
        gyro_z_sum.append(gyro['z'])
        acc_x_sum.append(acc['x'])
        acc_y_sum.append(acc['y'])
        acc_z_sum.append(acc['z'])
        # time.sleep(0.01)
    acc_x = statistics.median(acc_x_sum)
    acc_y = statistics.median(acc_y_sum)
    acc_z = statistics.median(acc_z_sum)
    gyro_x = statistics.median(gyro_x_sum)
    gyro_y = statistics.median(gyro_y_sum)
    gyro_z = statistics.median(gyro_z_sum)

    return acc_x, acc_y,acc_z,gyro_x, gyro_y, gyro_z


def get_open_angle(anglespeed, open_angle, last_time):
    delta_t = time.time() - last_time

    # Calculate the change in angle (in degrees) using the gyroscope's Z axis (c)
    # Gyroscope values are in degrees per second, so multiply by delta_t to get degrees
    delta_angle = anglespeed * delta_t
    if abs(delta_angle) < 1:
        delta_angle = 0.0  # Ignore small changes to reduce drift
    open_angle += delta_angle
    last_time = time.time()
    return open_angle, last_time


if __name__ == "__main__":
    import filterpy
    import filterpy.kalman as kf
    import numpy as np
    last_time = time.time()
    sensor = mpu6050(0x68)
    x_ref, y_ref, z_ref, a_off, b_off, c_off = calibrate_gyro(sensor)
    open_angle = 0.0
    a_angle, b_angle, c_angle = 0.0, 0.0, 0.0
    a_time, b_time, c_time = last_time, last_time, last_time
    v_ref = [x_ref, y_ref, z_ref]
    while True:
        data, gyro, temp=test_messure()

        # print("Beschleunigung X:", data['x'])
        # print("Beschleunigung Y:", data['y'])
        # print("Beschleunigung Z:", data['z'])
        # print("Gyroskop X:", gyro['x']-a_off)
        # print("Gyroskop Y:", gyro['y']-b_off)
        # print("Gyroskop Z:", gyro['z']-c_off)
        #print("Temperatur:", temp)
        
        x, y, z = data['x'], data['y'], data['z']
        x_sum, y_sum, z_sum, a_sum, b_sum, c_sum = [], [], [], [], [], []
        steps = 100
        for i in range(steps):
            data, gyro, temp=test_messure()
            x_sum.append(x)
            y_sum.append(y)
            z_sum.append(z)
            a_angle, a_time = get_open_angle(gyro['x']-a_off,a_angle, a_time)
            b_angle, b_time = get_open_angle(gyro['y']-b_off,b_angle, b_time)
            c_angle, c_time = get_open_angle(gyro['z']-c_off,c_angle, c_time)
            a_sum.append(a_angle)
            b_sum.append(b_angle)
            c_sum.append(c_angle)
            time.sleep(1/steps)
        
        x = statistics.median(x_sum)
        y = statistics.median(y_sum)
        z = statistics.median(z_sum)
        a = statistics.median(a_sum)
        b = statistics.median(b_sum)
        c = statistics.median(c_sum)


        print(f"Accelerometer X: {x-x_ref:.2f}, Y: {y-y_ref:.2f}, Z: {z-z_ref:.2f}")
        print(f"Gyroscope angles X: {a:.2f}, Y: {b:.2f}, Z: {c:.2f}")
        

        angle = get_tilt_angle(x_ref, y_ref, z_ref, x, y, z, )
        # open_angle, last_time = get_open_angle(a,b,c,open_angle, last_time)
        print(f"Open angle a: {a:.2f}°")
        print(f"Open angle c: {c:.2f}°")
        print(f"Open angle: {b:.2f}°")
        print(f"Tilt angle: {angle:.2f}°")


        # tilt angle works really well
        # open angle does suffer alot from drift
        # open angle is not reliable but seems to work for now
        # try kalman filer


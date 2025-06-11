import smbus2 
import time

MPU6050_ADDR = 0x4B
bus=smbus2.SMBus(1)

# Register-Adressen
PWR_MGMT_1   = 0x6B
ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H  = 0x43
TEMP_OUT_H   = 0x41

def start_up():
        # Sensor aktivieren
        bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0) 

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
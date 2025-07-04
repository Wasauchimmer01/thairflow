import smbus2 

name='SDP810'
SDP810_ADDR = 0x25
bus=smbus2.SMBus(1)

def start_up(nummer):
        status='ON'
        error=0
        who_am_i = bus.read_byte_data(SDP810_ADDR, 0x75)
        if who_am_i != SDP810_ADDR:
             status ='OFF'
             error=1
        return name,status,error,SDP810_ADDR,nummer

def read_sdp610(bus):
    try:
        # Lese 2 Bytes vom Sensor
        data = bus.read_i2c_block_data(SDP810_ADDR, 0xF1, 2)  # 0xF1 = Read Pressure Command
        raw_pressure = (data[0] << 8) | data[1]

        # Werte sind als signed integer
        if raw_pressure >= 32768:
            raw_pressure -= 65536

        # Umrechnung laut Sensirion-Datenblatt (bei SDP610-500Pa)
        pressure_pa = raw_pressure * 60.0 / 16384.0  # Umrechnung in Pascal

        return pressure_pa

    except Exception as e:
        return None

def Drucksensor():
    pressure = read_sdp610(bus)
    if pressure is not None:
        return pressure


#################################################
import time
import argparse
from sensirion_i2c_driver.linux_i2c_transceiver import LinuxI2cTransceiver
from sensirion_i2c_driver import I2cConnection
from sensirion_i2c_sdp import SdpI2cDevice
from sensirion_driver_adapters.i2c_adapter.i2c_channel import I2cChannel
from software.partikelsensor import get_args

# def main():
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--i2c-port', '-p', default='/dev/i2c-1',
#                         help='Linux I2C device path (default: /dev/i2c-1)')
#     args = parser.parse_args()

#     # Use LinuxI2cTransceiver to talk directly to I2C bus
#     with LinuxI2cTransceiver(args.i2c_port) as i2c_transceiver:
#         # Set up the SDP device at I2C address 0x25 (adjust if needed)
#         sdp = SdpI2cDevice(I2cConnection(i2c_transceiver), slave_address=0x25)

#         # Prepare and start measurement
#         sdp.stop_continuous_measurement()
#         sdp.start_continuous_measurement_with_mass_flow_t_comp()

#         try:
#             for _ in range(500):
#                 try:
#                     differential_pressure, temperature = sdp.read_measurement()
#                     # print("{}, {}".format(differential_pressure, temperature))
#                     # print("{:0.2f} °C ({} ticks), {:0.2f} Pa ({} ticks)".format(
#                     #     temperature.degrees_celsius, temperature.ticks,
#                     #     differential_pressure.pascal, differential_pressure.ticks))
#                     # time.sleep(0.2)
#                     print ("Differential Pressure: {} Pa".format(differential_pressure.pascal))
#                     time.sleep(1)
#                 except Exception as e:
#                     print(f"Error reading measurement: {e}")
#                     continue
#         finally:
#             sdp.stop_continuous_measurement()
#             print("Measurement stopped.")


def read_measurements(sensor):
    try:
        differential_pressure, temperature = sensor.read_measurement()
        #print ("Differential Pressure: {} Pa".format(differential_pressure.pascal))
        return differential_pressure, temperature
    except Exception as e:
        print(f"Error reading measurement: {e}")
        read_measurements(sensor)

def init_sensor(i2c_port, slave_address=0x25):
    """Initialisiert den Sensor und gibt das Sensorobjekt zurück."""
    i2c_transceiver = LinuxI2cTransceiver(i2c_port)
    channel = I2cChannel(
        I2cConnection(i2c_transceiver),
        slave_address=slave_address)
    
    sensor = SdpI2cDevice(I2cConnection(i2c_transceiver), slave_address=slave_address)
    sensor.stop_continuous_measurement()
    sensor.start_continuous_measurement_with_mass_flow_t_comp()
    return sensor, i2c_transceiver


def stop_sensor(sensor, i2c_transceiver):
    """Stoppt die Messung und schließt die Verbindung."""
    sensor.stop_continuous_measurement()
    i2c_transceiver.close()
    print("Measurement stopped and connection closed.")


def data_printout(data, show_temp=True):
    """Gibt die Messdaten aus."""
    differential_pressure, temperature = data
    print(f"Differential Pressure: {differential_pressure.pascal} Pa")
    if show_temp:
        print(f"Differential Pressure: {differential_pressure.pascal} Pa" + f"Temperature: {temperature.degrees_celsius} °C")


def test_run(slave_address=0x25):
    
    args = get_args()
    sensor, i2c_transceiver = init_sensor(args.i2c_port, slave_address=slave_address)
    i= 0
    while True:
        try:
            data = read_measurements(sensor)
            i += 1
            print(f"Measurement {i}")
            data_printout(data, show_temp = False)
            time.sleep(1)
        except KeyboardInterrupt:
            print("Measurement stopped by user.")
            break
 
    stop_sensor(sensor, i2c_transceiver)
    print("Measurement stopped.")

if __name__ == "__main__":
    test_run(slave_address=0x25)
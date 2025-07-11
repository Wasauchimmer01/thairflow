import time
from sensirion_i2c_driver.linux_i2c_transceiver import LinuxI2cTransceiver
from sensirion_i2c_driver import I2cConnection
from sensirion_i2c_sdp import SdpI2cDevice
from sensirion_driver_adapters.i2c_adapter.i2c_channel import I2cChannel
from software.utils import get_args, error_handler
import statistics


def read_measurements(sensor, error_retries=60, error_delay=0.5):
    for attempt in range(error_retries):
        try:
            differential_pressure, temperature = sensor.read_measurement()
            return differential_pressure, temperature
        except Exception as e:
            print(f"Error reading measurement (attempt {attempt + 1}): {e}")
            time.sleep(error_delay)
    print("All attempts failed.")
    print("trying to reconnect sensor")
    try:
        sensor.start_continuous_measurement_with_mass_flow_t_comp()
        return read_measurements(sensor, error_retries= 5, error_delay= 1)
    except Exception as e:
        print(f"Reconnection failed: {e}")
        raise RuntimeError("Failed to read measurements after retries.") from e

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



def rolling_mean(sensor, window_size, store):
    data = read_measurements(sensor, error_retries=60, error_delay=0.5)
    store.append(data)
    if len(store) > window_size:
        store.pop(0)
    avg_pressure = sum([d[0].pascal for d in store]) / len(store)
    return avg_pressure


def rolling_median(sensor, window_size, store):
    data = read_measurements(sensor, error_retries=60, error_delay=0.5)
    store.append(data)
    if len(store) > window_size:
        store.pop(0)
    avg_pressure = statistics.median([d[0].pascal for d in store])
    return avg_pressure
    


def test_run(slave_address=0x25):
    global ERROR_COUNT
    args = get_args()
    sensor, i2c_transceiver = init_sensor(args.i2c_port, slave_address=slave_address)
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
 
    stop_sensor(sensor, i2c_transceiver)
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
    test_run(slave_address=0x25)

    # since the sensor is very fast, we can use a rolling window smoothing to at least whatever global time interval we want
    # or like adapt it to the ramp up and down of the fan

    # mean or median does not seem to matter (at least not for a 1000 sample window)

    # 0.3Pa ~ 50m^3/h
    # 1Pa ~ 100m^3/h
    # 3.5Pa ~ 200m^3/h
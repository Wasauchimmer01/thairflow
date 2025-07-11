import time
import smbus2
from ads1015 import ADS1015

def setup_sensor(i2c_port=1, slave_address=0x48):
    """Initializes the ADS1015 sensor and returns the sensor object."""
    bus = smbus2.SMBus(i2c_port)

    ads1015 = ADS1015(slave_address)
    ads1015.set_mode("single")
    ads1015.set_programmable_gain(6.144)
    ads1015.set_sample_rate(1600)

    return ads1015
    

def get_values(ads1015:ADS1015, channels):
    """Reads voltage values from the specified channels."""
    #reference = ads1015.get_reference_voltage()
    values = {}

    for channel in channels:
        voltage = ads1015.get_voltage(channel=channel)
        values[channel] = {
            "voltage": voltage
        }

    return values


def test_output_status(values, interval=0.5, obs_time=120, on_off=False, obs_values=[], txt_output=False):
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


def test_run(slave_adress):
    sensor = setup_sensor(i2c_port=1, slave_address=slave_adress)
    channels = ["in0/ref"]#, "in1/ref", "in2/ref"]

    print(f"Sensor initialized at address {slave_adress}.")
    while True:
        values = get_values(sensor, channels)
        on_off, obs_values = test_output_status(values, interval=0.5, obs_time=120, on_off=False, obs_values=[], txt_output=True)


if __name__ == "__main__":

    test_run(slave_adress=0x48)

    # sensor = setup_sensor(i2c_port=1, slave_address=0x49) 
    # while True:
    #     try:
    #         values = get_values(sensor, channels=["in0/ref"])
    #         time.sleep(0.5)
    #         print(values["in0/ref"]["voltage"])
    #     except Exception as e:
    #         #print(f"Error reading sensor: {e}")
    #         time.sleep(1)


    # put vdd pin into addr pin for adress 0x49

    # could ether save data as is (observation window like 1sec) and calculate afterwards
    # or calculate based on observation time (like was there movement in the last 120 seconds)
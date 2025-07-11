from software.motionsensor import setup_sensor, get_values
import time



def output_to_status(value, open_closed=False):
    """Convert a voltage value to a status string."""
    if value > -0.1 and not open_closed:
        print("Door closed")
        with open("output.txt", "a") as f:
            f.write(f"Door closed, time:{time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        return True
    elif value < -0.1 and open_closed:
        print("Door open")
        with open("output.txt", "a") as f:
            f.write(f"Door opened, time:{time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        return False
    return open_closed

def test_run(slave_address):
    """Run the sensor setup and continuously read values."""
    sensor = setup_sensor(i2c_port=1, slave_address=slave_address)
    channels = ["in1/ref"]  # Define the channels to read
    #reference = sensor.get_reference_voltage()  # Get the reference voltage

    print(f"Sensor initialized at address {slave_address}.")
    open_closed = False  # Initial state of the sensor
    while True:
        try:
            values = get_values(sensor, channels)
            open_closed = output_to_status(values["in1/ref"]["voltage"], open_closed)
            #print(values["in1/ref"]["voltage"])  # Print the voltage reading
        except Exception as e:
            #print(f"Error: {e}")
            continue
        time.sleep(1)  # Sleep for a short duration before the next reading


if __name__ == "__main__":
    # Run the sensor with the specified slave address
    test_run(slave_address=0x48)  # Change the address as needed
    #test_run(slave_address=0x48)  # Uncomment to test with a different address

    # sensor = setup_sensor(i2c_port=1, slave_address=0x48)
    # print(sensor.get_reference_voltage())

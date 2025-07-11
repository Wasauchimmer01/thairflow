import argparse
import time

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--i2c-port', '-p', default='/dev/i2c-1')
    args = parser.parse_args()
    return args


def error_handler(func, func_args, restart_func, error_retries=60, error_delay=0.5):
    for attempt in range(error_retries):
        try:
            data = func(*func_args)
            return data
        except Exception as e:
            print(f"Error reading measurement (attempt {attempt + 1}): {e}")
            time.sleep(error_delay)
            #ERROR_COUNT += 1
    print("All attempts failed.")
    print("trying to reconnect sensor")
    try:
        restart_func()
        return error_handler(func, func_args, restart_func, error_retries= 5, error_delay= 1)
    except Exception as e:
        raise RuntimeError("Failed to read measurements after retries and restart.") from e
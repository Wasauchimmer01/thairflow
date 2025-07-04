import argparse

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--i2c-port', '-p', default='/dev/i2c-1')
    args = parser.parse_args()
    return args
import csv
import json
import os


sensordata = ['Name', 'Status','Error', 'Adresse']
data = []

 
with open('config.csv', 'w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=sensordata)
    writer.writeheader()
    writer.writerows(data)

def add_sensor(name,status,error,adresse,nummer):
    data += {'Name': name, 'Status': status,'Error':error, 'Adresse': adresse},


def load_imap_config(path: str = 'config_private/imap_config.json') -> dict:
    """Load IMAP configuration from a JSON file.

    The configuration must contain the following keys:
    imap_host, imap_port, use_ssl, username, password,
    mailbox, search_criteria.

    Args:
        path: Path to the JSON configuration file.

    Returns:
        A dictionary with the configuration values.

    Raises:
        FileNotFoundError: If the file does not exist.
        KeyError: If any required keys are missing.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"IMAP config file not found: {path}")

    with open(path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    required = [
        'imap_host',
        'imap_port',
        'use_ssl',
        'username',
        'password',
        'mailbox',
        'search_criteria',
    ]
    missing = [key for key in required if key not in config]
    if missing:
        raise KeyError(f"Missing keys in IMAP config: {', '.join(missing)}")

    return config

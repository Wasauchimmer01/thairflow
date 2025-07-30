from setuptools import setup, find_packages

setup(
    name='airflow-software',
    version='0.1.0',
    description='Sensor data acquisition and management software',
    author='Florian Aigner, Alexander Sommerfeld',
    packages=find_packages(),
    install_requires=[
        'smbus2',
        'gpiozero',
        'sensirion-i2c-driver>=1.0.0,<2.0',
        'sensirion-driver-adapters>=2.1.9,<3.0',
        'sensirion-driver-support-types>=1.1.0,<2.0',
        'sensirion-shdlc-sensorbridge>=0.1.0,<0.3.0',
        'openpyxl'
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'airflow-main=Main:Initialisieren',
        ],
    },
    include_package_data=True,
)
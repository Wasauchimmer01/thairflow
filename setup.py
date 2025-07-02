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
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'airflow-main=Main:Initialisieren',
        ],
    },
    include_package_data=True,
)
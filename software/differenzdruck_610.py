import smbus2 

name ='SDP610'
SDP610_ADDR = 0x40
bus=smbus2.SMBus(1)

def start_up(nummer):
        status='ON'
        error=0
        who_am_i = bus.read_byte_data(SDP610_ADDR, 0x75)
        if who_am_i != SDP610_ADDR:
             status ='OFF'
             error=1
        return name,status,error,SDP610_ADDR,nummer

def read_sdp610(bus):
    try:
        # Lese 2 Bytes vom Sensor
        data = bus.read_i2c_block_data(SDP610_ADDR, 0xF1, 2)  # 0xF1 = Read Pressure Command
        raw_pressure = (data[0] << 8) | data[1]

        # Werte sind als signed integer
        if raw_pressure >= 32768:
            raw_pressure -= 65536

        # Umrechnung laut Sensirion-Datenblatt (bei SDP610-500Pa)
        pressure_pa = raw_pressure * 60.0 / 16384.0  # Umrechnung in Pascal

        return pressure_pa

    except Exception as e:
        return None

def read_measurement():
    pressure = read_sdp610(bus)
    if pressure is not None:
        return pressure


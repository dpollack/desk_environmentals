# MMA8452Q setup and query code from ControlEverything
# https://github.com/ControlEverythingCommunity

import os
import smbus
import time
import signal
import sys
from datetime import datetime
from influxdb import InfluxDBClient

sys.path.append('./Adafruit_ADS1x15')
from Adafruit_ADS1x15 import ADS1x15

def signal_handler(signal, frame):
        print 'You pressed Ctrl+C!'
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
print 'Press Ctrl+C to exit'

#fname = 'accel_data_out'
#try:
#    os.unlink(fname)
#except:
#    print "no previous data file to remove"

# setup accelerometer
# Get I2C bus
bus = smbus.SMBus(1)

# MMA8452Q address, 0x1D(28)
# Select Control register, 0x2A(42)
#		0x00(00)	StandBy mode
bus.write_byte_data(0x1D, 0x2A, 0x00)
# MMA8452Q address, 0x1D(28)
# Select Control register, 0x2A(42)
#		0x01(01)	Active mode
bus.write_byte_data(0x1D, 0x2A, 0x01)
# MMA8452Q address, 0x1D(28)
# Select Configuration register, 0x0E(14)
#		0x00(00)	Set range to +/- 2g
bus.write_byte_data(0x1D, 0x0E, 0x00)

time.sleep(0.5)

# Initialise the ADC using the default mode (use default I2C address)
ADS1115 = 0x01  # 16-bit ADC
adc = ADS1x15(ic=ADS1115)

# setup sound detector
# Select the gain
# gain = 6144  # +/- 6.144V
gain = 4096  # +/- 4.096V
# gain = 2048  # +/- 2.048V
# gain = 1024  # +/- 1.024V
# gain = 512   # +/- 0.512V
# gain = 256   # +/- 0.256V

# Select the sample rate
# sps = 8    # 8 samples per second
# sps = 16   # 16 samples per second
# sps = 32   # 32 samples per second
sps = 64   # 64 samples per second
# sps = 128  # 128 samples per second
# sps = 250  # 250 samples per second
# sps = 475  # 475 samples per second
# sps = 860  # 860 samples per second

i = 0

#fout = open(fname, 'w')
#fout.write( "time, X, Y, Z\n" )

# while i < 432000: # 6 hour runtime
while True: # continuous run

    # MMA8452Q address, 0x1D(28)
    # Read data back from 0x00(0), 7 bytes
    # Status register, X-Axis MSB, X-Axis LSB, Y-Axis MSB, Y-Axis LSB, Z-Axis MSB, Z-Axis LSB
    data = bus.read_i2c_block_data(0x1D, 0x00, 7)

    # Convert the data
    xAccl = (data[1] * 256 + data[2]) / 16
    if xAccl > 2047 :
        xAccl -= 4096

    yAccl = (data[3] * 256 + data[4]) / 16
    if yAccl > 2047 :
        yAccl -= 4096

    zAccl = ((data[5] * 256 + data[6]) / 16) - 1000
    if zAccl > 2047 :
        zAccl -= 4096
    # read the volume voltage 0 - 4.096V
    voltsCh0 = adc.readADCSingleEnded(0, gain, sps) / 1000

    #convert the volume to a percentage of total
    volume = voltsCh0 / 4.096 * 100

    # Output data to DB
    ts = int(round(time.time() * 1000))
    fmtts = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
    #print ts
    # print a timestamp to show activity
    if i%200 == 0:
        print fmtts
    #print "Acceleration in X-Axis : %d" %xAccl
    #print "Acceleration in Y-Axis : %d" %yAccl
    #print "Acceleration in Z-Axis : %d" %zAccl
    json_body = []
    xval = {
            "measurement": "accels",
            "time_precision": "ms",
            "time": fmtts,
            "tags": {
            "dim": "X",
            },
            "fields": {
                "value": xAccl
            }
        }
    json_body.append(xval)
    yval = {
            "measurement": "accels",
            "time_precision": "ms",
            "time": fmtts,
            "tags": {
            "dim": "Y",
            },
            "fields": {
                "value": yAccl
            }
        }
    json_body.append(yval)
    zval = {
            "measurement": "accels",
            "time_precision": "ms",
            "time": fmtts,
            "tags": {
            "dim": "Z",
            },
            "fields": {
                "value": zAccl
            }
        }
    json_body.append(zval)
    #print json_body
    client = InfluxDBClient(host='localhost', port=8086, database='accel_data')
    client.write_points(json_body)
    json_body = []
    volpct = {
              "measurement": "volpct",
              "time_precision": "ms",
              "time": fmtts,
              "tags": {
              "dim": "vol",
              },
              "fields": {
                  "value": volume
              }
         }
    json_body.append(volpct)
    client = InfluxDBClient(host='localhost', port=8086, database='vol_data')
    client.write_points(json_body)
    #fout.write( str(ts) + ", " + str(xAccl) + ", " + str(yAccl) + ", " + str(zAccl) + "\n" )
    #time.sleep(0.0086)
    i = i + 1

#fout.close()

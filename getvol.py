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
#print 'Press Ctrl+C to exit'

ADS1115 = 0x01	# 16-bit ADC

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

# Initialise the ADC using the default mode (use default I2C address)
adc = ADS1x15(ic=ADS1115)
while True:

        fmtts = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
	# Read channels  in single-ended mode using the settings above

	print"--------------------"
	voltsCh0 = adc.readADCSingleEnded(0, gain, sps) / 1000
	rawCh0 = adc.readRaw(0, gain, sps) 
	print "Channel 0 =%.6fV raw=0x%4X" % (voltsCh0, rawCh0)
        #print voltsCh0 / 4.096 * 100
        volume = voltsCh0 / 4.096 * 100
        print volume
        print fmtts
	print"--------------------"
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
	time.sleep(0.05)

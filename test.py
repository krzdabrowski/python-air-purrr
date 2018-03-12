#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Copyright 2016, Frank Heuer, Germany
test.py is demonstrating some capabilities of the SDS011 module.
If you run this using your Nova Fitness Sensor SDS011 and
do not get any error (one warning will be ok) all is fine.

This is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

'''
import sys
import os
import time
from sds011 import SDS011


def printValues(timing, values, unit_of_measure):
    if unit_of_measure == SDS011.UnitsOfMeasure.MassConcentrationEuropean:
        unit = 'µg/m³'
    else:
        unit = 'pcs/0.01cft'
    print("Waited %d secs\nValues measured in %s:    PM2.5  " %
          (timing, unit), values[1], ", PM10 ", values[0])
    return 


sensor = SDS011("/dev/ttyUSB0", timeout=1, unit_of_measure=SDS011.UnitsOfMeasure.MassConcentrationEuropean)
sensor.reset()     


if __name__ == "__main__":            

    print("SDS011 sensor info:")
    print("Device ID: ", sensor.device_id)
    print("Device firmware: ", sensor.firmware)
    print("Current device cycle (0 is permanent on): ", sensor.dutycycle)
    print("Current workstate: ", sensor.workstate)
    print("Current reportmode: ", sensor.reportmode)

    while True:
        try:  # pojedynczy tryb rozgrzewania (okolo 30 sek)
            sensor.workstate = SDS011.WorkStates.Measuring
            with open('/var/www/html/workstate.txt', 'w') as f_workstate:
                print(sensor.workstate, file=f_workstate)
            sensor.dutycycle = 1
            last = time.time()
            while True:  # pojedyncze pingowanie podczas rozgrzewania (= timeout = 5 sek)
                last1 = time.time()
                values = sensor.get_values()
                if values is not None:
                    printValues(time.time() - last, values, sensor.unit_of_measure)
                    with open('/var/www/html/pm_data.txt', 'w') as f_data:
                        print(str(values[1]) + '\n' + str(values[0]), file=f_data)
                    break
                print("Waited %d secs, no values read, we try again" % (time.time() - last1))
                
            sensor.workstate = SDS011.WorkStates.Sleeping
            with open('/var/www/html/workstate.txt', 'w') as f_workstate:
                print(sensor.workstate, file=f_workstate)
            print("Read was successful. Going to sleep for 15 minutes")
            time.sleep(900)

        except KeyboardInterrupt:
            sensor.reset()
            with open('/var/www/html/workstate.txt', 'w') as f_workstate:
                print(sensor.workstate, file=f_workstate)
            sensor = None
            sys.exit("Sensor reset due to a KeyboardInterrupt")

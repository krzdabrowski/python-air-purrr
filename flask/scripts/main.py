#!/usr/bin/python3.7

'''
Copyright 2016, Frank Heuer, Germany
Reuse 2018, Krzysztof Dabrowski, Poland
Refactor 2019, Krzysztof Dabrowski, Poland

Main.py is designed to run continuously.
It includes warm-up mode (at least 30 secs) so it guarantees as correct as possible results.
Data is published using ThingSpeak platform.
Big thumbs-up to Frank for his awesome codebase - http://gitlab.com/frankrich/sds011_particle_sensor

This is distributed in the hope that it will be useful,
But WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
'''

import sys
import os
import time
import json
import paho.mqtt.publish as publish
from sds011 import SDS011


# create instance of sensor & clear it
sensor = SDS011("/dev/ttyUSB0", timeout=1, unit_of_measure=SDS011.UnitsOfMeasure.MassConcentrationEuropean)
sensor.reset()     

json_data = {}

# values need for ThingSpeak
channel_ID = "462987" # your channel_ID
with open('/home/pi/Desktop/write_api_key.txt', 'r') as f_api_key:
    write_api_key = f_api_key.read()
mqtt_host = "mqtt.thingspeak.com"
t_transport = "websockets"
t_port = 80
topic = "channels/" + channel_ID + "/publish/" + write_api_key


def print_values(timing, values, unit_of_measure):
    if unit_of_measure == SDS011.UnitsOfMeasure.MassConcentrationEuropean:
        unit = 'µg/m³'
    else:
        unit = 'pcs/0.01cft'

    print("Waited {:.0f} seconds".format(timing))
    print("Values measured in {0}: \t PM2.5 \t {1}  ,  PM10 \t {2}".format(unit, values[1], values[0]))
    return None


def publish_to_thingspeak():
    publish.single(topic, payload, hostname=mqtt_host, transport=t_transport, port=t_port)
    return None


if __name__ == "__main__":            

    # log some info at launch
    print("SDS011 sensor info:")
    print("Device ID: ", sensor.device_id)
    print("Device firmware: ", sensor.firmware)
    print("Current device cycle (0 is permanent on): ", sensor.dutycycle)
    print("Current workstate: ", sensor.workstate)
    print("Current reportmode: ", sensor.reportmode)

    while True:
        try:

            # warm-up mode
            sensor.workstate = SDS011.WorkStates.Measuring
            # update workstate for an app
            with open('/var/www/airpurrr.eu/html/data.json', 'w') as file_obj:
                json_data['workstate'] = str(sensor.workstate)
                json.dump(json_data, file_obj)
                # print(sensor.workstate, file=f_workstate)
            sensor.dutycycle = 1
            last = time.time()
            
            # query every single dutycycle (1 sec) if ready
            while True:
                last1 = time.time()
                values = sensor.get_values()
                if values is not None:
                    print_values(time.time() - last, values, sensor.unit_of_measure)
                    # make them online
                    with open('/var/www/airpurrr.eu/html/data.json', 'w') as file_obj:
                        json_data['values'] = {}
                        json_data['values']['pm25'] = values[1]
                        json_data['values']['pm10'] = values[0]
                        json.dump(json_data, file_obj)
                        # print(str(values[1]) + '\n' + str(values[0]), file=f_data)
                    break
                print("Waited {:.0f} secs, no values read, trying again".format(time.time() - last1))
            
            # sleeping mode
            sensor.workstate = SDS011.WorkStates.Sleeping
            # update workstate for an app
            with open('/var/www/airpurrr.eu/html/data.json', 'w') as file_obj:
                json_data['workstate'] = str(sensor.workstate)
                json.dump(json_data, file_obj)
                # print(sensor.workstate, file=f_workstate)
            # send data to ThingSpeak
            payload = "field1=" + str(values[1]) + "&amp;amp;field2=" + str(values[0])
            try:
                publish_to_thingspeak()
            except:
                print("Error or timeout while publishing data")
                
            # go to sleep
            print("Read was successful. Going to sleep for 15 minutes")
            time.sleep(900)

        except KeyboardInterrupt:
            sensor.reset()
            with open('/var/www/airpurrr.eu/html/data.json', 'w') as file_obj:
                json_data['workstate'] = str(sensor.workstate)
                json.dump(json_data, file_obj)
                # print(sensor.workstate, file=file_obj)
            sensor = None
            sys.exit("Sensor reset due to a KeyboardInterrupt")



#!/usr/bin/python3.7

'''
Copyright 2016, Frank Heuer, Germany
Reuse 2018, Krzysztof Dabrowski, Poland
Refactor 2019, Krzysztof Dabrowski, Poland

Main.py is designed to run continuously.
It includes warm-up mode (at least 30 secs) so it guarantees as correct as possible results.
Data is published using ThingSpeak platform.
Big thumbs-up to Frank for his awesome codebase: http://gitlab.com/frankrich/sds011_particle_sensor

This is distributed in the hope that it will be useful,
But WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
'''

import sys
import time
import json
import paho.mqtt.publish as publish
from sds011 import SDS011


sensor = SDS011("/dev/ttyUSB0", timeout=5, unit_of_measure=SDS011.UnitsOfMeasure.MassConcentrationEuropean)
json_data = {}

def init():
    sensor.reset()
    sensor.dutycycle = 1  # how much minute(s) SDS011 will wait before the measurement (maximum)

def save_workstate_to_json():
    with open('/var/www/airpurrr.eu/html/data.json', 'w') as f:
        json_data['workstate'] = str(sensor.workstate)
        json.dump(json_data, f)
        
def save_values_to_json(values):
    with open('/var/www/airpurrr.eu/html/data.json', 'w') as f:
        json_data['values'] = {}
        json_data['values']['pm25'] = values[1]
        json_data['values']['pm10'] = values[0]
        json.dump(json_data, f)

def set_measure_mode():
    sensor.workstate = SDS011.WorkStates.Measuring
    save_workstate_to_json()
    save_values_to_json([0.0, 0.0])

def get_values():
    print(f"\n1. Trying to get some values:")
    measure_time_start = time.time()
            
    while True:
        reading_interval = time.time()  # equals timeout from sensor (=5)
        values = sensor.get_values()
        if values is None:
            print(f"\t{time.time() - reading_interval:.0f} seconds elapsed, no values read, trying again...")
        else:
            print(f"2. {time.time() - measure_time_start:.0f} seconds elapsed, values measured:    PM2.5   {values[1]}µg/m³, PM10    {values[0]}µg/m³")
            save_values_to_json(values)
            return values

def publish_to_thingspeak(payload):
    print("3. Read completed. Publishing data to ThingSpeak...")

    with open('/home/pi/Desktop/write_api_key.txt', 'r') as api_key:
        write_api_key = api_key.read()
    publish.single("channels/462987/publish/" + write_api_key, payload, hostname="mqtt.thingspeak.com", transport="websockets", port=80)

def go_to_sleep():
    print("4. Publishing completed. See you in 15 minutes!")
    time.sleep(60 * 15)


if __name__ == "__main__":
    init()

    while True:
        try:
            set_measure_mode()
            values = get_values()
            
            sensor.workstate = SDS011.WorkStates.Sleeping
            save_workstate_to_json()

            publish_to_thingspeak("field1=" + str(values[1]) + "&field2=" + str(values[0]))
            go_to_sleep()

        except KeyboardInterrupt:
            save_workstate_to_json()
            sensor.reset()
            sensor = None
            sys.exit("Sensor reset due to a KeyboardInterrupt")

#!/usr/bin/python3.7

'''
Copyright 2016, Frank Heuer, Germany
Reuse and refactor 2018-2020, Krzysztof Dabrowski, Poland

Main.py is designed to run continuously.
It includes warm-up mode (at least 30 secs) so it guarantees as correct as possible results.
Big thumbs-up to Frank for his awesome codebase: http://gitlab.com/frankrich/sds011_particle_sensor

This is distributed in the hope that it will be useful,
But WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
'''

import sys
import os
import time
import requests
import paho.mqtt.client as mqtt
from sds011 import SDS011

sensor = SDS011('/dev/ttyUSB0')
mqtt_client = mqtt.Client(client_id="rpi")

mqtt_url = 'backend.airpurrr.eu'
database_url = 'http://backend.airpurrr.eu:8086/write?db=airquality_sds011'
database_location = '/home/pi/Desktop/db/cached_db.txt'


def init():
    sensor.reset()
    sensor.dutycycle = 1  # how much minute(s) SDS011 will wait before the measurement (maximum)

def configure_mqtt_client():
    mqtt_client.connect(mqtt_url)
    mqtt_client.loop_start()
    
def send_cached_values_to_influxdb_if_any():
    is_cache_empty = os.stat(database_location).st_size == 0
    
    if not is_cache_empty:
        try:
            print('Sending cache to InfluxDB...')
            with open(database_location, 'r') as cache:
                requests.post(url=database_url, data=cache.read())
            print('Send completed, CLEANING CACHE!!!')
            with open(database_location, 'w'): pass
        except:
            print('Error sending CACHE to InfluxDB!')

def publish_workstate_to_mosquitto(workstate):
    try:
        mqtt_client.publish("sds011/workstate", str(workstate), retain=True)  # retained = save last known good msg for client before subscription
    except:
        print('Error publishing workstate to Mosquitto')

def get_values():
    print(f'\n1. Trying to get some values:')
    measure_time_start = time.time()
            
    while True:
        reading_interval = time.time()  # equals timeout from sensor (=5)
        values = sensor.get_values()
        if values is None:
            print(f'\t{time.time() - reading_interval:.0f} seconds elapsed, no values read, trying again...')
        else:
            print(f'2. {time.time() - measure_time_start:.0f} seconds elapsed, values measured:    PM2.5   {values[1]}µg/m³, PM10    {values[0]}µg/m³')
            return values

def send_values_to_influxdb(values):
    print('3. Read completed. Sending values to database...')
    data_formatted = f'indoors_pollution pm25={values[1]},pm10={values[0]}'

    try:
        requests.post(url=database_url, data=data_formatted)
    except:
        print('Error sending data to InfluxDB, appending to cache...')
        with open(database_location, 'a') as cache:
            cache.write(f'{data_formatted} {time.time_ns()}\n')

def publish_values_to_mosquitto(payload):
    print('4. Publishing data to Mosquitto...')

    try:
        mqtt_client.publish("sds011/pollution", payload, retain=True)  # retained = save last known good msg for client before subscription
    except:
        print('Error publishing data to Mosquitto')

def go_to_sleep():
    print('5. Work is done. See you in 15 minutes!')
    time.sleep(29)  # 30 secs


if __name__ == '__main__':
    init()
    configure_mqtt_client()
    send_cached_values_to_influxdb_if_any()

    while True:
        try:
            # measuring
            sensor.workstate = SDS011.WorkStates.Measuring
            publish_workstate_to_mosquitto(sensor.workstate)
            values = get_values()
            
            # sending data
            sensor.workstate = SDS011.WorkStates.Sleeping
            publish_workstate_to_mosquitto(sensor.workstate)
            send_values_to_influxdb(values)
            publish_values_to_mosquitto(f'{str(values[1])},{str(values[0])}')
            
            go_to_sleep()

        except KeyboardInterrupt:
            publish_workstate_to_mosquitto(sensor.workstate)
            sensor.reset()
            sensor = None
            mqtt_client.loop_stop()
            sys.exit('Sensor reset due to a KeyboardInterrupt')

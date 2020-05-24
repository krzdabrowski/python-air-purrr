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
import paho.mqtt.client
import control_purifier
from sds011 import SDS011
from utils_mqtt import Mqtt

sensor = SDS011('/dev/ttyUSB0')
mqtt = Mqtt()
mqtt_client = paho.mqtt.client.Client(client_id="rpi")

database_url = 'http://backend.airpurrr.eu:8086/write?db=airquality_sds011'
cache_location = '/home/pi/Desktop/db/cached_db.txt'
local_database_location = '/home/pi/git-backend-air-purrr/backend-air-purrr/raspberry-pi/flask/local_db.csv'


def init():
    sensor.reset()
    sensor.dutycycle = 1  # how much minute(s) SDS011 will wait before the measurement (maximum)
    
def send_cached_sensor_airpollution_to_influxdb_if_any():
    is_cache_empty = os.stat(cache_location).st_size == 0
    
    if not is_cache_empty:
        try:
            print('Sending cache to InfluxDB...')
            with open(cache_location, 'r') as cache:
                requests.post(url=database_url, data=cache.read())
            print('Send completed, CLEANING CACHE!!!')
            with open(cache_location, 'w'): pass
        except:
            print('Error sending CACHE to InfluxDB!')

def get_sensor_airpollution_values():
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

def send_sensor_airpollution_to_influxdb(values):
    print('3. Read completed. Saving to local csv file and and sending to InfluxDB...')
    data_formatted = f'indoors_pollution pm25={values[1]},pm10={values[0]}'
    current_time_in_ns = time.time_ns()
    
    with open(local_database_location, 'a') as local_db:
        local_db.write(f'{data_formatted} {current_time_in_ns}\n')
    
    try:
        requests.post(url=database_url, data=data_formatted)
    except:
        print('Error sending data to InfluxDB, appending to cache...')
        with open(cache_location, 'a') as cache:
            cache.write(f'{data_formatted} {current_time_in_ns}\n')

def go_to_sleep():
    print('5. Work is done. See you in 30 seconds!')
    time.sleep(900)  # 30 secs  BYLO 29


if __name__ == '__main__':
    init()
    mqtt.configure_mqtt_client(mqtt_client)
    send_cached_sensor_airpollution_to_influxdb_if_any()

    while True:
        try:
            # pomiar
            sensor.workstate = SDS011.WorkStates.Measuring
            mqtt.workstate = SDS011.WorkStates.Measuring
            mqtt.publish_sensor_workstate(mqtt_client, sensor.workstate)
            airpollution_values = get_sensor_airpollution_values()
            
            # wyslanie danych
            sensor.workstate = SDS011.WorkStates.Sleeping
            mqtt.workstate = SDS011.WorkStates.Sleeping
            mqtt.publish_sensor_workstate(mqtt_client, sensor.workstate)
            send_sensor_airpollution_to_influxdb(airpollution_values)
            mqtt.publish_sensor_airpollution(mqtt_client, f'{str(airpollution_values[1])},{str(airpollution_values[0])}')
            
            go_to_sleep()

        except KeyboardInterrupt:
            mqtt.publish_sensor_workstate(mqtt_client, sensor.workstate)
            sensor.reset()
            sensor = None
            mqtt_client.loop_stop()
            sys.exit('Sensor reset due to a KeyboardInterrupt')

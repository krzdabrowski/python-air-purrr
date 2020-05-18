#!/usr/bin/python3.7

import json


sensor_state = ''
automode_state = False
automode_threshold = 100
performancemode_state = False

fan_topics = ['airpurifier/fan/state', 'airpurifier/fan/speed']
sensor_topics = ['airpurifier/sensor/state']
android_topics = ['android/automode/state', 'android/automode/threshold', 'android/performancemode/state']

def configure_mqtt_client(client):
    try:
        client.on_connect = on_subscribe_changes
        client.on_message = on_changes_received
        client.connect('localhost')
        client.loop_start()
    except:
        print('Error connecting to Mosquitto')

def on_subscribe_changes(client, userdata, flags, rc):
    try:
        client.subscribe(sensor_topics[0])
        
        client.subscribe(android_topics[0])
        client.subscribe(android_topics[1])
        client.subscribe(android_topics[2])
    except:
        print('Error subscribing channels to Mosquitto')
        
def on_changes_received(client, userdata, msg):
    if msg.topic == sensor_topics[0]:
        if msg.payload == 'WorkStates.Sleeping' or msg.payload == 'WorkStates.Measuring':
            sensor_state = msg.payload
        else:
            print('Incorrent message payload for fan state')
    elif msg.topic == android_topics[0]:
        if msg.payload == 'on':
            automode_state = True
            control_air_purifier_automatically()
        elif msg.payload == 'off':
            automode_state = False
            control_air_purifier_automatically()
        else:
            print('Incorrent message payload for android automode state')
    elif msg.topic == android_topics[1]:
        try:
            automode_threshold = int(msg.payload)
            control_air_purifier_automatically()
        except:
            print('Incorrent message payload for android automode threshold')
    elif msg.topic == android_topics[2]:
        if msg.payload == 'high':
            performancemode_state = True
            control_air_purifier_automatically()
        elif msg.payload == 'low':
            performancemode_state = False
            control_air_purifier_automatically()
        else:
            print('Incorrent message payload for fan speed')
    else:
        print('Incorrect message topic')
        
def publish_forecast_values(client, results, topic):
    payload = json.dumps(results)
    
    try:
        client.publish(topic, payload, retain=True)  # retained = save last known good msg for client before subscription
    except:
        print('Error publishing forecast data to Mosquitto')

def publish_air_purifier_fan_state(client, payload):
    try:
        client.publish(fan_topics[0], payload, retain=True)
    except:
        print('Error publishing fan state to Mosquitto')
        
def publish_air_purifier_fan_speed(client, payload):
    try:
        client.publish(fan_topics[1], payload, retain=True)
    except:
        print('Error publishing fan speed to Mosquitto')
        
def control_air_purifier_automatically():
    
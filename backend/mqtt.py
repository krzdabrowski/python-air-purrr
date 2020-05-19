#!/usr/bin/python3.7

import json
from main import forecast_topics, forecast_linear, forecast_nonlinear, forecast_xgboost, forecast_neural


fan_state = False
sensor_state = ''
automode_state = False
automode_threshold = 100
performancemode_state = False
forecast_choice = ''

fan_states = ['WorkStates.Sleeping', 'WorkStates.Measuring']

fan_topics = ['airpurifier/fan/state', 'airpurifier/fan/speed']
sensor_topics = ['airpurifier/sensor/state']
android_topics = ['android/automode/state', 'android/automode/threshold', 'android/performancemode/state', 'android/forecast/choice']

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
        client.subscribe(fan_topics[0])
        client.subscribe(sensor_topics[0])
        
        client.subscribe(android_topics[0])
        client.subscribe(android_topics[1])
        client.subscribe(android_topics[2])
        client.subscribe(android_topics[3])
    except:
        print('Error subscribing channels to Mosquitto')
        
def on_changes_received(client, userdata, msg):
    if msg.topic == fan_topics[0]:
        if msg.payload == 'on':
            fan_state = True
        elif msg.payload == 'off':
            fan_state = False
        else:
            print('Incorrent message payload for fan state')
    if msg.topic == sensor_topics[0]:
        if msg.payload in fan_states:
            sensor_state = msg.payload
            check_auto_control_of_air_purifier(client)
        else:
            print('Incorrent message payload for sensor state')
    elif msg.topic == android_topics[0]:
        if msg.payload == 'on':
            automode_state = True
            check_auto_control_of_air_purifier(client)
        elif msg.payload == 'off':
            automode_state = False
            check_auto_control_of_air_purifier(client)
        else:
            print('Incorrent message payload for android automode state')
    elif msg.topic == android_topics[1]:
        try:
            automode_threshold = int(msg.payload)
            check_auto_control_of_air_purifier(client)
        except:
            print('Incorrent message payload for android automode threshold')
    elif msg.topic == android_topics[2]:
        if msg.payload == 'high':
            performancemode_state = True
            check_auto_control_of_air_purifier(client)
        elif msg.payload == 'low':
            performancemode_state = False
            check_auto_control_of_air_purifier(client)
        else:
            print('Incorrent message payload for android performancemode state')
    elif msg.topic == android_topics[3]:
        if msg.payload in forecast_topics:
            forecast_choice = msg.payload
            check_auto_control_of_air_purifier(client)
        else:
            print('Incorrent message payload for android forecast choice')
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
        client.publish(fan_topics[0], str(payload), retain=True)
    except:
        print('Error publishing fan state to Mosquitto')
        
def publish_air_purifier_fan_speed(client, payload):
    try:
        client.publish(fan_topics[1], str(payload), retain=True)
    except:
        print('Error publishing fan speed to Mosquitto')
        
def check_auto_control_of_air_purifier(client):
    if automode_state == False or sensor_state == fan_states[1]:  # user doesn't want to use automatic mode, or sensor is in Measuring mode
        return
    
    forecast_values = select_forecast_of_choice()
    next_forecast_pm25 = forecast_values.get('pm25')[0]
    next_forecast_pm10 = forecast_values.get('pm10')[0]
    bigger_forecasted_value = max(next_forecast_pm25, next_forecast_pm10)
    
    if automode_threshold > bigger_forecasted_value:
        if fan_state == True:  # turn off air purifier
            fan_state == False
            publish_air_purifier_fan_state(client, 'off')
    else:
        if fan_state == False:  # turn on air purifier
            fan_state == True
            publish_air_purifier_fan_state(client, 'on')
        if performancemode_state == True:  # switch to high-speed mode
            publish_air_purifier_fan_speed(client, 'high')
        else:  # switch to low-speed mode
            publish_air_purifier_fan_speed(client, 'low')
            
            
def select_forecast_of_choice():   
    if forecast_choice == forecast_topics[0]:
        return forecast_linear
    elif forecast_choice == forecast_topics[1]:
        return forecast_nonlinear
    elif forecast_choice == forecast_topics[2]:
        return forecast_xgboost
    elif forecast_choice == forecast_topics[3]:
        return forecast_neural
    else:
        return dict()
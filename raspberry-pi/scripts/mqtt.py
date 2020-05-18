#!/usr/bin/python3.7

mqtt_url = 'backend.airpurrr.eu'
fan_topics = ['airpurifier/fan/state', 'airpurifier/fan/speed'] 
sensor_topics = ['airpurifier/sensor/state', 'airpurifier/sensor/pollution']

def configure_mqtt_client(client):
    try:
        client.on_connect = on_subscribe_fan_changes
        client.on_message = on_fan_changes_received
        client.connect(mqtt_url)
        client.loop_start()
    except:
        print('Error connecting to Mosquitto')
        
def on_subscribe_fan_changes(client, userdata, flags, rc):
    try:
        client.subscribe(fan_topics[0])
        client.subscribe(fan_topics[1])
    except:
        print('Error subscribing fan channels to Mosquitto')

def on_fan_changes_received(client, userdata, msg):
    if msg.topic == fan_topics[0]:
        if msg.payload == 'on':
            control_purifier.turn_on()
        elif msg.payload == 'off':
            control_purifier.turn_off()
        else:
            print('Incorrent message payload for fan state')
    elif msg.topic == fan_topics[1]:
        if msg.payload == 'high':
            control_purifier.high_mode()
        elif msg.payload == 'low':
            control_purifier.low_mode()
        else:
            print('Incorrent message payload for fan speed')
    else:
        print('Incorrect message topic')
        
def publish_sensor_workstate(client, workstate):
    try:
        client.publish(sensor_topics[0], str(workstate), retain=True)  # retained = save last known good msg for client before subscription
    except:
        print('Error publishing workstate to Mosquitto')
        
def publish_sensor_airpollution(client, payload):
    print('4. Publishing air pollution to Mosquitto...')

    try:
        client.publish(sensor_topics[1], payload, retain=True)
    except:
        print('Error publishing data to Mosquitto')

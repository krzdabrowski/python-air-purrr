#!/usr/bin/python3.7

import json

fan_states = ['WorkStates.Sleeping', 'WorkStates.Measuring']
fan_topics = ['airpurifier/fan/state', 'airpurifier/fan/speed']
sensor_topics = ['airpurifier/sensor/state']
android_topics = ['android/automode/state', 'android/automode/threshold', 'android/performancemode/state', 'android/forecast/choice']
forecast_topics = ['backend/forecast/linear', 'backend/forecast/nonlinear', 'backend/forecast/xgboost', 'backend/forecast/neuralnetwork']

class Mqtt:
    fan_state = False
    sensor_state = ''
    automode_state = False
    automode_threshold = 100
    performancemode_state = False
    forecast_choice = ''
    forecast_results = None
    
    def configure_mqtt_client(self, client):
        try:
            client.on_connect = self.on_subscribe_changes
            client.on_message = self.on_changes_received
            client.connect('localhost')
            client.loop_start()
        except:
           print('Error connecting to Mosquitto')
           
    def on_subscribe_changes(self, client, userdata, flags, rc):
        try:
            client.subscribe(fan_topics[0])
            client.subscribe(sensor_topics[0])
            
            client.subscribe(android_topics[0])
            client.subscribe(android_topics[1])
            client.subscribe(android_topics[2])
            client.subscribe(android_topics[3])
        except:
            print('Error subscribing channels to Mosquitto')
            
    def on_changes_received(self, client, userdata, msg):
        if msg.topic == fan_topics[0]:
            if msg.payload.decode('UTF-8') == 'on':
                self.fan_state = True
            elif msg.payload.decode('UTF-8') == 'off':
                self.fan_state = False
            else:
                print('Incorrent message payload for fan state')
        elif msg.topic == sensor_topics[0]:
            if msg.payload.decode('UTF-8') in fan_states:
                self.sensor_state = msg.payload.decode('UTF-8')
                self.check_auto_control_of_air_purifier(client)
            else:
                print('Incorrent message payload for sensor state')
        elif msg.topic == android_topics[0]:
            if msg.payload.decode('UTF-8') == 'on':
                self.automode_state = True
                self.check_auto_control_of_air_purifier(client)
            elif msg.payload.decode('UTF-8') == 'off':
                self.automode_state = False
                self.check_auto_control_of_air_purifier(client)
            else:
                print('Incorrent message payload for android automode state')
        elif msg.topic == android_topics[1]:
            try:
                self.automode_threshold = int(msg.payload.decode('UTF-8'))
                self.check_auto_control_of_air_purifier(client)
            except:
                print('Incorrent message payload for android automode threshold')
        elif msg.topic == android_topics[2]:
            if msg.payload.decode('UTF-8') == 'high':
                self.performancemode_state = True
                self.check_auto_control_of_air_purifier(client)
            elif msg.payload.decode('UTF-8') == 'low':
                self.performancemode_state = False
                self.check_auto_control_of_air_purifier(client)
            else:
                print('Incorrent message payload for android performancemode state')
        elif msg.topic == android_topics[3]:
            if msg.payload.decode('UTF-8') in forecast_topics:
                self.forecast_choice = msg.payload.decode('UTF-8')
                self.check_auto_control_of_air_purifier(client)
            else:
                print('Incorrent message payload for android forecast choice')
        else:
            print('Incorrect message topic')
            
    def publish_forecast_values(self, client, results, topic):
        payload = json.dumps(results)
        
        try:
            client.publish(topic, payload, retain=True)  # retained = save last known good msg for client before subscription
        except:
            print('Error publishing forecast data to Mosquitto')
    
    def publish_air_purifier_fan_state(self, client, payload):
        try:
            client.publish(fan_topics[0], str(payload), retain=True)
        except:
            print('Error publishing fan state to Mosquitto')
            
    def publish_air_purifier_fan_speed(self, client, payload):
        try:
            client.publish(fan_topics[1], str(payload), retain=True)
        except:
            print('Error publishing fan speed to Mosquitto')
    
    def check_auto_control_of_air_purifier(self, client):       
        if self.sensor_state == fan_states[1]:
            return
        
        forecast_values = self.select_forecast_of_choice()
        next_forecast_pm25 = forecast_values.get('pm25')[0]
        next_forecast_pm10 = forecast_values.get('pm10')[0]
        bigger_forecasted_value = max(next_forecast_pm25, next_forecast_pm10)
        
        if self.automode_state == False or self.automode_threshold > bigger_forecasted_value:
            if self.fan_state == True:  # turn off air purifier
                self.fan_state == False
                self.publish_air_purifier_fan_state(client, 'off')
        else:
            if self.fan_state == False:  # turn on air purifier
                self.fan_state == True
                self.publish_air_purifier_fan_state(client, 'on')
            if self.performancemode_state == True:  # switch to high-speed mode
                self.publish_air_purifier_fan_speed(client, 'high')
            else:  # switch to low-speed mode
                self.publish_air_purifier_fan_speed(client, 'low')
 
    def select_forecast_of_choice(self):        
        if self.forecast_choice == forecast_topics[0]:
            return self.forecast_results.linear
        elif self.forecast_choice == forecast_topics[1]:
            return self.forecast_results.nonlinear
        elif self.forecast_choice == forecast_topics[2]:
            return self.forecast_results.xgboost
        elif self.forecast_choice == forecast_topics[3]:
            return self.forecast_results.neural
        else:
            return dict()
   
#!/usr/bin/python3.7

import control_purifier
from sds011 import SDS011

mqtt_url = 'backend.airpurrr.eu'
fan_topics = ['airpurifier/fan/state', 'airpurifier/fan/speed'] 
sensor_topics = ['airpurifier/sensor/state', 'airpurifier/sensor/pollution']

class Mqtt:
	workstate = ''
	
	def configure_mqtt_client(self, client):
		try:
			client.on_connect = self.on_subscribe_fan_changes
			client.on_message = self.on_fan_changes_received
			client.connect(mqtt_url)
			client.loop_start()
		except:
			print('Error connecting to Mosquitto')
			
	def on_subscribe_fan_changes(self, client, userdata, flags, rc):
		try:
			client.subscribe(fan_topics[0])
			client.subscribe(fan_topics[1])
		except:
			print('Error subscribing fan channels to Mosquitto')

	def on_fan_changes_received(self, client, userdata, msg):
		if self.workstate == SDS011.WorkStates.Measuring:
			print('Sensor in measuring mode, cannot handle message')
			return
		
		if msg.topic == fan_topics[0]:
			if msg.payload.decode('UTF-8') == 'on':
				control_purifier.turn_on()
			elif msg.payload.decode('UTF-8') == 'off':
				control_purifier.turn_off()
			else:
				print('Incorrent message payload for fan state')
		elif msg.topic == fan_topics[1]:
			if msg.payload.decode('UTF-8') == 'high':
				control_purifier.high_mode()
			elif msg.payload.decode('UTF-8') == 'low':
				control_purifier.low_mode()
			else:
				print('Incorrent message payload for fan speed')
		else:
			print('Incorrect message topic')
			
	def publish_sensor_workstate(self, client, workstate):
		try:
			client.publish(sensor_topics[0], str(workstate), retain=True)  # retained = save last known good msg for client before subscription
		except:
			print('Error publishing workstate to Mosquitto')
			
	def publish_sensor_airpollution(self, client, payload):
		print('4. Publishing air pollution to Mosquitto...')

		try:
			client.publish(sensor_topics[1], payload, retain=True)
		except:
			print('Error publishing data to Mosquitto')

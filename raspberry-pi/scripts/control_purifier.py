#!/usr/bin/python3.7

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print('Error importing RPi.GPIO! This is probably because you need superuser privileges. Try "sudo" to run this script')
import sys
import time
from sds011 import SDS011

sensor = SDS011('/dev/ttyUSB0')

# use board pin references
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# pins to control each purifier's behaviour:
# * to turn it on: (11, 13)
# * to turn it off: 16, then (11, 13, 15)
# * to change between low-high mode: (15, 16)
# DO NOT CHANGE THESE PINS
pins_tuple = (11, 13, 15, 16)


def turn_on():
    print('Turning purifier on...')
    
    GPIO.setup(pins_tuple[0:2], GPIO.OUT)
    GPIO.output(pins_tuple[0:2], GPIO.LOW)
    
    set_sensor_to_sleep()

def turn_off():
    print('Turning purifer off...')
    
    GPIO.setup(pins_tuple, GPIO.OUT)
    GPIO.output(pins_tuple[-1], GPIO.HIGH)  # pin 16 first
    time.sleep(1)  # security purpose
    GPIO.output(pins_tuple[0:3], GPIO.HIGH)
    
    set_sensor_to_sleep()
    
def high_mode():
    print('Switching to high (performance) mode...')
    
    GPIO.setup(pins_tuple[2:], GPIO.OUT)
    
    GPIO.output(pins_tuple[2], GPIO.LOW)  # pin 15
    time.sleep(1)
    GPIO.output(pins_tuple[3], GPIO.LOW)  # pin 16
    
    set_sensor_to_sleep()    
    
def low_mode():
    print('Switching to low (night) mode...')
    
    GPIO.setup(pins_tuple[2:], GPIO.OUT)
    
    GPIO.output(pins_tuple[3], GPIO.HIGH) # pin 16
    time.sleep(1)
    GPIO.output(pins_tuple[2], GPIO.HIGH) # pin 15
    
    set_sensor_to_sleep()
    

def set_sensor_to_sleep():
    if (sensor.workstate != SDS011.WorkStates.Sleeping):
        sensor.workstate = SDS011.WorkStates.Sleeping


if __name__ == '__main__':
    try:
        turn_on() if sys.argv[1] == 'on' else turn_off()

    except KeyboardInterrupt:
        print('Quitting...') 
        GPIO.cleanup()
        
    finally:
        set_sensor_to_sleep()

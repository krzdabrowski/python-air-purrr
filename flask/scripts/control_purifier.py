#!/usr/bin/python3.7

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print('Error importing RPi.GPIO! This is probably because you need superuser privileges. Try "sudo" to run this script')
import sys
import main
from sds011 import SDS011


# Use BCM GPIO references instead of physical pin numbers
GPIO.setmode(GPIO.BCM)
pin_list = [14, 15]

def change_state(should_turn_on):
    gpio_state = GPIO.OUT if should_turn_on == 'on' else GPIO.IN
    
    try:
        for i in pin_list:
            GPIO.setwarnings(False)
            GPIO.setup(i, gpio_state)
    
        main.sensor.workstate = SDS011.WorkStates.Sleeping

    except KeyboardInterrupt:
        print('Quitting...') 
        GPIO.cleanup()


if __name__ == '__main__':
    try:
        change_state(sys.argv[1])

    except KeyboardInterrupt:
        print('Quitting...') 
        GPIO.cleanup()

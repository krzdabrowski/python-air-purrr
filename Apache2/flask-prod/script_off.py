#!/usr/bin/python3

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO! This is probably because you need superuser privileges. Try 'sudo' to run this script")
import time
<<<<<<< HEAD
import test
from subprocess import check_call
=======
import continuous_run as run
>>>>>>> 853649c... Alpha release
from sds011 import SDS011


# Use BCM GPIO references instead of physical pin numbers
GPIO.setmode(GPIO.BCM)
pinList = [14, 15]


def turn_off():
<<<<<<< HEAD:script_off.py
    
    for i in pinList:
        GPIO.setwarnings(False)
        print("Setup is changing to IN for pin no. ", i)
        GPIO.setup(i, GPIO.IN)
<<<<<<< HEAD
        
=======

    run.sensor.workstate = SDS011.WorkStates.Sleeping
>>>>>>> 853649c... Alpha release
    print("Pins have been clean-up")
    test.sensor.workstate = SDS011.WorkStates.Sleeping
    
    
=======
    try:    
        for i in pinList:
            GPIO.setwarnings(False)
            print("Setup is changing to IN for pin no.", i)
            GPIO.setup(i, GPIO.IN)

        run.sensor.workstate = SDS011.WorkStates.Sleeping
        print("Pins have been clean-up")

    except KeyboardInterrupt:
        print("Quitting...") 
        GPIO.cleanup()

             
>>>>>>> 2624d3d... Implement Flask webserver instead of PHP:Apache2/flask-prod/script_off.py
if __name__ == "__main__":
    try:
        turn_off()

    except KeyboardInterrupt:
        print("Quitting...") 
        GPIO.cleanup()

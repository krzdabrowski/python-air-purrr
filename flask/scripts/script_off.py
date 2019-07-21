#!/usr/bin/python3

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO! This is probably because you need superuser privileges. Try 'sudo' to run this script")
import time
import main
from sds011 import SDS011


# Use BCM GPIO references instead of physical pin numbers
GPIO.setmode(GPIO.BCM)
pinList = [14, 15]


def turn_off():
    try:    
        for i in pinList:
            GPIO.setwarnings(False)
            print("Setup is changing to IN for pin no.", i)
            GPIO.setup(i, GPIO.IN)

        main.sensor.workstate = SDS011.WorkStates.Sleeping
        print("Pins have been clean-up")

    except KeyboardInterrupt:
        print("Quitting...") 
        GPIO.cleanup()

             
if __name__ == "__main__":
    try:
        turn_off()

    except KeyboardInterrupt:
        print("Quitting...") 
        GPIO.cleanup()

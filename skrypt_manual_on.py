#!/usr/bin/python3

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO! This is probably because you need superuser privileges. Try 'sudo' to run this script")
import time
import test
from sds011 import SDS011


# Use BCM GPIO references instead of physical pin numbers
GPIO.setmode(GPIO.BCM)

pinList = [14, 15]


def turn_on():
    for i in pinList:
        GPIO.setwarnings(False)
        print("Ustawiam setup na OUT dla pinu", i)
        GPIO.setup(i, GPIO.OUT)
    
    test.sensor.workstate = SDS011.WorkStates.Sleeping

    while True:
    	time.sleep(0.1)
  

if __name__ == "__main__":

    try: 
        turn_on()
             
    except KeyboardInterrupt:
        print("Quitting...") 
        GPIO.cleanup()
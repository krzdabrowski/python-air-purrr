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


def trigger():
    for i in pinList:
        GPIO.setwarnings(True)
        print("Ustawiam setup na OUT dla pinu", i)
        GPIO.setup(i, GPIO.OUT)
    
    test.sensor.workstate = SDS011.WorkStates.Sleeping

    print("I czyszcze przez 10 sekund")
    time.sleep(10)
        
    print("Koniec roboty")
    GPIO.cleanup(pinList)
    
    test.sensor.workstate = SDS011.WorkStates.Measuring
    print("Pauza po zakonczeniu na 1 sekunde..")
    time.sleep(1)    
    test.sensor.workstate = SDS011.WorkStates.Sleeping
   
  
if __name__ == "__main__":

    try: 
        trigger()
             
    except KeyboardInterrupt:
        print("Quitting...") 
        GPIO.cleanup()

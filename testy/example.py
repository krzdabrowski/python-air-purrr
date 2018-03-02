#!/usr/bin/python3

import os.path
from time import sleep




print("example rozpoczyna sie")
while not os.path.exists("/home/pi/testy/USUNTO.py"):
    sleep(1)
    print("wciaz spie")
    
print("jestem obudzony")
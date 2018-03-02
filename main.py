#!/usr/bin/python3

import skrypt_10sec

with open('/home/pi/datas.txt', 'r') as f_input:
    dane = [float(i) for i in f_input.read().splitlines()]
    print(dane)

if any(x > 3 for x in dane):
    print("It's so bad")
    skrypt_10sec.trigger()
    
else:
    print("Ah not so bad lol'd")

#!/usr/bin/python3.7

from flask import Flask, request
from scripts import control_purifier

app = Flask(__name__)

@app.route('/control-on-off', methods=['POST'])
def control_turning_on_off():
    is_on_or_off = request.form['onOff']
    
    if is_on_or_off == 'on':
        control_purifier.turn_on()
    else:
        control_purifier.turn_off()

    return 'Turning on/off returns Success'
    
@app.route('/control-high-low', methods=['POST'])
def control_switching_low_high_modes():
    is_high_or_low = request.form['highLow']
    
    if is_high_or_low == 'high':
        control_purifier.high_mode()
    else:
        control_purifier.low_mode()

    return 'Switching high/low modes returns Success'


if __name__ == '__main__':
    app.run()
    

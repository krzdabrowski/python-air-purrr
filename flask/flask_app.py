#!/usr/bin/python3.7

import os
from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
from flask_bcrypt import Bcrypt
from scripts import control_purifier


app = Flask(__name__)
auth = HTTPBasicAuth()
bcrypt = Bcrypt(app)

@auth.verify_password
def login(request_auth_header_username, request_auth_header_password):
    db_path = '/home/pi/Desktop/db/db.txt'
    
    if os.stat(db_path).st_size != 0:
        with open(db_path, 'r') as f:            
            check_login = bcrypt.check_password_hash(f.readline().rstrip('\n'), request_auth_header_username)
            check_password = bcrypt.check_password_hash(f.readline().rstrip('\n'), request_auth_header_password)

        return check_login and check_password
                
    else:
        with open(db_path, 'w') as f:
            print(bcrypt.generate_password_hash('your_mail@domain.com').decode('utf-8'), sep='\n', file=f)
            print(bcrypt.generate_password_hash('your_password').decode('utf-8'), file=f)
            
        return False

@app.route('/control-on-off', methods=['POST'])
@auth.login_required
def control_turning_on_off():
    is_on_or_off = request.form['onOff']
    
    if is_on_or_off == 'on':
        control_purifier.turn_on()
    else:
        control_purifier.turn_off()

    return 'Turning on/off returns Success'
    
@app.route('/control-high-low', methods=['POST'])
@auth.login_required
def control_switching_low_high_modes():
    is_high_or_low = request.form['highLow']
    
    if is_high_or_low == 'high':
        control_purifier.high_mode()
    else:
        control_purifier.low_mode()

    return 'Swiotching high/low modes returns Success'


if __name__ == '__main__':
    app.run()
    

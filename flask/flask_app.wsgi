#!/usr/bin/python3.7

import sys

sys.path.insert(0, 'scripts')
sys.path.insert(1, '/home/pi/Desktop/db')

from flask_app import app as application
import config

application.config['SECRET_KEY'] = config.secret_key

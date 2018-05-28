import importlib.util
from flask import Flask, session, redirect, flash, request
from flask_basicauth import BasicAuth
from functools import wraps
from script_on import turn_on
from script_off import turn_off


# Import necessary scripts and helpers
database_helper = importlib.util.spec_from_file_location("database_helper", "/home/pi/Apache2/helper.py")
db_helper = importlib.util.module_from_spec(database_helper)
database_helper.loader.exec_module(db_helper)  # load helper.py
db_helper.open_database()  # load db file to memory

# Flask init
app = Flask(__name__)
basic_auth = BasicAuth(app)

app.config['BASIC_AUTH_USERNAME'] = db_helper.get_hashed_email()
app.config['BASIC_AUTH_PASSWORD'] = db_helper.get_hashed_password()
app.config['BASIC_AUTH_FORCE'] = False
app.config['SECRET_KEY'] = 'super secret key'


@app.route('/', methods=['POST'])
@basic_auth.required
def login():
    session['logged_in'] = True

    req = request.form.get("req")
    if req == "MANUAL=1" or req == "AUTO=1":
        turn_on()
    else:
        turn_off()

    return "done"


if __name__ == '__main__':
    app.run()


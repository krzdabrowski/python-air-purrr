#!/usr/bin/python3.7

from flask import Flask, session, redirect, flash, request
from flask_basicauth import BasicAuth
from scripts import control_purifier

app = Flask(__name__)
basic_auth = BasicAuth(app)

@app.route('/login', methods=['POST'])
@basic_auth.required
def login():
    control_purifier.change_state(request.form.get("shouldTurnOn"))


if __name__ == '__main__':
    app.run()

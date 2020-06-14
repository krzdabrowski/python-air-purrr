#!/usr/bin/python3.7

import pytz
import numpy as np
import pandas as pd
from datetime import timedelta


def get_input_forecast_array(forecast_hours_ahead):
    timedelta_next_full_hour = pd.Timedelta(hours=pd.Timestamp.utcnow().hour + 1)  # times in database in UTC!
    timedelta_last_full_hour = timedelta_next_full_hour + pd.Timedelta(hours=forecast_hours_ahead)
    timedelta_one_hour_in_nanosecs = pd.Timedelta(hours=1)
    
    return np.arange(
        start=timedelta_next_full_hour.value,
        stop=timedelta_last_full_hour.value,
        step=timedelta_one_hour_in_nanosecs.value
    ).reshape(-1, 1)

def get_input_forecast_formatted_array(forecast_hours_ahead):
    X_forecast = get_input_forecast_array(forecast_hours_ahead)
    X_forecast_strings = np.empty(forecast_hours_ahead, dtype=object)
        
    for index, forecast_full_hour in enumerate(X_forecast):
    # numpy array indexing returns 1-element array, hence [0]
        timedelta_full_hour = pd.Timedelta(forecast_full_hour[0]) + pd.Timedelta(hours=1)  # add +1 hour for Europe/Warsaw
        X_forecast_strings[index] = pd \
            .to_datetime(forecast_full_hour[0]) \
            .replace(tzinfo=pytz.utc) \
            .astimezone(pytz.timezone('Europe/Warsaw')) \
            .strftime('%H:%M')
            
        if timedelta_full_hour >= pd.Timedelta(days=1):  # input values for a new day
            X_forecast[index] = (timedelta_full_hour - pd.Timedelta(days=1)).value
    
    return X_forecast, X_forecast_strings.tolist()
    
def pm25_to_percentage(data):
    return [round(val * 4, 2) for val in data]
    
def pm10_to_percentage(data):
    return [round(val * 2, 2) for val in data]

def format_date(value):
    delta = timedelta(seconds=value[0]/(10 ** 9)) + timedelta(hours=2)  # convert to local time
    return delta.total_seconds() % (86400) / (60 * 60)  # get hours.minutes in float, with modulo 24-hours (1d2h -> 2h)
    
def rmse(predictions, targets):
    return np.sqrt(((predictions - targets) ** 2).mean())
#!/usr/bin/python3.7

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt  
import paho.mqtt.client as mqtt
from influxdb import DataFrameClient
from sklearn.linear_model import LinearRegression

mqtt_client = mqtt.Client(client_id="backend")
prediction_hours_ahead = 8

def configure_mqtt_client():
    mqtt_client.connect('localhost')
    mqtt_client.loop_start()
    
def get_dataframe():
    client = DataFrameClient(database='airquality_sds011')
    query_result = client.query('SELECT * FROM indoors_pollution;')
    dataframe = query_result['indoors_pollution']
    dataframe['time_of_a_day'] = pd.to_timedelta(dataframe.index.strftime('%H:%M:%S'))  # additional column to ease daily profile's creation
    
    return dataframe
    
def linear_regression(dataframe):
    X = (dataframe['time_of_a_day']) \
        .values \
        .astype(np.int64) \
        .reshape(-1, 1)
    Y_pm25 = dataframe.pm25.values
    Y_pm10 = dataframe.pm10.values
    
    model_pm25 = LinearRegression().fit(X, Y_pm25)
    model_pm10 = LinearRegression().fit(X, Y_pm10)
    
    print(f'Coefficient of determination for PM25: {model_pm25.score(X, Y_pm25)}')
    print(f'Coefficient of determination for PM10: {model_pm10.score(X, Y_pm10)}')
    
    timedelta_next_full_hour = pd.Timedelta(hours=pd.Timestamp.now().hour + 1)
    timedelta_last_full_hour = timedelta_next_full_hour + pd.Timedelta(hours=prediction_hours_ahead)
    timedelta_one_hour_in_nanosecs = pd.Timedelta(hours=1)

    X_prediction = np.arange(start=timedelta_next_full_hour.value, stop=timedelta_last_full_hour.value, step=timedelta_one_hour_in_nanosecs.value).reshape(-1, 1)
    X_prediction_strings = np.empty(prediction_hours_ahead, dtype=object)
    
    for index, prediction_full_hour in enumerate(X_prediction):
        timedelta_full_hour = pd.Timedelta(prediction_full_hour[0])  # numpy array indexing returns 1-element array, hence [0]
        X_prediction_strings[index] = pd.to_datetime(prediction_full_hour[0]).strftime('%H:%M')
        
        if timedelta_full_hour >= pd.Timedelta(days=1):  # get values for a new day
            X_prediction[index] = (timedelta_full_hour - pd.Timedelta(days=1)).value
    
    Y_pm25_prediction_perc = [round(val * 4, 2) for val in model_pm25.predict(X_prediction)]
    Y_pm10_prediction_perc = [round(val * 2, 2) for val in model_pm10.predict(X_prediction)]
    
    print(f'Linear regression prediction for pm25 in % is: {Y_pm25_prediction_perc}')
    print(f'Linear regression prediction for pm10 in % is: {Y_pm10_prediction_perc}')
    
    results = dict()
    results['hours'] = X_prediction_strings.tolist()
    results['pm25'] = Y_pm25_prediction_perc
    results['pm10'] = Y_pm10_prediction_perc
    
    return results
    
def publish_values_to_mosquitto(results):
    payload = json.dumps(results)

    try:
        mqtt_client.publish("forecast/linear", payload, retain=True)  # retained = save last known good msg for client before subscription
    except:
        print('Error publishing data to Mosquitto')


if __name__ == '__main__':
    configure_mqtt_client()
    dataframe = get_dataframe()
    
    results = linear_regression(dataframe)
    publish_values_to_mosquitto(results)
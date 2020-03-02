#!/usr/bin/python3.7

import json
import numpy as np
import pandas as pd
import paho.mqtt.client as mqtt
from influxdb import DataFrameClient

from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor

from daily_profile import DailyProfileModel
from neural import NeuralNetworkModel


mqtt_client = mqtt.Client(client_id="backend")

def configure_mqtt_client():
    mqtt_client.connect('localhost')
    mqtt_client.loop_start()
    
def get_dataframe():
    client = DataFrameClient(database='airquality_sds011')
    query_result = client.query('SELECT * FROM indoors_pollution;')
    dataframe = query_result['indoors_pollution']
    dataframe['time_of_a_day'] = pd.to_timedelta(dataframe.index.strftime('%H:%M:%S'))  # additional column to ease daily profile's creation
    
    return dataframe
  
def publish_values_to_mosquitto(results):
    payload = json.dumps(results)

    try:
        mqtt_client.publish("forecast/linear", payload, retain=True)  # retained = save last known good msg for client before subscription
    except:
        print('Error publishing data to Mosquitto')


if __name__ == '__main__':
    configure_mqtt_client()
    dataframe = get_dataframe()
    
    X_daily = (dataframe['time_of_a_day']) \
        .values \
        .astype(np.int64) \
        .reshape(-1, 1)
    Y_pm25 = dataframe.pm25.values
    Y_pm10 = dataframe.pm10.values
    
    
    print('Linear regression forecast results for PM25:')
    linear_pm25 = DailyProfileModel(regressor_type=LinearRegression())
    linear_pm25.calculate_regression(X_daily, Y_pm25)
    
    print('\nLinear regression forecast results for PM10:')
    linear_pm10 = DailyProfileModel(regressor_type=LinearRegression())
    linear_pm10.calculate_regression(X_daily, Y_pm10)
    
    
    print('\n\nDecision tree regression forecast results for PM25:')
    decision_tree_pm25 = DailyProfileModel(regressor_type=DecisionTreeRegressor())
    decision_tree_pm25.calculate_regression(X_daily, Y_pm25)
    
    print('\nDecision tree regression forecast results for PM10:')
    decision_tree_pm10 = DailyProfileModel(regressor_type=DecisionTreeRegressor())
    decision_tree_pm10.calculate_regression(X_daily, Y_pm10)
    
    
    print('\n\nRandom forest regression forecast results for PM25:')
    random_forest_pm25 = DailyProfileModel(regressor_type=RandomForestRegressor())
    random_forest_pm25.calculate_regression(X_daily, Y_pm25)
        
    print('\nRandom forest regression forecast results for PM10:')
    random_forest_pm10 = DailyProfileModel(regressor_type=RandomForestRegressor())
    random_forest_pm10.calculate_regression(X_daily, Y_pm10)
    
    
    print('\n\nNeural network regression forecast results for PM25:')
    neural_network_pm25 = NeuralNetworkModel(n_lag=60, n_seq=6, n_epochs=1, n_neurons=1)
    neural_network_pm25.calculate_regression(Y_pm25)
    
    print('\nNeural network regression forecast results for PM10:')
    neural_network_pm10 = NeuralNetworkModel(n_lag=60, n_seq=6, n_epochs=1, n_neurons=1)
    neural_network_pm10.calculate_regression(Y_pm10)
#!/usr/bin/python3.7

import numpy as np
import pandas as pd
import paho.mqtt.client

from influxdb import DataFrameClient
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor

from daily_profile import DailyProfileModel
from neural import NeuralNetworkModel
from utils import pm25_to_percentage, pm10_to_percentage
from mqtt import configure_mqtt_client, publish_forecast_values
from hypertuning import nonlinear_hyperparameters_tuning, xgboost_hyperparameters_tuning


mqtt_client = paho.mqtt.client.Client(client_id='backend')
forecast_topics = ['forecast/linear', 'forecast/nonlinear', 'forecast/xgboost', 'forecast/neuralnetwork']

def get_dataframe():
    client = DataFrameClient(database='airquality_sds011')
    query_result = client.query('SELECT * FROM indoors_pollution;')
    dataframe = query_result['indoors_pollution']
    dataframe['time_of_a_day'] = pd.to_timedelta(dataframe.index.strftime('%H:%M:%S'))  # additional column to ease daily profile's creation
    
    return dataframe
    
def linear_regression(X_daily, Y_pm25, Y_pm10):
    results = dict()
    print('Linear regression forecast results for PM25:')
    linear_pm25 = DailyProfileModel(regressor_type=LinearRegression())
    linear_pm25.calculate_regression(X_daily, Y_pm25)
    
    print('\nLinear regression forecast results for PM10:')
    linear_pm10 = DailyProfileModel(regressor_type=LinearRegression())
    linear_pm10.calculate_regression(X_daily, Y_pm10)
    
    if linear_pm25.hours == linear_pm10.hours:
        results['hours'] = linear_pm25.hours
        results['pm25'] = pm25_to_percentage(linear_pm25.forecast)
        results['pm10'] = pm10_to_percentage(linear_pm10.forecast)
        
        publish_forecast_values(mqtt_client, results, forecast_topics[0])

def nonlinear_regression(X_daily, Y_pm25, Y_pm10):
    results = dict()
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
    
    # I choose Random Forest for nonlinear for now
    if random_forest_pm25.hours == random_forest_pm10.hours:
        results['hours'] = random_forest_pm25.hours
        results['pm25'] = pm25_to_percentage(random_forest_pm25.forecast)
        results['pm10'] = pm10_to_percentage(random_forest_pm10.forecast)
        
        publish_forecast_values(mqtt_client, results, forecast_topics[1])

def xgboost_regression(X_daily, Y_pm25, Y_pm10):
    results = dict()
    print('\n\nXGBoost regression forecast results for PM25:')
    xgboost_pm25 = DailyProfileModel(regressor_type=XGBRegressor())
    xgboost_pm25.calculate_regression(X_daily, Y_pm25)
    
    print('\nXGBoost regression forecast results for PM10:')
    xgboost_pm10 = DailyProfileModel(regressor_type=XGBRegressor())
    xgboost_pm10.calculate_regression(X_daily, Y_pm10)
    
    if xgboost_pm25.hours == xgboost_pm10.hours:
        results['hours'] = xgboost_pm25.hours
        results['pm25'] = pm25_to_percentage(xgboost_pm25.forecast)
        results['pm10'] = pm10_to_percentage(xgboost_pm10.forecast)
        
        publish_forecast_values(mqtt_client, results, forecast_topics[2])

def neural_network_regression(Y_pm25, Y_pm10):
    results = dict()
    # print('\n\nNeural network regression forecast results for PM25:')
    # neural_network_pm25 = NeuralNetworkModel(isPm25=True, n_lag=1440, n_epochs=500, n_neurons=10) # hidden neurony miedzy 5 a 12 zalecane?
    # neural_network_pm25.calculate_regression(Y_pm25)
    
    print('\nNeural network regression forecast results for PM10:')
    neural_network_pm10 = NeuralNetworkModel(isPm25=False, n_lag=1440, n_epochs=500, n_neurons=10)
    neural_network_pm10.calculate_regression(Y_pm10)
    
    # if neural_network_pm25.hours == neural_network_pm10.hours:
    #     results['hours'] = neural_network_pm25.hours
    #     results['pm25'] = pm25_to_percentage(neural_network_pm25.forecast)
    #     results['pm10'] = pm10_to_percentage(neural_network_pm10.forecast)
        
    #     publish_forecast_values(mqtt_client, results, forecast_topics[3])


if __name__ == '__main__':    
    configure_mqtt_client(mqtt_client)
    dataframe = get_dataframe()
    
    X_daily = (dataframe['time_of_a_day']) \
        .values \
        .astype(np.int64) \
        .reshape(-1, 1)
    Y_pm25 = dataframe.pm25.values
    Y_pm10 = dataframe.pm10.values
    
    # print('##### HYPERPARAMETERS TUNING #####')
    
    # nonlinear_hyperparameters_tuning(X_daily, Y_pm25, Y_pm10)
    # xgboost_hyperparameters_tuning(X_daily, Y_pm25, Y_pm10)

    print('\n\n##### CALCULATING PREDICTIONS #####')
    
    # linear_regression(X_daily, Y_pm25, Y_pm10)
    # nonlinear_regression(X_daily, Y_pm25, Y_pm10)
    # xgboost_regression(X_daily, Y_pm25, Y_pm10)
    neural_network_regression(Y_pm25, Y_pm10)
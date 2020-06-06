#!/usr/bin/python3.7

import time
import numpy as np
import pandas as pd
import paho.mqtt.client

from influxdb import DataFrameClient
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from datetime import datetime
from matplotlib import pyplot as plt

from daily_profile import DailyProfileModel
from neural import NeuralNetworkModel
from utils_mqtt import Mqtt
from utils_calculation import pm25_to_percentage, pm10_to_percentage, format_date
from hypertuning import nonlinear_hyperparameters_tuning, xgboost_hyperparameters_tuning


class ForecastResults():
    linear = dict()
    nonlinear = dict()
    xgboost = dict()
    neural = dict()


mqtt = Mqtt()  
mqtt_client = paho.mqtt.client.Client(client_id='backend')
forecast_topics = ['backend/forecast/linear', 'backend/forecast/nonlinear', 'backend/forecast/xgboost', 'backend/forecast/neuralnetwork']
forecast_results = ForecastResults()

def get_dataframe():
    client = DataFrameClient(database='airquality_sds011')
    query_result = client.query('SELECT * FROM indoors_pollution;')
    dataframe = query_result['indoors_pollution']
    dataframe['time_of_a_day'] = pd.to_timedelta(dataframe.index.strftime('%H:%M:%S'))  # additional column to ease daily profile's creation
    
    return dataframe
    
def create_daily_profile_plot(X, Y):    
    X_formatted = np.apply_along_axis(format_date, 1, X)
        
    plt.xlabel("Godzina") 
    plt.ylabel(u"$PM_{10}\ [\u03bcg/m^3]$") 
    ax = plt.gca()
    ax.set_xticks([0.01, 6, 12, 18, 23.999])
    ax.set_xticklabels(['00:00', '06:00', '12:00', '18:00', '24:00'])

    plt.plot(X_formatted, Y, '.', markersize=1)
    plt.margins(0,0)
    plt.savefig('daily_profile_plot.png', bbox_inches='tight', dpi=450)
    
def linear_regression(X_daily, Y_pm25, Y_pm10):
    start_time = datetime.now()
    
    results = dict()
    print('Linear regression forecast results for PM25:')
    linear_pm25 = DailyProfileModel(regressor_type=LinearRegression())
    linear_pm25.calculate_regression(X_daily, Y_pm25)
    
    print('\nLinear regression forecast results for PM10:')
    linear_pm10 = DailyProfileModel(regressor_type=LinearRegression())
    linear_pm10.calculate_regression(X_daily, Y_pm10)
    
    end_time = datetime.now() - start_time
    print(f'Execution time for linear was: {end_time} hours')
    
    if linear_pm25.hours == linear_pm10.hours:
        results['hours'] = linear_pm25.hours
        results['pm25'] = pm25_to_percentage(linear_pm25.forecast)
        results['pm10'] = pm10_to_percentage(linear_pm10.forecast)
        
        mqtt.publish_forecast_values(mqtt_client, results, forecast_topics[0])
    return results

def nonlinear_regression(X_daily, Y_pm25, Y_pm10):
    start_time_decision_tree = datetime.now()
    results = dict()
    
    print('\n\nDecision tree regression forecast results for PM25:')
    decision_tree_pm25 = DailyProfileModel(regressor_type=DecisionTreeRegressor(max_features='sqrt'))
    decision_tree_pm25.calculate_regression(X_daily, Y_pm25)
    
    print('\nDecision tree regression forecast results for PM10:')
    decision_tree_pm10 = DailyProfileModel(regressor_type=DecisionTreeRegressor(max_features='sqrt'))
    decision_tree_pm10.calculate_regression(X_daily, Y_pm10)
    
    end_time_decision_tree = datetime.now() - start_time_decision_tree
    print(f'Execution time for decision tree was: {end_time_decision_tree} hours')
    
    
    start_time_random_forest = datetime.now()
    
    print('\n\nRandom forest regression forecast results for PM25:')
    random_forest_pm25 = DailyProfileModel(regressor_type=RandomForestRegressor(max_features=None, n_estimators=250))
    random_forest_pm25.calculate_regression(X_daily, Y_pm25)
        
    print('\nRandom forest regression forecast results for PM10:')
    random_forest_pm10 = DailyProfileModel(regressor_type=RandomForestRegressor(max_features='log2', n_estimators=250))
    random_forest_pm10.calculate_regression(X_daily, Y_pm10)
    
    end_time_random_forest = datetime.now() - start_time_random_forest
    print(f'Execution time for random forest was: {end_time_random_forest} hours')
    
    # I choose Random Forest for nonlinear for now
    if random_forest_pm25.hours == random_forest_pm10.hours:
        results['hours'] = random_forest_pm25.hours
        results['pm25'] = pm25_to_percentage(random_forest_pm25.forecast)
        results['pm10'] = pm10_to_percentage(random_forest_pm10.forecast)
        
        mqtt.publish_forecast_values(mqtt_client, results, forecast_topics[1])
    return results

def xgboost_regression(X_daily, Y_pm25, Y_pm10):
    start_time = datetime.now()
    results = dict()
    
    print('\n\nXGBoost regression forecast results for PM25:')
    xgboost_pm25 = DailyProfileModel(regressor_type=XGBRegressor(n_estimators=200, learning_rate=0.01))
    xgboost_pm25.calculate_regression(X_daily, Y_pm25)
    
    print('\nXGBoost regression forecast results for PM10:')
    xgboost_pm10 = DailyProfileModel(regressor_type=XGBRegressor(n_estimators=200, learning_rate=0.01))
    xgboost_pm10.calculate_regression(X_daily, Y_pm10)
    
    end_time = datetime.now() - start_time
    print(f'Execution time for XGBoost was: {end_time} hours')
    
    if xgboost_pm25.hours == xgboost_pm10.hours:
        results['hours'] = xgboost_pm25.hours
        results['pm25'] = pm25_to_percentage(xgboost_pm25.forecast)
        results['pm10'] = pm10_to_percentage(xgboost_pm10.forecast)
        
        mqtt.publish_forecast_values(mqtt_client, results, forecast_topics[2])
    return results

def neural_network_regression(Y_pm25, Y_pm10):
    start_time = datetime.now()

    results = dict()
    print('\n\nNeural network regression forecast results for PM25:')
    neural_network_pm25 = NeuralNetworkModel(isPm25=True, n_lag=1440, n_epochs=500, n_neurons=10)
    neural_network_pm25.calculate_regression(Y_pm25)
    
    print('\nNeural network regression forecast results for PM10:')
    neural_network_pm10 = NeuralNetworkModel(isPm25=False, n_lag=1440, n_epochs=500, n_neurons=10)
    neural_network_pm10.calculate_regression(Y_pm10)
    
    end_time = datetime.now() - start_time
    print(f'Execution time for neural network was: {end_time} hours')
    
    if neural_network_pm25.hours == neural_network_pm10.hours:
        results['hours'] = neural_network_pm25.hours
        results['pm25'] = pm25_to_percentage(neural_network_pm25.forecast)
        results['pm10'] = pm10_to_percentage(neural_network_pm10.forecast)
        
        mqtt.publish_forecast_values(mqtt_client, results, forecast_topics[3])
    return results


if __name__ == '__main__':  
    mqtt.configure_mqtt_client(mqtt_client)
    
    while True:
        dataframe = get_dataframe()
    
        X_daily = (dataframe['time_of_a_day']) \
            .values \
            .astype(np.int64) \
            .reshape(-1, 1)
        Y_pm25 = dataframe.pm25.values
        Y_pm10 = dataframe.pm10.values
    
        # create_daily_profile_plot(X_daily, Y_pm10)

        # print('##### HYPERPARAMETERS TUNING #####')
    
        # nonlinear_tuning_params = nonlinear_hyperparameters_tuning(X_daily, Y_pm25, Y_pm10)
        # xgboost_tuning_params = xgboost_hyperparameters_tuning(X_daily, Y_pm25, Y_pm10)

        print('\n\n##### CALCULATING PREDICTIONS #####')
    
        forecast_results.linear = linear_regression(X_daily, Y_pm25, Y_pm10)
        forecast_results.nonlinear = nonlinear_regression(X_daily, Y_pm25, Y_pm10)
        forecast_results.xgboost = xgboost_regression(X_daily, Y_pm25, Y_pm10)
        forecast_results.neural = neural_network_regression(Y_pm25, Y_pm10)
        mqtt.forecast_results = forecast_results

        print('Going to sleep for next 15 minutes...')
        time.sleep(60*15)

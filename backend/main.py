#!/usr/bin/python3.7

import json
import pytz
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt  
import paho.mqtt.client as mqtt
from influxdb import DataFrameClient
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from math import sqrt


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

def get_daily_profile_data(dataframe):
    X = (dataframe['time_of_a_day']) \
        .values \
        .astype(np.int64) \
        .reshape(-1, 1)
    Y_pm25 = dataframe.pm25.values
    Y_pm10 = dataframe.pm10.values
    
    return (X, Y_pm25, Y_pm10)

def calculate_regression(daily_profile, regressor_for_pm25, regressor_for_pm10):
    X, Y_pm25, Y_pm10 = daily_profile
        
    model_pm25 = regressor_for_pm25.fit(X, Y_pm25)
    model_pm10 = regressor_for_pm10.fit(X, Y_pm10)
    
    print(f'Coefficient of determination for PM25: {model_pm25.score(X, Y_pm25)}')
    print(f'Coefficient of determination for PM10: {model_pm10.score(X, Y_pm10)}')
    
    timedelta_next_full_hour = pd.Timedelta(hours=pd.Timestamp.utcnow().hour + 1)  # times in database in UTC!
    timedelta_last_full_hour = timedelta_next_full_hour + pd.Timedelta(hours=prediction_hours_ahead)
    timedelta_one_hour_in_nanosecs = pd.Timedelta(hours=1)

    X_prediction = np.arange(start=timedelta_next_full_hour.value, stop=timedelta_last_full_hour.value, step=timedelta_one_hour_in_nanosecs.value).reshape(-1, 1)
    X_prediction_strings = np.empty(prediction_hours_ahead, dtype=object)
    
    for index, prediction_full_hour in enumerate(X_prediction):
    # numpy array indexing returns 1-element array, hence [0]
        timedelta_full_hour = pd.Timedelta(prediction_full_hour[0]) + pd.Timedelta(hours=1)  # add +1 hour for Europe/Warsaw
        X_prediction_strings[index] = pd \
            .to_datetime(prediction_full_hour[0]) \
            .replace(tzinfo=pytz.utc) \
            .astimezone(pytz.timezone('Europe/Warsaw')) \
            .strftime('%H:%M')
        
        if timedelta_full_hour >= pd.Timedelta(days=1):  # get values for a new day
            X_prediction[index] = (timedelta_full_hour - pd.Timedelta(days=1)).value
    
    Y_pm25_prediction_perc = [round(val * 4, 2) for val in model_pm25.predict(X_prediction)]
    Y_pm10_prediction_perc = [round(val * 2, 2) for val in model_pm10.predict(X_prediction)]

    print(f'Prediction for pm25 in % is: {Y_pm25_prediction_perc}')
    print(f'Prediction for pm10 in % is: {Y_pm10_prediction_perc}')
    
    results = dict()
    results['hours'] = X_prediction_strings.tolist()
    results['pm25'] = Y_pm25_prediction_perc
    results['pm10'] = Y_pm10_prediction_perc
    
    return results
    
def calculate_neural(dataframe):
    X = (dataframe.index) \
        .values \
        .astype(np.int64) \
    
    Y_pm25 = dataframe.pm25.values
    Y_pm10 = dataframe.pm10.values
    
    n_lag = 60  # ile minut wstecz bierze pod uwage - w teorii nie powinien chyba wiecej niz max czas do kolejnej predykcji? + najwazniejsza do detekcji czy jest dobre powietrze czy zle = to co bedzie w kolejnej rownej godzinie
    n_seq = 6  # ile minut predykcja do przodu
    n_epochs = 1 # ile epok 
    n_neurons = 1 # ile neuronow
    
    scaler, data = prepare_data(Y_pm25, n_lag, n_seq)
    model = fit_lstm(data, n_lag, n_seq, n_epochs, n_neurons)
    forecast = make_forecast(model, data, n_lag)
    inversed_forecast = inverse_transform(Y_pm25, forecast, scaler, n_seq-1)
    print(f'predicted: {inversed_forecast}') 


# convert time series into supervised learning problem
def timeseries_to_supervised(data, n_in=1, n_out=1, dropnan=True):
    df = pd.DataFrame(data)
    cols = list()
    
    # input sequence (t-n, ... t-1)
    for i in range(n_in, 0, -1):
        cols.append(df.shift(i))
        
    # forecast sequence (t, t+1, ... t+n)
    for i in range(0, n_out):
        cols.append(df.shift(-i))
            
    # put it all together
    agg = pd.concat(cols, axis=1)
    
   	# drop rows with NaN values
    if dropnan:
        agg.dropna(inplace=True)
    
    return agg
    
    
# create a differenced series
def difference(dataset, interval=1):
    diff = list()
    for i in range(interval, len(dataset)):
        value = dataset[i] - dataset[i - interval]
        diff.append(value)
    
    return pd.Series(diff)


# transform series for supervised learning
def prepare_data(raw_values, n_lag, n_seq):
    # transform data to be stationary
    diff_series = difference(raw_values, 1)
    diff_values = diff_series.values
    diff_values = diff_values.reshape(len(diff_values), 1)
    
    # rescale values to [-1, 1]
    scaler = MinMaxScaler(feature_range=(-1, 1))
    scaled_values = scaler.fit_transform(diff_values)
    scaled_values = scaled_values.reshape(len(scaled_values), 1)
    
    # transform into supervised learning problem X, y
    supervised = timeseries_to_supervised(scaled_values, n_lag, n_seq)
    supervised_values = supervised.values

    return scaler, supervised_values
     

# fit an LSTM network to training data
def fit_lstm(data, n_lag, n_seq, nb_epoch, n_neurons):
    # reshape training into [samples, timesteps, features]
    X, y = data[:, 0:n_lag], data[:, n_lag:]
    X = X.reshape(X.shape[0], 1, X.shape[1])
    
    # design network
    model = Sequential()
    model.add(LSTM(n_neurons, batch_input_shape=(1, X.shape[1], X.shape[2]), stateful=True))
    model.add(Dense(y.shape[1]))
    model.compile(loss='mean_squared_error', optimizer='adam')
    
    # fit network
    for i in range(nb_epoch):
        model.fit(X, y, epochs=1, batch_size=1, shuffle=False)
        model.reset_states()
    return model


# forecast with an LSTM
def make_forecast(model, data, n_lag):
    forecasts = list()
    X, y = data[0, 0:n_lag], data[0, n_lag:]
    
    # reshape input pattern to [samples, timesteps, features]
    X = X.reshape(1, 1, len(X))
    
    # make forecast
    forecast = model.predict(X, batch_size=1)
    
    # convert to array
    return [x for x in forecast[0, :]]
    

# invert differenced forecast
def inverse_difference(last_ob, forecast):
    inverted = list()
    inverted.append(forecast[0] + last_ob)
    
    return inverted
    
    
# inverse data transform on forecasts
def inverse_transform(series, forecasts, scaler, n_seq):
    inverted = list()
    
    for i in range(len(forecasts)):
        # create array from forecast
        forecast = np.array(forecasts[i])
        forecast = forecast.reshape(1, -1)
        
        # invert scaling
        inv_scale = scaler.inverse_transform(forecast)
        inv_scale = inv_scale[0, :]
        
        # invert differencing
        index = len(series) - n_seq + i - 1
        last_ob = series[index]
        inv_diff = list()
        inv_diff.append(inv_scale[0] + last_ob)
        
        # store
        inverted.append(inv_diff)
    return inverted


def publish_values_to_mosquitto(results):
    payload = json.dumps(results)

    try:
        mqtt_client.publish("forecast/linear", payload, retain=True)  # retained = save last known good msg for client before subscription
    except:
        print('Error publishing data to Mosquitto')


if __name__ == '__main__':
    # configure_mqtt_client()
    # daily_profile = get_daily_profile_data(get_dataframe())
    
    # print('Linear regression prediction results: \n')
    # results = calculate_regression(daily_profile, LinearRegression(), LinearRegression())
    # publish_values_to_mosquitto(results)
    
    # print('\n\nDecision tree regression prediction results: \n')
    # calculate_regression(daily_profile, DecisionTreeRegressor(), DecisionTreeRegressor())
    
    # print('\n\nRandom forest regression prediction results: \n')
    # calculate_regression(daily_profile, RandomForestRegressor(), RandomForestRegressor())
    
    calculate_neural(get_dataframe())
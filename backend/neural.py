#!/usr/bin/python3.7

import numpy as np
import pandas as pd

from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.models import load_model
from keras.layers import Dropout
from keras.layers import Dense
from keras.layers import LSTM

from utils import get_input_forecast_formatted_array 


class NeuralNetworkModel:
    def __init__(self, isPm25, n_lag, n_epochs, n_neurons, forecast_hours_ahead = 6):
        self.isPm25 = isPm25
        self.forecast_hours_ahead = forecast_hours_ahead
        self.minutes_of_forecasts_array = self.get_minutes_of_forecasts_from_now()
        _, self.hours = get_input_forecast_formatted_array(forecast_hours_ahead)
    
        self.n_lag = n_lag  # ile minut wstecz bierze pod uwage - w teorii nie powinien chyba wiecej niz max czas do kolejnej predykcji? + najwazniejsza do detekcji czy jest dobre powietrze czy zle = to co bedzie w kolejnej rownej godzinie = INPUT NEURONS (?)
        self.n_seq = forecast_hours_ahead * 60  # ile minut predykcja do przodu (max 6h, realnie miedzy 5 a 6h) = OUTPUT NEURONS
        self.n_epochs = n_epochs  # ile epok 
        self.n_neurons = n_neurons  # ile neuronow


    def get_minutes_of_forecasts_from_now(self):
        timedelta_now = pd.Timedelta(hours=pd.Timestamp.now().hour, minutes=pd.Timestamp.now().minute)
        timedelta_next_full_hour = pd.Timedelta(hours=pd.Timestamp.now().hour + 1)
        next_full_hour_in_minutes_from_now = (timedelta_next_full_hour - timedelta_now).seconds // 60  # 60 seconds in minute
        last_full_hour_in_minutes_from_now = (timedelta_next_full_hour - timedelta_now + pd.Timedelta(hours=self.forecast_hours_ahead)).seconds // 60
        
        return np.arange(
            start=next_full_hour_in_minutes_from_now,
            stop=last_full_hour_in_minutes_from_now,
            step=60
        )  # 60 minutes in hour  

    
    # create a differenced series
    def difference(self, dataset, interval=1):
        diff = list()
        for i in range(interval, len(dataset)):
            value = dataset[i] - dataset[i - interval]
            diff.append(value)
        
        return pd.Series(diff)
    
    # convert time series into supervised learning problem
    def timeseries_to_supervised(self, data, n_in=1, n_out=1, dropnan=True):
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
    
    # transform series for supervised learning
    def calculate_regression(self, raw_values):
        self.raw_values = raw_values
    
        # transform data to be stationary
        diff_series = self.difference(raw_values, 1)
        diff_values = diff_series.values
        diff_values = diff_values.reshape(len(diff_values), 1)
        
        # rescale values to [-1, 1]
        self.scaler = MinMaxScaler(feature_range=(-1, 1))
        scaled_values = self.scaler.fit_transform(diff_values)
        scaled_values = scaled_values.reshape(len(scaled_values), 1)
        
        # transform into supervised learning problem X, y
        supervised = self.timeseries_to_supervised(scaled_values, self.n_lag, self.n_seq)
        supervised_values = supervised.values
        
        # split into train and test sets
        train, test = supervised_values[0:-1440], supervised_values[-1440:]  # last 1440 samples (1 day) to make a prediction (test)
    
        ### self.fit_lstm(supervised_values) ###
        
        # load model
        if self.isPm25:
            model = load_model('pm25_model_50k_500_epochs.h5')
        else:
            model = load_model('pm10_model_50k_500_epochs.h5')
        
        self.make_forecast(model, test)
     
    ### fit an LSTM network to training data ###
    def fit_lstm(self, train):
        # reshape training into [samples, timesteps, features]
        X, y = train[:, 0:self.n_lag], train[:, self.n_lag:]
        X = X.reshape(X.shape[0], 1, X.shape[1])
        
        # design network
        model = Sequential()
        model.add(LSTM(self.n_neurons, batch_input_shape=(1, X.shape[1], X.shape[2]), stateful=True))
        model.add(Dropout(0.2))
        model.add(Dense(y.shape[1]))
        model.compile(loss='mean_squared_error', optimizer='adam')
                
        # fit network
        for i in range(self.n_epochs):
            model.fit(X, y, epochs=1, batch_size=1, shuffle=False)
            model.reset_states()
            
        ### model.save("pm10_model_50k_500_epochs.h5") ###
        ### print("Model saved") ###
        
        ### self.make_forecast(model, train) ###

    # forecast with LSTM
    def make_forecast(self, model, test):
        X, y = test[0, 0:self.n_lag], test[0, self.n_lag:]
        
        # reshape input pattern to [samples, timesteps, features]
        X = X.reshape(1, 1, len(X))
        
        # make forecast
        forecast = model.predict(X, batch_size=1)
        
        # convert to array
        forecast_array = [x for x in forecast[0, :]]
        
        # inverse data transform on forecast
        self.inverse_transform(forecast_array)
        
    # inverse data transform on forecasts
    def inverse_transform(self, forecasts):
        # create array from forecast
        forecast = np.array(forecasts).reshape(1, -1)
            
        # invert scaling
        inv_scale = self.scaler.inverse_transform(forecast)
        inv_scale = inv_scale[0, :]
            
        # invert differencing
        index = len(self.raw_values) - 1
        last_ob = self.raw_values[index]
        inverted = self.inverse_difference(last_ob, inv_scale)
            
        self.forecast = [inverted[i-1] for i in self.minutes_of_forecasts_array]
        print(f'Forecast is: {self.forecast}')
        
    # invert differenced forecast
    def inverse_difference(self, last_ob, forecast):
        # invert first forecast
        inverted = list()
        inverted.append(forecast[0] + last_ob)

        # propagate difference forecast using inverted first value
        for i in range(1, len(forecast)):
            inverted.append(forecast[i] + inverted[i-1])
        
        return inverted
#!/usr/bin/python3.7

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM


class NeuralNetworkModel:
    def __init__(self, n_lag, n_seq, n_epochs, n_neurons, forecast_hours_ahead = 8):
        self.n_lag = n_lag  # ile minut wstecz bierze pod uwage - w teorii nie powinien chyba wiecej niz max czas do kolejnej predykcji? + najwazniejsza do detekcji czy jest dobre powietrze czy zle = to co bedzie w kolejnej rownej godzinie
        self.n_seq = n_seq  # ile minut predykcja do przodu
        self.n_epochs = n_epochs  # ile epok 
        self.n_neurons = n_neurons  # ile neuronow
        self.forecast_hours_ahead = forecast_hours_ahead
    
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
    
        self.fit_lstm(supervised_values)
     
    # fit an LSTM network to training data
    def fit_lstm(self, data):
        # reshape training into [samples, timesteps, features]
        X, y = data[:, 0:self.n_lag], data[:, self.n_lag:]
        X = X.reshape(X.shape[0], 1, X.shape[1])
        
        # design network
        model = Sequential()
        model.add(LSTM(self.n_neurons, batch_input_shape=(1, X.shape[1], X.shape[2]), stateful=True))
        model.add(Dense(y.shape[1]))
        model.compile(loss='mean_squared_error', optimizer='adam')
        
        # fit network
        for i in range(self.n_epochs):
            model.fit(X, y, epochs=1, batch_size=1, shuffle=False)
            model.reset_states()
            
        self.make_forecast(model, data)

    # forecast with LSTM
    def make_forecast(self, model, data):
        forecasts = list()
        X, y = data[0, 0:self.n_lag], data[0, self.n_lag:]
        
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
        inverted = list()
        
        for i in range(len(forecasts)):
            # create array from forecast
            forecast = np.array(forecasts[i])
            forecast = forecast.reshape(1, -1)
            
            # invert scaling
            inv_scale = self.scaler.inverse_transform(forecast)
            inv_scale = inv_scale[0, :]
            
            # invert differencing
            index = len(self.raw_values) - self.n_seq + i - 1
            last_ob = self.raw_values[index]
            inv_diff = list()
            inv_diff.append(inv_scale[0] + last_ob)
            
            # store
            inverted.append(inv_diff)
            
        print(f'Predicted: {inverted}') 
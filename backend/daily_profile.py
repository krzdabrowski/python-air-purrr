#!/usr/bin/python3.7

import pytz
import numpy as np
import pandas as pd


class DailyProfileModel:
    def __init__(self, regressor_type, forecast_hours_ahead = 8):
        self.regressor_type = regressor_type
        self.forecast_hours_ahead = forecast_hours_ahead
    
    def calculate_regression(self, daily_profile_input, daily_profile_output):            
        model = self.regressor_type.fit(daily_profile_input, daily_profile_output)
        print(f'Coefficient of determination: {model.score(daily_profile_input, daily_profile_output)}')
        
        X_forecast = self.get_input_forecast_array()
        X_forecast_strings = np.empty(self.forecast_hours_ahead, dtype=object)
        
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
        
        Y_forecast_perc = [round(val * 4, 2) for val in model.predict(X_forecast)]
        print(f'Forecast in % is: {Y_forecast_perc}')
        
        self.hours = X_forecast_strings.tolist()
        self.forecast = Y_forecast_perc

        
    def get_input_forecast_array(self):
        timedelta_next_full_hour = pd.Timedelta(hours=pd.Timestamp.utcnow().hour + 1)  # times in database in UTC!
        timedelta_last_full_hour = timedelta_next_full_hour + pd.Timedelta(hours=self.forecast_hours_ahead)
        timedelta_one_hour_in_nanosecs = pd.Timedelta(hours=1)
    
        return np.arange(
            start=timedelta_next_full_hour.value,
            stop=timedelta_last_full_hour.value,
            step=timedelta_one_hour_in_nanosecs.value
        ).reshape(-1, 1)
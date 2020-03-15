#!/usr/bin/python3.7

from utils import get_input_forecast_formatted_array 

class DailyProfileModel:
    def __init__(self, regressor_type, forecast_hours_ahead = 6):
        self.regressor_type = regressor_type
        self.forecast_hours_ahead = forecast_hours_ahead
    
    def calculate_regression(self, daily_profile_input, daily_profile_output):            
        model = self.regressor_type.fit(daily_profile_input, daily_profile_output)
        print(f'Coefficient of determination: {model.score(daily_profile_input, daily_profile_output)}')
        
        X_forecast, self.hours = get_input_forecast_formatted_array(self.forecast_hours_ahead)

        self.forecast = model.predict(X_forecast)
        print(f'Forecast is: {self.forecast}')
#!/usr/bin/python3
import sql_writer 
import api_handler

FORECAST_NAMES = ['time', 'min_percipitation', 'mean_percipitation', 'max_percipitation', 'type_percipitation', 'frozen_percipitation']
TEMP_NAMES = ['time', 'temperature']
RAIN_NAMES = ['time', 'percipitation']
ENERGY_NAMES = ['time', 'kwh']

def main():
    smhi_api = api_handler.SmhiApi()
    sql = sql_writer.Writer()
    
    rain = smhi_api.get_rain()
    temperature = smhi_api.get_temp()
    perc_forecast = smhi_api.get_perc_forecast(24)
    temp_forecast = smhi_api.get_temp_forecast(24)
        
    sql.write('station',RAIN_NAMES,rain)
    sql.write('station',TEMP_NAMES,temperature)
    sql.write('forecast',TEMP_NAMES,temp_forecast)
    sql.write('forecast',FORECAST_NAMES,perc_forecast)
    
    sql.terminate_connection()

if __name__ == "__main__":
    main()
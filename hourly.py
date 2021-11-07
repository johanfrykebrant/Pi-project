#!/usr/bin/python3
import sql_writer 
import api_handler
import metrics as m

PARAMETER_NAMES = ['time', 'name','value','unit']
METRIC_NAMES = ['time', 'hostname','temperature','used_gig','total_gig']

def main():
    smhi_api = api_handler.SmhiApi()
    sql = sql_writer.Writer()
    
    metrics = m.get_metrics()
    sql.write('cpu_metrics',METRIC_NAMES,metrics)    

    measurements = smhi_api.get_all_measurements()
    for value in measurements:
        sql.write('station',PARAMETER_NAMES,value)
    
    forecasts = smhi_api.get_all_forecasts()
    for value in forecasts:
        sql.write('forecast',PARAMETER_NAMES,value)
    
    sql.terminate_connection()
    
if __name__ == "__main__":
    main()
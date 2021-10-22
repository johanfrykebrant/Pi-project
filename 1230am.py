#!/usr/bin/python3
import sql_writer 
import api_handler

PRICE_NAMES = ['time', 'kwh']

def main():
    tibber_api = api_handler.TibberApi()
    
    sql = sql_writer.Writer()
    energy = tibber_api.get_consumption()
    sql.write_many('energy',PRICE_NAMES,energy)
    
    sql.terminate_connection()
    
    

if __name__ == "__main__":
    main()

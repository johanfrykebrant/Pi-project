#!/usr/bin/python3
import sql_writer 
import api_handler

PRICE_NAMES = ['time', 'sek']

def main():
    tibber_api = api_handler.TibberApi()
    
    sql = sql_writer.Writer()
    energy_prices = tibber_api.get_prices_tomorrow()
    
    sql.write_many('energy',PRICE_NAMES,energy_prices)
    
    sql.terminate_connection()
    
    

if __name__ == "__main__":
    main()
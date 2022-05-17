from api_handler import SmhiApi
import json
import mysql.connector
from os.path import join
from os import getcwd


def upsert_forecast(forecasts):

    with open(join(getcwd() ,'.config')) as json_data_file:
        config = json.load(json_data_file)
            
    # --- Connecting to Database ---
    con = mysql.connector.connect(
        host= config["mysql"]["host"],
        user= config["mysql"]["user"],
        password= config["mysql"]["passwd"],
        database= config["mysql"]["db"]
    )

    cur = con.cursor()
    for forecast in forecasts:
        # Get Id for specific measurement
        select_id = ("SELECT forecast_id FROM forecast_ids WHERE name = %(name)s")
        cur.execute(select_id, forecast)

        # Should only return one value. write it to the forecast dict.
        for (forecast_id) in cur:    
            forecast["id"] = forecast_id[0]

    # Write measurement value to db
    add_measurement =   ("REPLACE INTO current_forecasts"
                        "(timestamp, value, forecast_id) "
                        "VALUES (%(timestamp)s, %(value)s, %(id)s)")
    cur.executemany(add_measurement, forecasts)

    # Commit and close connection
    con.commit()
    cur.close()
    con.close()

def main():
    api = SmhiApi()
    forecast_range = range(25)
    r = api.get_forecasts_hours_in_future(hours_in_future=forecast_range)
    upsert_forecast(r)

    
if __name__ == "__main__":
    main()
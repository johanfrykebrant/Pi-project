import mysql.connector
import TibberAPI as API
import json
import logging


# --- Configuring logging ---
logging.basicConfig(filename='/Projects/Error.log', level=logging.WARNING,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# --- Fetching config parameters ---
try:    
    with open("/home/pi/Projects/SQL.config") as json_data_file:
        data = json.load(json_data_file)
except Exception as e:
    logging.error(e)
else:
    # --- Connecting to Database ---
    cn = mysql.connector.connect(
      host= data["mysql"]["host"],
      user= data["mysql"]["user"],
      password= data["mysql"]["pw"],
      database= data["mysql"]["powerdb"]
    )

    cur = cn.cursor()

def hourly():
    try:
        #[Time, consumption]
        tempData = API.get_consumption()
    except Exception as e:
        logging.error(e)
    else:    
        time = tempData[0]
        cons = tempData[1]
        # --- Insert Data in SQL server ---
        #Power: (Time datetime, Consumption DECIMAL(4,2))
        cur.execute("INSERT INTO Power (Time, Consumption) VALUES (%s,%s)", (time,cons))
        cn.commit()


def daily():
    try:
        #[Time, consumption]
        tempData = API.get_prices_tomorrow()
    except Exception as e:
        logging.error(e)
    else:
        for x in tempData:
            time = tempData[0][0]
            cons = tempData[0][1]
            # --- Insert Data in SQL server ---
            #Power: (Time datetime, Consumption DECIMAL(4,2))
            cur.execute("INSERT INTO Power (Time, Consumption) VALUES (%s,%s)", (time,cons))
            cn.commit()
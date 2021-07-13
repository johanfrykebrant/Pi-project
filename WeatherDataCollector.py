import mysql.connector
from datetime import datetime
import numpy as np
import json
import API
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
    mydb = mysql.connector.connect(
      host= data["mysql"]["host"],
      user= data["mysql"]["user"],
      password= data["mysql"]["pw"],
      database= data["mysql"]["db"]
    )

    mycursor = mydb.cursor()

# --- Get Data ---
try:
    tempData = API.getTemp()
    rainData = API.getRain()
except Exception as e:
    logging.error(e)
else:
    time = tempData[0]
    temp = tempData[1]
    rain = rainData[1]
    
    # --- Insert Data in SQL server ---
    #Time datetime, Temperature DECIMAL(4,2),Percipitation 
    mycursor.execute("INSERT INTO Station (Time, Temperature, Percipitation) VALUES (%s,%s,%s)", (time,temp,rain))
    mydb.commit()
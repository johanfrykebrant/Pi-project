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
    #[ValidTime, temp]
    tempData = API.getTempForecast(25)
    #[ValidTime, Pmin, Pmean, Pmax, PercCat, PercentFrozen]
    percData = API.getPercForecast(25)
except Exception as e:
    logging.error(e)
else:    
    time = tempData[0]
    temp = tempData[1]
    minPerc = percData[1]
    meanPerc = percData[2]
    maxPerc = percData[3]
    typePerc = percData[4]
    frozenPerc = percData[5]
    # --- Insert Data in SQL server ---
    #Forecast: (Time datetime, Temperature DECIMAL(4,2), MinPercipitation DECIMAL(6,1), MeanPercipitation DECIMAL(6,1), MaxPercipitation DECIMAL(6,1), TypePercipitation CHAR(20), FrozenPercipitation TINYINT)")
    mycursor.execute("INSERT INTO Forecast (Time, Temperature, MinPercipitation, MeanPercipitation, MaxPercipitation, TypePercipitation, FrozenPercipitation) VALUES (%s,%s,%s,%s,%s,%s,%s)", (time,temp,minPerc,meanPerc,maxPerc,typePerc,frozenPerc))
    mydb.commit()


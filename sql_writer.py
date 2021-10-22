import mysql.connector
from datetime import datetime
import numpy as np
import json
import logging

class Writer:
      
    def __init__(self):
        # --- Configuring logging ---
        logging.basicConfig(filename='./error.log', level=logging.WARNING,
                            format='%(asctime)s:%(levelname)s:%(message)s')

        # --- Fetching config parameters ---
        try:    
            with open("/home/pi/Projects/.config") as json_data_file:
                data = json.load(json_data_file)
        except Exception as e:
            logging.error(e)
        else:
            # --- Connecting to Database ---
            self.con = mysql.connector.connect(
              host= data["mysql"]["host"],
              user= data["mysql"]["user"],
              password= data["mysql"]["passwd"],
              database= data["mysql"]["db"]
            )

            self.cur = self.con.cursor()
       
    def __build_string(self,table,names):
        v = ""
        s = ""
        for i in names:
            v = v + i + ","
            s = s + "%s,"
        v = v[:-1]
        s = s[:-1]
        return "INSERT INTO " + table + " (" + v + ") VALUES (" + s + ")"
    
    def write(self,table,names,values):
        self.table=table
        self.names=names
        self.values=values
        
        command_string = self.__build_string(table,names)

        self.cur.execute(command_string,values)
        self.con.commit()
        
    def write_many(self,table,names,values):
        command_string = self.__build_string(table,names)
        for value in values:
            self.cur.execute(command_string,value)
            self.con.commit()
            
        
    def terminate_connection(self):
        self.cur.close()
        self.con.close()
        pass
        


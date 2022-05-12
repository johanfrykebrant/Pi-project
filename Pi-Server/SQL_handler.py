import mysql.connector
import json
import logging


class SQL_handler:
      
    def __init__(self,schema):
        
        with open(".config") as json_data_file:
                config = json.load(json_data_file)
               
        # --- Connecting to Database ---
        self.con = mysql.connector.connect(
          host= config["mysql"]["host"],
          user= config["mysql"]["user"],
          password= config["mysql"]["passwd"],
          database= config["mysql"]["db"]
        )

        self.schema = schema["databases"][config["mysql"]["db"]]["tables"]

        self.cur = self.con.cursor()

    def __build_value_str__(self,table,jobj):
        value_names = self.schema[table]["collumns"]
        l = []
        try:
            for nest_obj in jobj:
                row = []
                for value_name in value_names:
                    if "_id" in value_name:
                        try:
                            param_name = nest_obj["name"]
                            row.append("'" + str(self.schema[table]["ids"][param_name]) + "'")
                        except KeyError as ke:
                            raise KeyError(f"The parameter with name {param_name} does not have an id assigned to it in the schema.") from ke
                    else:
                        try:
                            row.append("'" +str(nest_obj[value_name])+ "'")
                        except KeyError as ke:
                            raise KeyError(f"No parameter with name {value_name} exist on json-object provided. {nest_obj}") from ke
                l.append(", ".join(row))
        except KeyError as ke:
            raise Exception("The SQL_handler schema does not agree with the table schema and/or json-object. See earlier exceptions for further hints.") from ke
        s = "(" + "), (".join(l) + ")"    
        return s

    def __build_value_name_str__(self,table):
        value_names = self.schema[table]["collumns"]
        s = "(" + ", ".join(value_names) + ")"
        return s
    
    def generic_command(self,command,table,jobj):
        valuenames = self.__build_value_name_str__(table)
        values = self.__build_value_str__(table,jobj)
        commandStr = command.upper() + " INTO " + table + " " + valuenames + " VALUES " + values +";"

        self.cur.execute(commandStr,values)
        self.con.commit()
        
        return commandStr

    def terminate_connection(self):
        self.cur.close()
        self.con.close()
        return

def main():
    #sql = SQL_handler()
    #sql.terminate_connection()
    pass

if __name__ == "__main__":
    main()



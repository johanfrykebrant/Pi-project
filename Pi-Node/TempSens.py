import os
import glob
from datetime import datetime
import json
import logging

class Sensor():
    def __logg_or_raise__(self, error_string):
        pass

    def __init_logger__(self):
        logging.basicConfig(level = self.config["logging"]["level"], filename = self.config["logging"]["filename"],
                              format = "%(asctime)s | %(name)s | %(levelname)s | %(funcName)s | %(message)s")
        self.logger = logging.getLogger(__name__)
    
    def __init__(self):
        os.system('sudo modprobe w1-gpio')
        os.system('sudo modprobe w1-therm')
        self.logging = False
        try:
            with open(".config") as json_data_file:
                self.config = json.load(json_data_file)
            self.__init_logger__()
            self.logging = True
        except FileNotFoundError:
            print("WARNING: Config file not found. Logging and error handling disabled")
         
        self.device_files = []
        base_dir = '/sys/bus/w1/devices/'
        self.sensors = glob.glob(base_dir + '28*')

        if len(self.sensors) == 0:
            error_string = "Unable to read temperature. No sensor found."
            if self.logging:
                self.logger.error(error_string)
            else:
                raise Exception(error_string)
        else:
            for i in range(len(self.sensors)):
                self.device_files.append(glob.glob(base_dir + '28*')[i] + '/w1_slave')

    def read_sens_lines(self):
        self.lines = []
        for i in range(len(self.device_files)):
            f = open(self.device_files[i], 'r')
            self.lines.append(f.readlines())
            f.close()
     
    def read_temp(self):
        result_dict = {"Sensor values" : []}
        self.read_sens_lines()
        for i in range(len(self.lines)):
            line = self.lines[i]
            temp_c = None
            temp_dict ={ 
              "name" : "Temperature",
              "timestamp" : None,
              "value" : None,
              "parameter_key" : i+1,
              "unit" : "degC"
              }
            
            while line[0].strip()[-3:] != 'YES':
                time.sleep(0.2)
                self.read_sens_lines()
            
            equals_pos = line[1].find('t=')
            if equals_pos != -1:
                temp_string = line[1][equals_pos+2:]
                temp_c = float(temp_string) / 1000.0
            else:
                error_string = "Sensors found but unable to read value."
                if self.logging:
                    self.logger.error(error_string)
                else:
                    raise Exception(error_string)
            temp_dict["value"] = temp_c
            temp_dict["timestamp"] = datetime.now()
            result_dict["Sensor values"].append(temp_dict)    
            
        return result_dict

def main():
    s = Sensor()
    t = s.read_temp()
    print(t)
    
if __name__ == "__main__":
    main()

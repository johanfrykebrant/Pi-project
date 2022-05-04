from socket import gaierror
from urllib3.exceptions import MaxRetryError, NewConnectionError
import requests
import json
import logging
from datetime import datetime

class SmhiApi:
    """
    https://opendata.smhi.se/apidocs/metobs
    https://opendata.smhi.se/apidocs/metfcst
    """
    def __init__(self):
      with open(r"Pi-Server\.config") as json_data_file:
        config = json.load(json_data_file)
      
      logging.basicConfig(level = config["logging"]["level"], filename = config["logging"]["filename"],
                          format = "%(asctime)s | %(name)s | %(levelname)s | %(funcName)s | %(message)s")
      self.logger = logging.getLogger(__name__)
      
      """
      ~Station~
      Malmö = 52350
      GET /api/version/{version}/parameter/{parameter}/station/52350/period/{period}/data.json
      """
      self.longitude = '13.07'
      self.latitude = '55.6'
      self.SMHI_FORECAST = "https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/" + self.longitude + "/lat/" + self.latitude + "/data.json"
      self.SMHI_OBSERVATION = "https://opendata-download-metobs.smhi.se/api/version/latest/parameter/<parameter>/station/52350/period/latest-hour/data.json"
      self.NAME_CODES ={
            'msl':	'Air pressure',
            't':	'Air temperature',
            'vis': 'Horizontal visibility',
            'wd': 'Wind direction',
            'ws': 'Wind speed',
            'r':	'Relative humidity',
            'tstm': 'Thunder probability',
            'tcc_mean':	'Mean value of total cloud cover',
            'lcc_mean':	'Mean value of low level cloud cover',
            'mcc_mean':	'Mean value of medium level cloud cover',
            'hcc_mean':	'Mean value of high level',
            'gust': 'Wind gust speed',
            'pmin':	'Minimum precipitation intensity',
            'pmax':	'Maximum precipitation intensity',
            'spp':	'Percent of precipitation in frozen form',
            'pcat':	'Precipitation category',
            'pmean':	'Mean precipitation intensity',
            'pmedian':	'Median precipitation intensity',
            'Wsymb2':	'Weather symbol'
            }
 
    def __epoch_to_date(self,jobj):
        d = jobj["value"][0]['date']/1000
        t = datetime.fromtimestamp(d).strftime('%Y-%m-%d %H:%M:%S')
        return t

    def __date_str_format(self,string):
        dateStr = string[1:11] + ' ' + string[12:20]
        #t = datetime.strptime(dateStr, '%Y-%m-%d %H:%M:%S')
        return dateStr

    def get_all_measurements(self):
      result_dict = {"Observations" : []}
      parameters = [1,3,4,6,7,12,13,14,21,25]
      
      for param in parameters:
        url = self.SMHI_OBSERVATION.replace("<parameter>",str(param))
        temp_dict ={ 
            "name" : None,
            "timestamp" : None,
            "value" : None,
            "parameter_key" : None,
            "unit" : None
            }

        try:
          r = requests.get(url)
        except (requests.exceptions.ConnectionError, NewConnectionError, gaierror, MaxRetryError):
          self.logger.critical("Failed GET request. Could not establish connection. Ensure that device has internet acecss")
          return None

        if r.status_code == 200: 
          jobj = r.json()
          temp_dict["timestamp"] = self.__epoch_to_date(jobj)
          temp_dict["value"] = jobj["value"][0]["value"]
          temp_dict["parameter_key"] = jobj["parameter"]["key"]
          temp_dict["name"] = jobj["parameter"]["name"]
          temp_dict["unit"] = jobj["parameter"]["unit"]
          
          result_dict["Observations"].append(temp_dict)
        else:
          self.logger.error(f"GET from url {url} returned status code {r.status_code}")
          return None

      n = len(result_dict["Observations"])
      self.logger.info(f"Returned {n} parameters")
      return result_dict

    def get_all_forecasts(self,hours_in_future = [24,48]):
      result_dict = {"Forecasts" : []}

      try:
        r = requests.get(self.SMHI_FORECAST)
      except (requests.exceptions.ConnectionError, NewConnectionError, gaierror, MaxRetryError):
        self.logger.critical("Failed GET request. Could not establish connection. Ensure that device has internet acecss")
        return None

      if r.status_code == 200: 
        jobj = r.json()
        for hrs in hours_in_future:
          time = self.__date_str_format(json.dumps(jobj["timeSeries"][hrs]["validTime"]))

          for i in jobj["timeSeries"][hrs]["parameters"]:
            temp_dict ={ 
              "name" : None,
              "timestamp" : time,
              "value" : None,
              "parameter_key" : None,
              "unit" : None
              }

            temp_dict["name"] = self.NAME_CODES[i["name"]]
            temp_dict["unit"] = i["unit"]
            temp_dict["value"] = i["values"][0]
            result_dict["Forecasts"].append(temp_dict)
      else:
        self.logger.error(f"GET from url {self.SMHI_FORECAST} returned status code {r.status_code}")
        return None
      
      n = len(result_dict["Forecasts"])
      self.logger.info(f"Returned {n} parameters")
      return result_dict

def main():
  api = SmhiApi()
  r = api.get_all_forecasts(hours_in_future=[24,48])
  s = json.dumps(r,indent = 2, ensure_ascii=False)
  print(s)

if __name__ == "__main__":
    main()





from socket import gaierror
from urllib3.exceptions import MaxRetryError, NewConnectionError
import requests
import json
import logging
from datetime import datetime
from os import chdir, getcwd
from os.path import dirname, join

class SmhiApi:
    """
    See links for information on the APIs called in this class
    https://opendata.smhi.se/apidocs/metobs
    https://opendata.smhi.se/apidocs/metfcst
    """
    def __init__(self):
      dir = dirname(__file__)
      chdir(dir)
      chdir('..')
      dir = getcwd()
      file_path = join(dir, ".config") 
      with open(file_path) as json_data_file:
        config = json.load(json_data_file)
      
      logging.basicConfig(level = config["logging"]["level"], filename = config["logging"]["filename"],
                          format = config["logging"]["format"])
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
            'msl': 'Air pressure',
            't': 'Air temperature',
            'vis': 'Horizontal visibility',
            'wd': 'Wind direction',
            'ws': 'Wind speed',
            'r': 'Relative humidity',
            'tstm': 'Thunder probability',
            'tcc_mean': 'Mean value of total cloud cover',
            'lcc_mean': 'Mean value of low level cloud cover',
            'mcc_mean': 'Mean value of medium level cloud cover',
            'hcc_mean': 'Mean value of high level',
            'gust': 'Wind gust speed',
            'pmin': 'Minimum precipitation intensity',
            'pmax': 'Maximum precipitation intensity',
            'spp': 'Percent of precipitation in frozen form',
            'pcat': 'Precipitation category',
            'pmean': 'Mean precipitation intensity',
            'pmedian': 'Median precipitation intensity',
            'Wsymb2': 'Weather symbol',
            }
    @staticmethod
    def epoch_to_date(jobj):
        d = jobj["value"][0]['date']/1000
        dateStr = datetime.fromtimestamp(d).strftime('%Y-%m-%d %H:%M:%S')
        return dateStr
    @staticmethod
    def date_str_format(string):
        dateStr = string[1:11] + ' ' + string[12:20]
        return dateStr

    def get_all_observations(self):
      result_dict = []
      parameters = [1,3,4,6,7,12,13,21,25]
      
      for param in parameters:
        url = self.SMHI_OBSERVATION.replace("<parameter>",str(param))
        temp_dict ={ 
            "name" : None,
            "timestamp" : None,
            "value" : None,
            "unit" : None
            }

        try:
          r = requests.get(url)
        except (requests.exceptions.ConnectionError, NewConnectionError, gaierror, MaxRetryError):
          self.logger.critical("Failed GET request. Could not establish connection. Ensure that device has internet acecss")
          return None

        if r.status_code == 200: 
          jobj = r.json()
          temp_dict["timestamp"] = self.epoch_to_date(jobj)
          temp_dict["value"] = jobj["value"][0]["value"]
          temp_dict["name"] = jobj["parameter"]["name"]
          temp_dict["unit"] = jobj["parameter"]["unit"]
          
          result_dict.append(temp_dict)
          self.logger.info(f"{r.request.method} request from {r.url} returned <Response{r.status_code}>")
        else:
          self.logger.error(f"{r.request.method} request from {r.url} returned <Response{r.status_code}>")
          return None
      return result_dict

    def get_forecasts_hours_in_future(self,hours_in_future = [24,48]):
      try:
        r = requests.get(self.SMHI_FORECAST)
      except (requests.exceptions.ConnectionError, NewConnectionError, gaierror, MaxRetryError):
        self.logger.critical("Failed GET request. Could not establish connection. Ensure that device has internet acecss")
        return None

      result_dict = []
      if r.status_code == 200:
        self.logger.info(f"{r.request.method} request from {r.url} returned <Response{r.status_code}>") 
        jobj = r.json()
        for hrs in hours_in_future:
          time = self.date_str_format(json.dumps(jobj["timeSeries"][hrs + 1]["validTime"]))

          for i in jobj["timeSeries"][hrs + 1]["parameters"]:
            temp_dict ={ 
              "name" : self.NAME_CODES[i["name"]],
              "timestamp": time,
              "value" : i["values"][0],
              "hours_in_future": hrs,
              "unit" : i["unit"]
              }
            result_dict.append(temp_dict)
      else:
        self.logger.error(f"{r.request.method} request from {r.url} returned <Response{r.status_code}>")
        return None
      return result_dict


def main():
  api = SmhiApi()
  r = api.get_forecasts_hours_in_future(hours_in_future=[24])
  s = json.dumps(r,indent = 2, ensure_ascii=False)
  print(s)
  #print("--------------------------------------------------------------------------")
  #r = api.get_all_measurements()
  #s = json.dumps(r,indent = 2, ensure_ascii=False)
  #print(s)

if __name__ == "__main__":
    main()





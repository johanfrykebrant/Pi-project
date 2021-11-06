import requests
import json
from os.path import dirname, join
import matplotlib.pyplot as plt
from datetime import datetime


class TibberApi:

    HEADER = {"Authorization": "Bearer " + "6xJ8vXFR2YPsX7WyIQMVtBWauHh0lGkS-AogcZljTCE"}
    URL = 'https://api.tibber.com/v1-beta/gql'    
    CONSUMPTION = """{
          viewer {
            homes {
              consumption(resolution: HOURLY, last: 36) {
                nodes {
                  from
                  to
                  cost
                  consumption
                  consumptionUnit
                }
              }
            }
          }
        }"""
    PRICE = """
      {
        viewer {
          homes {
            currentSubscription {
                priceInfo {
                    tomorrow {
                        total
                        energy
                        tax
                        startsAt
                        }
              }
            }
          }
        }
      }
      """
          
    def __init__(self):
        pass

    def run_query(self,query): # A simple function to use requests.post to make the API call.
      request = requests.post(self.URL, json={'query': query}, headers=self.HEADER)
          
      if request.status_code == 200:
        return request.json()
      else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

    def StrToDate(self,string):
      dateStr = string[0:10] + ' ' + string[11:19]
      t = datetime.strptime(dateStr, '%Y-%m-%d %H:%M:%S')
      return t

    def get_prices_tomorrow(self):#Gets the energy prices for the next day and returns them in a list.
      q = self.run_query(self.PRICE)
      price_dict = q["data"]["viewer"]["homes"][0]["currentSubscription"]["priceInfo"]["tomorrow"]
      prices = []
      
      for x in price_dict:
        time = self.StrToDate(x['startsAt'])
        price = x['total']
        l = [time,price]
        prices.append([time,price])
      
      return prices

    def get_consumption(self):
      response = self.run_query(self.CONSUMPTION)
      consumption_dict = response["data"]["viewer"]["homes"][0]["consumption"]["nodes"]
      #print(json.dumps(consumption_dict, indent=4))
      consumption = []
      
      for cons in consumption_dict:
          value = cons["consumption"]
          if not (value == None):
              time = self.StrToDate(str(cons["from"]))
              consumption.append([time,value])
        
      return consumption
    
class SmhiApi:
    """
    https://opendata.smhi.se/apidocs/metobs
    https://opendata.smhi.se/apidocs/metfcst

    ~Station~
    Malmö = 52350
    GET /api/version/{version}/parameter/{parameter}/station/52350/period/{period}/data.json
    """
    SMHI_TEMP_LATESTHOUR = "https://opendata-download-metobs.smhi.se/api/version/latest/parameter/1/station/52350/period/latest-hour/data.json"
    SMHI_RAIN_LATESTHOUR = "https://opendata-download-metobs.smhi.se/api/version/latest/parameter/7/station/52350/period/latest-hour/data.json"
    SMHI_FORECAST = "https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/13.07/lat/55.6/data.json"
    SMHI_WIND_DIRECTION_LATESTHOUR = "https://opendata-download-metobs.smhi.se/api/version/latest/parameter/3/station/52350/period/latest-hour/data.json"
    SMHI_WIND_LATESTHOUR = "https://opendata-download-metobs.smhi.se/api/version/latest/parameter/4/station/52350/period/latest-hour/data.json"
    SMHI_URL = "https://opendata-download-metobs.smhi.se/api/version/latest/parameter/"
    END_URL = "/station/52350/period/latest-hour/data.json"

    
    NAME_CODES ={
          'msl':	'Air pressure',
          't':	'Air temperature',
          'vis': 'Horizontal visibility',
          'wd': 'Wind direction',
          'ws': 'Wind speed	Decimal number',
          'r':	'Relative humidity',
          'tstm': 'Thunder probability',
          'tcc_mean':	'Mean value of total cloud cover',
          'lcc_mean':	'Mean value of low level cloud cover',
          'mcc_mean':	'Mean value of medium level cloud cover',
          'hcc_mean':	'Mean value of high level',
          'gust': 'Wind gust speed',
          'pmin':	'Minimum precipitation intensity',
          'pmax':	'Maximum precipitation intensity',
          'spp':		'Percent of precipitation in frozen form',	
          'pcat':	'Precipitation category',	
          'pmean':	'Mean precipitation intensity',	
          'pmedian':	'Median precipitation intensity',
          'Wsymb2':	'Weather symbol'
          }
    def __init__(self):
        pass
 
    def __epoch_to_date(self,jobj):
        d = jobj["value"][0]['date']/1000
        t = datetime.fromtimestamp(d).strftime('%Y-%m-%d %H:%M:%S')
        return t

    def __str_to_date(self,string):
        dateStr = string[1:11] + ' ' + string[12:20]
        t = datetime.strptime(dateStr, '%Y-%m-%d %H:%M:%S')
        return t

    def get_all_measurements(self):
      url = ""
      # [time , name , value ]
      result = list()
      nbr_of_parameters = 26
      for nbr in range(1,nbr_of_parameters):
        
        url = self.SMHI_URL + str(nbr) + self.END_URL
        r = requests.get(url)
        
        if not(r.status_code == 404): 
          jobj = r.json()
          time = self.__epoch_to_date(jobj)
          value = jobj["value"][0]["value"]
          name = jobj["parameter"]["name"]
          result.append([time,name,value])
      
      return result

    def get_all_forecasts(self):
      response = requests.get(self.SMHI_FORECAST)
      jobj = response.json()
      result= list()
      hours_in_future = 24
      time = self.__str_to_date(json.dumps(jobj["timeSeries"][hours_in_future]["validTime"]))

      for i in jobj["timeSeries"][24]["parameters"]:
        name = self.NAME_CODES[i["name"]]
        unit = i["unit"]
        value = i["values"][0]
        print([time,name,value,unit])
        result.append([time,name,value,unit])

      return result

def main():
  api = SmhiApi()
  api.get_all_forecasts()

if __name__ == "__main__":
    main()





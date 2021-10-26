import requests
import json
from os.path import dirname, join
from datetime import datetime


class TibberApi:
    current_dir = dirname(__file__)
    file_path = join(current_dir, "./.config")

    with open(file_path) as json_data_file:
        data = json.load(json_data_file)

    HEADER = {"Authorization": "Bearer " + data["API keys"]["Tibber"]}
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

    ~Parameter~
    1 = Lufttemperatur
    2 = Lufttemperatur
    4 = Vindriktning
    3 = Vindhastighet
    6 = Relativ Luftfuktighet
    7 = Nederbördsmängd

    """
    SMHI_TEMP_LATESTHOUR = "https://opendata-download-metobs.smhi.se/api/version/latest/parameter/1/station/52350/period/latest-hour/data.json"
    SMHI_RAIN_LATESTHOUR = "https://opendata-download-metobs.smhi.se/api/version/latest/parameter/7/station/52350/period/latest-hour/data.json"
    SMHI_FORECAST = "https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/13.07/lat/55.6/data.json"
    SMHI_WIND_DIRECTION_LATESTHOUR = "https://opendata-download-metobs.smhi.se/api/version/latest/parameter/3/station/52350/period/latest-hour/data.json"
    SMHI_WIND_LATESTHOUR = "https://opendata-download-metobs.smhi.se/api/version/latest/parameter/4/station/52350/period/latest-hour/data.json"
    SMHI_TEST = "https://opendata-download-metobs.smhi.se/api/version/latest/"
    
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
    
    def __find_param(self,param_list,param):
        res = None
        for sub in param_list:
            if sub['name'] == param:
                res = sub
                break

        return res['values']

    def get_rain(self):
        response = requests.get(self.SMHI_RAIN_LATESTHOUR)
        jobj = response.json()

        time = self.__epoch_to_date(jobj)
        value = jobj["value"][0]['value']
        return [time, value]

    def get_temp(self):
        response = requests.get(self.SMHI_TEMP_LATESTHOUR)
        jobj = response.json()

        time = self.__epoch_to_date(jobj)
        value = jobj["value"][0]['value']
        return [time, value]
    
    def get_wind(self):
        response = requests.get(self.SMHI_WIND_LATESTHOUR)
        jobj = response.json()
        time = self.__epoch_to_date(jobj)
        value = jobj["value"][0]['value']
        return [time, value]
    
    def get_wind_direction(self):
        response = requests.get(self.SMHI_WIND_DIRECTION_LATESTHOUR)
        jobj = response.json()

        time = self.__epoch_to_date(jobj)
        value = jobj["value"][0]['value']
        return [time, value]
    
    def get_perc_forecast(self,nbr):
        HoursInFuture = nbr
        Categories = ["No percipitation", "Snow", "Snow and rain", "Rain", "Drizzle", "Freezing rain", "Freezing drizzle"]
        
        response = requests.get(self.SMHI_FORECAST)
        jobj = response.json()
        
        ValidTime = self.__str_to_date(json.dumps(jobj["timeSeries"][HoursInFuture]["validTime"]))
        param_list = jobj["timeSeries"][HoursInFuture]["parameters"]
        PercentFrozen = self.__find_param(param_list,'spp')[0]
        #If no frozen percipitation PercentFrozen will be -9
        if PercentFrozen == -9:
            PercentFrozen = 0
        
        PercCat = self.__find_param(param_list,'pcat')[0]
        PercCat = Categories[int(PercCat)]
        Pmin = self.__find_param(param_list,'pmin')[0]
        Pmean = self.__find_param(param_list,'pmean')[0]
        Pmax = self.__find_param(param_list,'pmax')[0]

        return [ValidTime, Pmin, Pmean, Pmax, PercCat, PercentFrozen]
        
    def get_temp_forecast(self,nbr):
        HoursInFuture = nbr
        response = requests.get(self.SMHI_FORECAST)
        jobj = response.json()
        param_list = jobj["timeSeries"][HoursInFuture]["parameters"]

        Temp = self.__find_param(param_list,'t')[0]
        ValidTime = self.__str_to_date(json.dumps(jobj["timeSeries"][HoursInFuture]["validTime"]))

        return [ValidTime, Temp]
    
    def get_test(self):
        response = requests.get(self.SMHI_TEST)
        jobj = response.json()
        print(jobj)
    
def main():
    api = SmhiApi()
    api.get_test()


if __name__ == "__main__":
    main()





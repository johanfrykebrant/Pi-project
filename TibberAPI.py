import requests
import json
from os.path import dirname, join
import TibberQueries as queries
from datetime import datetime

def run_query(query): # A simple function to use requests.post to make the API call.
  request = requests.post(queries.url(), json={'query': query}, headers=queries.header())
  
  if request.status_code == 200:
      return request.json()
  else:
      raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

def StrToDate(string):
  dateStr = string[0:10] + ' ' + string[11:19]
  t = datetime.strptime(dateStr, '%Y-%m-%d %H:%M:%S')
  return t

def get_prices_tomorrow():#Gets the energy prices for the next day and returns them in a list.
  q = run_query(queries.price())
  priceDict = q["data"]["viewer"]["homes"][0]["currentSubscription"]["priceInfo"]["tomorrow"]
  prices = []
  
  for x in priceDict:
    time = StrToDate(x['startsAt'])
    price = x['total']
    l = [time,price]
    prices.append([time,price])
  
  return prices

def get_consumption():#Gets the energy consumption of the latest hour and returns it
  q = run_query(queries.consumption())
  time = StrToDate(str(q["data"]["viewer"]["homes"][0]["consumption"]["nodes"][0]["from"]))
  cons = q["data"]["viewer"]["homes"][0]["consumption"]["nodes"][0]["consumption"]
  
  if cons == None:
    cons = 0.00

  return [time, cons]
import json
from os.path import dirname, join
# Defining graphQL queries and attributes to save space in main code  
current_dir = dirname(__file__)
file_path = join(current_dir, "./test.config")

with open(file_path) as json_data_file:
    data = json.load(json_data_file)

def header():
  return {"Authorization": "Bearer " + data["API keys"]["Tibber"]}

def url():
  return 'https://api.tibber.com/v1-beta/gql'    

def consumption():
    c = """
    {
      viewer {
        homes {
          consumption(resolution: HOURLY, last: 1) {
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
    }
    """
    return c

def price():
  p = """
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
  return p
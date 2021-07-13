# Projects




 ________________________________
|  Scripts in this box are       |
|  scheduled to run once every   |
|  hour using crontab.           |                   ________                      ___________________________________________________      
|                                |                  |        |                     |                                                  |
|   WeatherDataCollector.py      | <--------------->| API.py | <-----------------> | https://opendata-download-metobs.smhi.se/api/... |
|   WeatherForecastCollector.py  |                  |________|   GET data via API  | https://opendata-download-metfcst.smhi.se/api/...|
|________________________________|                                                 |__________________________________________________|
            |
            | writing data
            | to database
            |
            v
    ____________________   
   |                    |
   |   MySQL database   | <--------------->
   |____________________| 

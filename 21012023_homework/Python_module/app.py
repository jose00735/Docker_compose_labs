# import the module
import python_weather
import asyncio
import os
import time
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

async def getweather():
  # declare the client. format defaults to the metric system (celcius, km/h, etc.)
  async with python_weather.Client(format=python_weather.IMPERIAL) as client:

    # fetch a weather forecast from a city
    weather = await client.get("Bogota")
    
    return weather.current.temperature, weather.current.humidity
    # returns the current day's forecast temperature (int)
    while(True):
        print(weather.current.humidity)
        print(round((weather.current.temperature-32)/1.8))
        time.sleep(5)

if __name__ == "__main__":
  # see https://stackoverflow.com/questions/45600579/asyncio-event-loop-is-closed-when-getting-loop
  # for more details
  if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  
  
  token = "tXn46DM2uhDNzfO_CP7rSRjUxqWf9LViCMAQ2obFUF84ZSFNBjqJYQe6Rs5M7KJYpGX6rhFQlyQNpOE5lb-6dQ=="
  bucket = "bucket"
  client = InfluxDBClient(url="http://172.17.0.2:8086", token=token, org="org")

  write_api = client.write_api(write_options=SYNCHRONOUS) 
  query_api = client.query_api()

  while(True):        
    temp, hum = asyncio.run(getweather())
    p = Point("my_measurement").tag("location", "Bogota").field("temperature", temp)
    write_api.write(bucket=bucket, record=p)
    p = Point("my_measurement").tag("location", "Bogota").field("humedad", hum)
    write_api.write(bucket=bucket, record=p)
    time.sleep(5)

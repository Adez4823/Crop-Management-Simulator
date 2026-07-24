import requests
import os
OPENWEATHER_API_KEY = os.environ["OPENWEATHER_API_KEY"]

def get_weather_rates(city):
    """
    Updates the moisture_decay_rate global variable based off of the weather of Seattle

    Later this function will be changed to be the weather of the user's location
    
    returns:
        float: The float representing the moisture_decay_rate

    """

    geo_url = "https://api.openweathermap.org/geo/1.0/direct"

    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY
    }

    geo_data_response = requests.get(geo_url, params=params)
    geo_data = geo_data_response.json()

    latitude = geo_data[0]["lat"]
    longitude = geo_data[0]["lon"]

    weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={OPENWEATHER_API_KEY}"

    weather_response = requests.get(weather_url)

    weather_data = weather_response.json()

    temp = weather_data["main"]["temp"]

    fahrenheit = (temp - 273.15) * (9/5) + 32

    if fahrenheit > 95.0:
        print("Weather is too hot! Moisture decay rate is 0.1")
        return 0.1
    elif fahrenheit > 80 and fahrenheit < 90:
        print("Weather is mild. Moisture decay rate is 0.05")
        return 0.05
    else:
        print("Weather is cool. Moisture decay rate is 0.0")
        return 0.0
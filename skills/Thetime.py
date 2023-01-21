from datetime import datetime
import requests
import re, os
import json
from utils.speak import say_text
from skills.Skill import Skill
import typing
import logging
from utils.config import open_config
from utils.time_utils import DAYS_OF_WEEK
import dateparser
from dateparser_data.settings import default_parsers

logger = logging.getLogger(__name__)


class Thetime(Skill):

    KEY = os.getenv("WEATHER_KEY")
    URL = "https://api.weatherapi.com/v1/"
    BASE_PATH_FORECAST = f"forecast.json?key={KEY}&q=Berlin"
    BASE_PATH_CURRENT = f"current.json?key={KEY}&q=Berlin&aqi=no"

    THE_TIME = r"((qué)|(que) hora es)|(dime (la)? hora)"
    FORECAST_NEXT_2_DAY = "pronóstico"
    PATTERN_FORECAST_HOURS = r"pronóstico (.*)"
    WEATHER_NOW = r"(cuál es el clima)|(clima)"

    def __init__(self, name: str) -> None:
        super().__init__(name)
        with open(open_config()["base_dir"] + "/conditions.json", 'r') as f:
            self.__conditions = json.loads(f.read())
            self.__settings = { #TODO: pack to timeutils
                "DEFAULT_LANGUAGES": ["es"],
                "PREFER_DATES_FROM": "future"
            }

    def __get_condition_es(self, weather_condition_code:str) -> str:
        for condition in self.__conditions:
            if weather_condition_code == condition['code']:
                for language in condition['languages']:
                    if language['lang_iso'] == 'es':
                        return language["day_text"]
        return ""

    def __will_it_rain_or_snow(self, rain: int, snow: int) -> None:
        if rain:
            say_text("Es muy probable que llueva")
        if snow:
            say_text("Es muy probable que neve")
        if not rain:
            say_text("No es probable que llueva")
        if not snow:
            say_text("No es probable que neve")

    def __combine_days(self, weather_json_response: dict) -> list:
        hours_1_day = weather_json_response['forecast']['forecastday'][0]['hour']
        hours_2_day = weather_json_response['forecast']['forecastday'][1]['hour']
        hours_3_day = weather_json_response['forecast']['forecastday'][2]['hour']
        hours_1_day.extend(hours_2_day)
        hours_1_day.extend(hours_3_day)
        return hours_1_day

    def __look_up_forecast(self, hours: list, epoch: int) -> dict:
        for hour in hours:
            if epoch - hour['time_epoch'] >= 0 and epoch - hour['time_epoch'] < 3600:
                return hour

    def trigger(self, transcript: str) -> typing.Tuple[bool, str]:
        if re.match(Thetime.THE_TIME, transcript):
            now = datetime.now()
            hour = now.hour
            minute = now.minute
            say_text(f'La hora es {hour} con {minute}')
            return True, Thetime.THE_TIME
        elif re.match(Thetime.WEATHER_NOW, transcript):
            weather_url_today = Thetime.URL + Thetime.BASE_PATH_CURRENT
            response = requests.request("GET", weather_url_today)
            response = response.json()
            weather_condition_code = response['current']['condition']['code']
            say_text(f'La sensación de temperatura es {response["current"]["feelslike_c"]} y la real es {response["current"]["temp_c"]}. {self.__get_condition_es(weather_condition_code)}') 
            return True, Thetime.WEATHER_NOW
        elif transcript ==  Thetime.FORECAST_NEXT_2_DAY:
            forecast_url = Thetime.URL + Thetime.BASE_PATH_FORECAST + "&days=4&aqi=no&alerts=no"
            response = requests.request("GET", forecast_url)
            response = response.json()
            forecasts = response['forecast']['forecastday']
            for i in range(1,3):
                forecast_day = forecasts[i]
                weekday = datetime.fromtimestamp(forecast_day['date_epoch']).weekday()
                day = DAYS_OF_WEEK[weekday]
                say_text(f'{day} con una máxima de {round(forecast_day["day"]["maxtemp_c"])} y mínima de {round(forecast_day["day"]["mintemp_c"])}, promedio de {round(forecast_day["day"]["avgtemp_c"])}')
                self.__will_it_rain_or_snow(forecast_day["day"]["daily_will_it_rain"], forecast_day["day"]["daily_will_it_snow"])
                weather_condition_code = forecast_day['day']['condition']['code']
                say_text(self.__get_condition_es(weather_condition_code))
            return True, Thetime.FORECAST_NEXT_2_DAY
        elif re.match(Thetime.PATTERN_FORECAST_HOURS, transcript):
            forecast_url = Thetime.URL + Thetime.BASE_PATH_FORECAST + "&days=3&aqi=no&alerts=no"
            response = requests.request("GET", forecast_url)
            response = response.json()
            forecast_query = re.match(Thetime.PATTERN_FORECAST_HOURS, transcript).group(1)
            forecast_epoch = dateparser.parse(forecast_query, settings=self.__settings)
            if forecast_epoch:
                forecast_epoch = int(forecast_epoch.timestamp())
                hours = self.__combine_days(response)
                forecast = self.__look_up_forecast(hours, forecast_epoch)
                if forecast == None:
                    say_text("Pronóstico fuera de rango")
                    return True, Thetime.PATTERN_FORECAST_HOURS
                weather_condition_code = forecast['condition']['code']
                say_text(f"Temperatura de {forecast['temp_c']} y {self.__get_condition_es(weather_condition_code)}")
                self.__will_it_rain_or_snow(forecast['will_it_rain'], forecast['will_it_snow'])
                logger.info(f"Forecast of {forecast}")
            else:
                say_text("No entendí el pronóstico")
            return True, Thetime.PATTERN_FORECAST_HOURS
        return False, transcript

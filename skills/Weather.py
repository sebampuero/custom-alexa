from datetime import datetime
import requests
import re, os
import json
from utils.speak import say_text
from skills.Skill import Skill
import typing
import logging
from utils.config import ConfigHandler
from utils.time_utils import DAYS_OF_WEEK
import dateparser
from dateparser_data.settings import default_parsers

logger = logging.getLogger(__name__)


class Weather(Skill):

    KEY = os.getenv("WEATHER_KEY")
    URL = "https://api.weatherapi.com/v1/"
    BASE_PATH_FORECAST = f"forecast.json?key={KEY}&q=Berlin"
    BASE_PATH_CURRENT = f"current.json?key={KEY}&q=Berlin&aqi=no"

    THE_TIME = "hora"
    FORECAST = "pronóstico"
    WEATHER_FUTURE_VERBS = ['será', 'ser', 'estar', 'estará']
    WEATHER = r".*(clima|tiempo).*"

    def __init__(self, name: str) -> None:
        super().__init__(name)
        with open(ConfigHandler().open_config()["base_dir"] + "/conditions.json", 'r') as f:
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

    def _forecast_weather(self, forecast_datetime: str):
        forecast_url = Weather.URL + Weather.BASE_PATH_FORECAST + "&days=3&aqi=no&alerts=no"
        response = requests.request("GET", forecast_url)
        response = response.json()
        forecast_epoch = dateparser.parse(forecast_datetime, settings=self.__settings)
        if forecast_epoch:
            forecast_epoch = int(forecast_epoch.timestamp())
            hours = self.__combine_days(response)
            forecast = self.__look_up_forecast(hours, forecast_epoch)
            if forecast == None:
                say_text("Pronóstico fuera de rango")
            weather_condition_code = forecast['condition']['code']
            say_text(f"Temperatura de {forecast['temp_c']} y {self.__get_condition_es(weather_condition_code)}")
            self.__will_it_rain_or_snow(forecast['will_it_rain'], forecast['will_it_snow'])
            logger.info(f"Forecast of {forecast}")
        else:
            say_text(f"No entendí la fecha del pronóstico {forecast_datetime}")

    def trigger(self, transcript: str, intent: dict) -> bool:
        if intent['WeatherKeyword'] == Weather.FORECAST:
            forecast_datetime = transcript.split(intent['WeatherKeyword'])[1].strip()
            if forecast_datetime == '':
                say_text("Tienes que darme una fecha a futuro no mayor a dos días.")
                return True
            self._forecast_weather(forecast_datetime)
            return True
        elif re.match(Weather.WEATHER, intent['WeatherKeyword']) and \
            intent['WeatherVerb'] in Weather.WEATHER_FUTURE_VERBS:
            forecast_datetime = transcript.split(intent['WeatherKeyword'])[1].strip()
            if forecast_datetime == '':
                say_text("Tienes que darme una fecha a futuro no mayor a dos días.")
                return True
            self._forecast_weather(forecast_datetime)
            return True
        elif intent['WeatherKeyword'] == Weather.THE_TIME:
            now = datetime.now()
            hour = now.hour
            minute = now.minute
            say_text(f'La hora es {hour} con {minute}')
            return True
        else:
            weather_url_today = Weather.URL + Weather.BASE_PATH_CURRENT
            response = requests.request("GET", weather_url_today)
            response = response.json()
            weather_condition_code = response['current']['condition']['code']
            say_text(f'La sensación de temperatura es {response["current"]["feelslike_c"]} y la real es {response["current"]["temp_c"]}. {self.__get_condition_es(weather_condition_code)}') 
            return True
        return False
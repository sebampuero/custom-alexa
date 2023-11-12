import json
import sys
from adapt.intent import IntentBuilder
from adapt.engine import IntentDeterminationEngine
from utils.config import ConfigHandler
import logging
import importlib

logger = logging.getLogger(__name__)

class IntentManager():

    BASE_DIR = ConfigHandler().open_config()['base_dir']

    intent_to_skill_map = {
        'DDGIntent': 'AskDDG',
        'BGIntent': 'BG',
        'ComputerIntent': 'Computer',
        'BulbIntent': 'Foquito',
        'GPTIntent': 'GPT',
        'HeaterIntent': 'Heater',
        'ReminderIntent': 'Reminder',
        'RGBLEDIntent': 'RGBLED',
        'WeatherIntent': 'Weather',
        'WeightIntent': 'WeightRegister'
    }

    turn_on_off_verbs = ['prende', 'prender', 'enciende', 'encender','apaga', 'apagar']

    def __init__(self):
        self.engine = IntentDeterminationEngine()
        self._init_intents()

    def execute_skill_by_intent(self, utterance: str):
        for intent in self.engine.determine_intent(utterance):
            if intent and intent.get('confidence') > 0:
                logger.info(f"Intent: {json.dumps(intent, indent=4)}")
                skill_to_invoke = self.intent_to_skill_map[intent['intent_type']]
                module_name = f"skills.{skill_to_invoke}"
                module = importlib.import_module(module_name)
                cls = getattr(module, skill_to_invoke)
                instance = cls(skill_to_invoke)
                logger.info(f"Going to invoke {skill_to_invoke}")
                return instance.trigger(utterance.lower(), intent)
        return False


    def _init_intents(self):
        ddg_keyword = ['internet']
        ddg_verbs = ['busca', 'buscar', 'averigua', 'averiguar']

        bg_keyword = ['azúcar']
        bg_verbs = ['dime', 'es', 'decir']
        bg_time = ['último']

        computer_keyword = ['computadora', 'compu', 'pc', 'computador', 'ordenador']
        computer_verbs = self.turn_on_off_verbs

        weather_keyword = ['clima', 'tiempo', 'pronóstico', 'hora']
        weather_verbs = ['dime', 'es', 'decir', 'ser', 'estar', 'será', 'estará', 'está']

        rgbled_keyword = ['luces', 'led']
        rgbled_verbs = ['pon', 'poner', 'configura', 'configurar', 'ajusta', 'ajustar'] + self.turn_on_off_verbs
        rgbled_colors = ['amarillo', 'azul', 'rojo', 'lila', 'verde']

        bulb_keyword = ['luz', 'foco']
        bulb_colors = ['blanco', 'amarillo', 'azul', 'rojo', 'lila', 'verde']
        bulb_color_temperature = ['temperatura']
        bulb_mode = ['modo']
        bulb_modes = ['dormir', 'estudio', 'estudiar']
        bulb_brightness = ['brillo', 'intensidad']
        bulb_verbs = ['pon', 'configura', 'poner', 'configurar'] + self.turn_on_off_verbs

        weight_keyword = ['peso']
        weights_verbs = ['registra', 'anota', 'registrar', 'anotar']
        weight_unit = ['kg', 'kilos']

        heater_keyword = ['calefactor', 'calefacción']
        heater_verbs = ['es', 'dime', 'decir', 'sido', 'pon', 'poner', 'configura', 'configurar', 'ajustar', 'ajusta', 'estado']
        heater_time = ['tiempo']
        heater_temperature = ['temperatura']
        heater_temperature_values = ['mínima', 'máxima']

        gpt_verbs = ['respóndeme', 'responde', 'dime', 'decir']

        reminder_keywords = ['recordatorio']
        reminder_verbs = ['recuérdame', 'hazme acordar', 'elimina', 'eliminar', 'es', 'será', 'borra', 'borrar']
        reminder_time = ['próximo', 'siguiente', 'último']
        for ddg in ddg_keyword:
            self.engine.register_entity(ddg, "DDGKeyword")
        for ddg in ddg_verbs:
            self.engine.register_entity(ddg, "DDGVerb")

        for bg in bg_keyword:
            self.engine.register_entity(bg, "BGKeyword")
        for bg in bg_verbs:
            self.engine.register_entity(bg, "BGVerb")
        for bg in bg_time:
            self.engine.register_entity(bg, "BGTime")

        for computer in computer_keyword:
            self.engine.register_entity(computer, "ComputerKeyword")
        for computer in computer_verbs:
            self.engine.register_entity(computer, "ComputerVerb")

        for weather in weather_keyword:
            self.engine.register_entity(weather, "WeatherKeyword")
        for weather in weather_verbs:
            self.engine.register_entity(weather, "WeatherVerb")

        for rgbled in rgbled_keyword:
            self.engine.register_entity(rgbled, "RGBLEDKeyword")
        for rgbled in rgbled_verbs:
            self.engine.register_entity(rgbled, "RGBLEDVerb")
        for rgbled in rgbled_colors:
            self.engine.register_entity(rgbled, "RGBLEDColor")

        for bulb in bulb_keyword:
            self.engine.register_entity(bulb, "BulbKeyword")
        for bulb in bulb_verbs:
            self.engine.register_entity(bulb, "BulbVerb")
        for bulb in bulb_colors:
            self.engine.register_entity(bulb, "BulbColor")
        for bulb in bulb_color_temperature:
            self.engine.register_entity(bulb, "BulbTemperature")
        for bulb in bulb_mode:
            self.engine.register_entity(bulb, "BulbMode")
        for bulb in bulb_modes:
           self.engine.register_entity(bulb, "BulbModes")
        for bulb in bulb_brightness:
           self.engine.register_entity(bulb, "BulbBrightness")
        

        for weight in weight_keyword:
            self.engine.register_entity(weight, "WeightKeyword")
        for weight in weights_verbs:
            self.engine.register_entity(weight, "WeightVerb")
        for weight in weight_unit:
            self.engine.register_entity(weight, "WeightUnit")

        for heater in heater_keyword:
            self.engine.register_entity(heater, "HeaterKeyword")
        for heater in heater_verbs:
            self.engine.register_entity(heater, "HeaterVerb")
        for heater in heater_time:
            self.engine.register_entity(heater, "HeaterTime")
        for heater in heater_temperature:
            self.engine.register_entity(heater, "HeaterTemperature")
        for heater in heater_temperature_values:
            self.engine.register_entity(heater, "HeaterTemperatureValues")

        for gpt in gpt_verbs:
            self.engine.register_entity(gpt, "GPTVerb")

        for reminder in reminder_keywords:
            self.engine.register_entity(reminder, "ReminderKeyword")
        for reminder in reminder_verbs:
            self.engine.register_entity(reminder, "ReminderVerb")
        for reminder in reminder_time:
            self.engine.register_entity(reminder, "ReminderTime")

        ddg_intent = IntentBuilder("DDGIntent")\
            .require("DDGKeyword")\
            .require("DDGVerb")\
            .build()
        bg_intent = IntentBuilder("BGIntent")\
            .require("BGKeyword")\
            .require("BGVerb")\
            .optionally("BGTime")\
            .build()
        computer_intent = IntentBuilder("ComputerIntent")\
                    .require("ComputerKeyword")\
                    .require("ComputerVerb")\
                    .build()
        weather_intent = IntentBuilder("WeatherIntent")\
                    .require("WeatherKeyword")\
                    .require("WeatherVerb")\
                    .build()
        rgbled_intent = IntentBuilder("RGBLEDIntent")\
                    .require("RGBLEDKeyword")\
                    .require("RGBLEDVerb")\
                    .optionally("RGBLEDColor")\
                    .build()
        bulb_intent = IntentBuilder("BulbIntent")\
                    .require("BulbKeyword")\
                    .require("BulbVerb")\
                    .optionally('BulbColor')\
                    .optionally('BulbTemperature')\
                    .optionally('BulbMode')\
                    .optionally('BulbModes')\
                    .optionally('BulbBrightness')\
                    .build()
        weight_intent = IntentBuilder("WeightIntent")\
                    .require("WeightKeyword")\
                    .require("WeightVerb")\
                    .optionally("WeightUnit")\
                    .build()
        heater_intent = IntentBuilder("HeaterIntent")\
                    .require("HeaterKeyword")\
                    .require("HeaterVerb")\
                    .optionally("HeaterTime")\
                    .optionally("HeaterTemperature")\
                    .optionally("HeaterTemperatureValues")\
                    .build()
        gpt_intent = IntentBuilder("GPTIntent")\
                    .require("GPTVerb")\
                    .build()
        reminder_intent = IntentBuilder("ReminderIntent")\
                    .optionally("ReminderKeyword")\
                    .require("ReminderVerb")\
                    .optionally("ReminderTime")\
                    .build()
        self.engine.register_intent_parser(ddg_intent)
        self.engine.register_intent_parser(bg_intent)
        self.engine.register_intent_parser(computer_intent)
        self.engine.register_intent_parser(weather_intent)
        self.engine.register_intent_parser(rgbled_intent)
        self.engine.register_intent_parser(bulb_intent)
        self.engine.register_intent_parser(weight_intent)
        self.engine.register_intent_parser(heater_intent)
        self.engine.register_intent_parser(gpt_intent)
        self.engine.register_intent_parser(reminder_intent)

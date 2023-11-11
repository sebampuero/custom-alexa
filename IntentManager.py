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
                return instance.trigger(utterance)


    def _init_intents(self):
        ddg_keyword = ['internet']
        ddg_verbs = ['busca', 'buscar', 'averigua', 'averiguar']
        bg_keyword = ['azúcar', 'último']
        bg_verbs = ['dime', 'es', 'decir']
        computer_keyword = ['computadora', 'compu', 'pc', 'computador', 'ordenador']
        computer_verbs = ['prende', 'prender', 'enciende', 'encender','apaga', 'apagar']
        weather_keyword = ['clima', 'tiempo', 'pronóstico']
        weather_verbs = ['dime', 'es', 'decir']
        rgbled_keyword = ['luces']
        rgbled_verbs = ['prende', 'prender', 'enciende', 'encender','apaga', 'apagar']
        bulb_keyword = ['luz', 'foco']
        bulb_verbs = ['prende', 'prender', 'enciende', 'encender','apaga', 'apagar']
        weight_keyword = ['peso']
        weights_verbs = ['registra', 'anota', 'registrar', 'anotar']
        heater_keyword = ['calefactor', 'calefacción']
        heater_verbs = ['es', 'dime', 'decir']
        gpt_verbs = ['respóndeme', 'responde']
        reminder_verbs = ['recuérdame', 'hazme acordar']
        for ddg in ddg_keyword:
            self.engine.register_entity(ddg, "DDGKeyword")
        for ddg in ddg_verbs:
            self.engine.register_entity(ddg, "DDGVerb")
        for bg in bg_keyword:
            self.engine.register_entity(bg, "BGKeyword")
        for bg in bg_verbs:
            self.engine.register_entity(bg, "BGVerb")
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
        for bulb in bulb_keyword:
            self.engine.register_entity(bulb, "BulbKeyword")
        for bulb in bulb_verbs:
            self.engine.register_entity(bulb, "BulbVerb")
        for weight in weight_keyword:
            self.engine.register_entity(weight, "WeightKeyword")
        for weight in weights_verbs:
            self.engine.register_entity(weight, "WeightVerb")
        for heater in heater_keyword:
            self.engine.register_entity(heater, "HeaterKeyword")
        for heater in heater_verbs:
            self.engine.register_entity(heater, "HeaterVerb")
        for gpt in gpt_verbs:
            self.engine.register_entity(gpt, "GPTVerb")
        for reminder in reminder_verbs:
            self.engine.register_entity(reminder, "ReminderVerb")
        ddg_intent = IntentBuilder("DDGIntent")\
            .require("DDGKeyword")\
            .require("DDGVerb")\
            .build()
        bg_intent = IntentBuilder("BGIntent")\
            .require("BGKeyword")\
            .require("BGVerb")\
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
                    .build()
        bulb_intent = IntentBuilder("BulbIntent")\
                    .require("BulbKeyword")\
                    .require("BulbVerb")\
                    .build()
        weight_intent = IntentBuilder("WeightIntent")\
                    .require("WeightKeyword")\
                    .require("WeightsVerb")\
                    .build()
        heater_intent = IntentBuilder("HeaterIntent")\
                    .require("HeaterKeyword")\
                    .require("HeaterVerb")\
                    .build()
        gpt_intent = IntentBuilder("GPTIntent")\
                    .require("GPTVerb")\
                    .build()
        reminder_intent = IntentBuilder("ReminderIntent")\
                    .require("ReminderVerb")\
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

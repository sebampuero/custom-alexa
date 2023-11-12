from skills.Skill import Skill
import typing
from utils.speak import say_text
from persistence.operations import *
from datetime import datetime
import re

class WeightRegister(Skill):

    def trigger(self, transcript: str, intent: dict) -> bool:
        weight = re.search(r'\d{2}((,| coma )\d{1,2})?', transcript).group(0) # search for 90,4 or 90 or 90 coma 4
        if "coma" or ',' in weight:
            weight = float(weight.replace(' coma ', '.').replace(',', '.'))
        today_time = datetime.today().strftime('%Y-%m-%d')
        last_entry_time = get_last_entry_time()
        if today_time == last_entry_time:
            say_text(f'Hoy ya has registrado peso, sobre escribiendo el último con {weight} kilos')
            delete_last()
            save_weight(weight)
            return True
        save_weight(weight)
        say_text(f'Registrando peso en {weight} kilos')
        last_7_entries = get_last_entries(7)
        if len(last_7_entries) == 7:
            last_week_entry = get_last_week_entry_time()
            if not last_week_entry:
                last_week_entry = save_last_week_entry_time(today_time)
            last_week_entry_timestamp = datetime.strptime(last_week_entry, "%Y-%m-%d").timestamp()
            today_timestamp = datetime.strptime(today_time, "%Y-%m-%d").timestamp()
            if today_timestamp - last_week_entry_timestamp >= 604800.0: # more than 7 days
                avg = sum([float(val) for val in last_7_entries]) / 7
                say_text(f"Promedio últimos 7 dias {round(avg, 2)} kilos")
                save_last_week_entry_time(today_time)
                save_weight_avg(str(round(avg, 2)))
                delete_key('weight') # delete list of weights
                return True
        save_last_entry_time(today_time)
        return True
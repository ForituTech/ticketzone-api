import json
from ast import literal_eval
from datetime import date
from json import JSONDecodeError

from core.utils import random_string


def generate_ticket_number() -> str:
    date_ = date.today()
    return f"tckt-{date_.year}{date_.month}{date_.day}-{random_string(6)}".upper()


def generate_event_number() -> str:
    date_ = date.today()
    return f"evnt-{date_.year}{date_.month}{date_.day}-{random_string(6)}".upper()


def pre_process_data(data: dict) -> dict:
    for key in data:
        if isinstance(data[key], str) and data[key][0] == "[":
            try:
                data[key] = json.loads(data[key])
            except JSONDecodeError:
                data[key] = literal_eval(data[key])
    return data

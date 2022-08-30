import json
from ast import literal_eval
from json import JSONDecodeError


def pre_process_data(data: dict) -> dict:
    for key in data:
        if isinstance(data[key], str) and data[key][0] == "[":
            try:
                data[key] = json.loads(data[key])
            except JSONDecodeError:
                data[key] = literal_eval(data[key])
    return data

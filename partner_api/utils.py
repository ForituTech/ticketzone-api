from datetime import date

from core.utils import random_string


def generate_resource_secret() -> str:
    date_ = date.today()
    return f"{date_.month}{random_string(6)}{date_.year}"

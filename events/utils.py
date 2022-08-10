from datetime import date

from core.utils import random_string


def generate_ticket_number() -> str:
    date_ = date.today()
    return f"tckt-{date_.year}{date_.month}{date_.day}-{random_string(6)}".upper()


def generate_event_number() -> str:
    date_ = date.today()
    return f"evnt-{date_.year}{date_.month}{date_.day}-{random_string(6)}".upper()

import hashlib

from partner.models import Person
from tickets.models import Ticket


def compute_ticket_hash(ticket: Ticket) -> str:
    if ticket.person:
        person: Person = ticket.person
    ticket_dict = ticket.__dict__.update(person.__dict__)
    str_to_be_hashed: str = ""
    for _, value in ticket_dict:
        str_to_be_hashed += str(value)

    return hashlib.md5(str_to_be_hashed.encode("UTF-8")).hexdigest()

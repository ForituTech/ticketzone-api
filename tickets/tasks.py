import hashlib

from partner.models import Person
from tickets.models import Ticket


def compute_ticket_hash(ticket: Ticket) -> str:
    person: Person = ticket.payment.person  # type: ignore
    ticket_dict = ticket.__dict__
    ticket_dict.update(person.__dict__)
    str_to_be_hashed: str = ""
    for value in ticket_dict:
        str_to_be_hashed += str(value)

    return hashlib.md5(str_to_be_hashed.encode("UTF-8")).hexdigest()

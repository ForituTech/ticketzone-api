import base64
import hashlib
import os
from datetime import datetime
from io import BytesIO
from tempfile import NamedTemporaryFile
from typing import Any, Union

import numpy as np
import pdfkit
import qrcode
from django.template.loader import render_to_string

from events.models import Event
from partner.models import Person
from tickets.models import Ticket

if os.environ.get("ENV") == "dev" or os.environ.get("GITHUB_WORKFLOW"):
    import cv2  # noqa


def compute_ticket_hash(ticket: Ticket) -> str:
    """
    Generate unique signature for tickets
    """
    person: Person = ticket.payment.person
    event: Event = ticket.ticket_type.event
    ticket_dict = ticket.__dict__
    ticket_dict.update(person.__dict__)
    ticket_dict.update(event.__dict__)
    ticket_dict.update({"now": datetime.now()})
    str_to_be_hashed: str = ""
    for value in ticket_dict:
        str_to_be_hashed += str(value)

    return hashlib.md5(str_to_be_hashed.encode("UTF-8")).hexdigest()


def generate_ticket_qr(ticket: Ticket) -> str:
    qr = qrcode.QRCode()
    qr.add_data(ticket.hash if ticket.hash else compute_ticket_hash(ticket))
    image = qr.make_image(fill="black")
    buffer: BytesIO = BytesIO()
    image.save(buffer, format="PNG")
    image_str: str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return image_str


def get_ticket_hash_from_qr(image_str: str) -> str:
    if os.environ.get("ENV") == "dev" or os.environ.get("GITHUB_WORKFLOW"):
        img_decoded: Union[str, bytes] = base64.b64decode(image_str)
        nparr = np.fromstring(img_decoded, np.uint8)  # type: ignore
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        qr_detector = cv2.QRCodeDetector()
        decoded_text, _, _ = qr_detector.detectAndDecode(image)
        return decoded_text
    else:
        raise EnvironmentError("Ticket hashes can only be decoded on dev")


def generate_ticket_pdf(ticket: Ticket) -> Any:
    date_obj = ticket.ticket_type.event.event_date
    date_str: str = datetime.strftime(date_obj, "%d-%B")
    date: list = date_str.split("-")
    image = generate_ticket_qr(ticket)
    poster_data = open(ticket.ticket_type.event.poster.url[1:], "rb")
    poster = base64.b64encode(poster_data.read()).decode("utf-8")

    ticket_html = render_to_string(
        "ticket.html",
        context={
            "date": date,
            "ticket_type": ticket.ticket_type,
            "image": image,
            "poster": poster,
        },
    )
    temp_file = NamedTemporaryFile(mode="w+b")
    ticket_pdf_data = pdfkit.from_string(ticket_html)
    temp_file.name = f"{ticket.__str__()}"
    temp_file.write(ticket_pdf_data)
    temp_file.seek(0)
    return temp_file


def generate_ticket_html(ticket: Ticket) -> str:
    date_obj = ticket.ticket_type.event.event_date
    date_str: str = datetime.strftime(date_obj, "%d-%B")
    date: list = date_str.split("-")
    image = generate_ticket_qr(ticket)
    poster_data = open(ticket.ticket_type.event.poster.url[1:], "rb")
    poster = base64.b64encode(poster_data.read()).decode("utf-8")

    return render_to_string(
        "ticket.html",
        context={
            "date": date,
            "ticket_type": ticket.ticket_type,
            "image": image,
            "poster": poster,
        },
    )

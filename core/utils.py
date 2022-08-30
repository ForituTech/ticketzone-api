import random
import string
from datetime import date
from typing import Generator, Type

from django.core.paginator import Paginator
from django.db.models.query import QuerySet
from rest_framework.serializers import Serializer


def random_string(len: int = 10) -> str:
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(len))


def generate_agent_number() -> str:
    date_ = date.today()
    return f"evnt-{date_.year}{date_.month}{date_.day}-{random_string(6)}".upper()


def generate_ticket_number() -> str:
    date_ = date.today()
    return f"tckt-{date_.year}{date_.month}{date_.day}-{random_string(6)}".upper()


def generate_event_number() -> str:
    date_ = date.today()
    return f"evnt-{date_.year}{date_.month}{date_.day}-{random_string(6)}".upper()


def _stream_model_data(
    *, queryset: QuerySet, serializer: Type[Serializer], chunk_size: int = 100
) -> Generator:
    # This util leverages djangos default pagintion class
    # to stream data, get_all will degrade when data
    # increases

    paged_queryset = Paginator(queryset, chunk_size)
    for page in paged_queryset.page_range:
        yield from serializer(paged_queryset.page(page).object_list, many=True).data

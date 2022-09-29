from datetime import datetime, timedelta
from http import HTTPStatus

from django.db import transaction
from django.db.models import Count
from django.db.models.functions import TruncDay
from django.db.models.query import QuerySet

from core.error_codes import ErrorCodes
from core.exceptions import HttpErrorException
from core.services import CRUDService
from events.services import event_service
from payments.constants import PaymentStates
from tickets.models import Ticket, TicketScan
from tickets.serializers import (
    TicketCreateSerializer,
    TicketScanCreateSerializer,
    TicketUpdateInnerSerializer,
)
from tickets.utils import compute_ticket_hash


class TicketService(
    CRUDService[Ticket, TicketCreateSerializer, TicketUpdateInnerSerializer]
):
    def on_post_create(self, obj: Ticket) -> None:
        hash = compute_ticket_hash(obj)
        try:
            Ticket.objects.get(hash=hash)
            self.on_post_create(obj)
        except Ticket.DoesNotExist:
            obj.hash = hash
            obj.save()

    def redeem(self, pk: str, agent_id: str) -> Ticket:
        try:
            ticket: Ticket = Ticket.objects.select_for_update().get(pk=pk)
        except Ticket.DoesNotExist:
            raise HttpErrorException(
                status_code=HTTPStatus.NOT_FOUND, code=ErrorCodes.INVALID_TICKET_ID
            )
        if ticket.payment.state != PaymentStates.PAID.value:
            raise HttpErrorException(
                status_code=HTTPStatus.FORBIDDEN,
                code=ErrorCodes.UNPAID_FOR_TICKET,
            )
        if ticket.ticket_type.use_limit <= ticket.uses:
            raise HttpErrorException(
                status_code=HTTPStatus.FORBIDDEN,
                code=ErrorCodes.REDEEMED_TICKET,
            )

        with transaction.atomic():
            ticket = Ticket.objects.select_for_update().get(pk=pk)
            ticket.uses += 1
            if ticket.uses >= ticket.ticket_type.use_limit:
                ticket.redeemed = True
            ticket.save()

        scans: QuerySet[TicketScan] = TicketScan.objects.filter(
            ticket_id=pk, agent_id=agent_id, redeem_triggered=False  # type: ignore
        )
        for scan in scans:
            scan.redeem_triggered = True
            scan.save()

        return ticket

    def counts_over_time(self, partner_id: str) -> QuerySet:
        last_week = datetime.today() - timedelta(days=7)
        return (
            Ticket.objects.all()
            .annotate(date=TruncDay("created_at"))
            .values("date")
            .annotate(count=Count("id"))
            .order_by("-date")
            .filter(ticket_type__event__partner_id=partner_id)
            .filter(created_at__gte=last_week)
        )

    def get_by_hash(self, hash: str, person_id: str, agent_id: str) -> Ticket:
        filters = {
            "hash": hash,
            "ticket_type__event__id__in": event_service.get_ta_assigned_events(
                person_id
            ),
        }
        try:
            ticket = ticket_service.get(**filters)
        except Ticket.MultipleObjectsReturned:
            raise HttpErrorException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                code=ErrorCodes.MULTIPLE_TICKETS_ONE_HASH,
            )
        if not ticket:
            raise HttpErrorException(
                status_code=HTTPStatus.NOT_FOUND,
                code=ErrorCodes.UNRESOLVABLE_HASH,
            )

        TicketScan.objects.create(agent_id=agent_id, ticket_id=str(ticket.id))
        return ticket

    def send(self, ticket: Ticket) -> bool:
        pass


ticket_service = TicketService(Ticket)


class TicketScansService(
    CRUDService[TicketScan, TicketScanCreateSerializer, TicketScanCreateSerializer]
):
    pass


ticket_scan_service = TicketScansService(TicketScan)

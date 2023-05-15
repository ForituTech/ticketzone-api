from typing import Any, Dict, List, Optional, Tuple, Union

from django.db.models.query import QuerySet
from rest_framework.request import Request

from core.error_codes import ErrorCodes
from core.exceptions import HttpErrorException, ObjectNotFoundException
from core.services import CRUDService
from eticketing_api import settings
from events.models import Event
from notifications.tasks import send_email
from partner.models import (
    Partner,
    PartnerPerson,
    PartnerPromotion,
    PartnerSMS,
    Person,
    PromoOptIn,
)
from partner.serializers import (
    PartnerPersonCreateSerializer,
    PartnerPersonUpdateSerializer,
    PartnerPromoCreateSerializer,
    PartnerPromoUpdateSerializer,
    PartnerSerializer,
    PartnerSMSPackageCreateSerializer,
    PartnerSMSPackageUpdateSerializer,
    PartnerUpdateSerializer,
    PasswordResetVerificationSerializer,
    PersonCreateSerializer,
    PersonUpdateSerializer,
    UserPasswordResetSerializer,
    UserSerializer,
)
from partner.utils import (
    create_access_token,
    create_otp,
    hash_password,
    random_password,
    verify_otp,
)
from tickets.models import Ticket


class PersonService(
    CRUDService[Person, PersonCreateSerializer, PersonUpdateSerializer]
):
    def on_pre_create(self, obj_in: Dict[str, Any]) -> None:
        if "hashed_password" in obj_in:
            obj_in["hashed_password"] = hash_password(obj_in["hashed_password"])

    def on_pre_update(self, obj_in: dict, obj: Person) -> None:
        if "hashed_password" in obj_in:
            obj_in["hashed_password"] = hash_password(obj_in["hashed_password"])

    def get_user_by_phonenumber(
        self, request: Request
    ) -> Tuple[Person, UserSerializer]:
        credential_error_exception = HttpErrorException(
            status_code=404,
            code=ErrorCodes.INVALID_CREDENTIALS,
        )
        user_in = UserSerializer(data=request.data)
        if not user_in.is_valid():
            raise credential_error_exception
        try:
            user = Person.objects.get(phone_number=user_in.data["phone_number"])
            partner = Partner.objects.filter(owner_id=user.id).first()
            if partner and not partner.verified:
                raise HttpErrorException(
                    status_code=400,
                    code=ErrorCodes.PARTNER_NOT_VERIFIED,
                )
        except Person.DoesNotExist:
            raise credential_error_exception
        except Person.MultipleObjectsReturned:
            raise credential_error_exception
        return (user, user_in)

    def get_by_phonenumber(self, request: Request) -> Person:
        credential_error_exception = HttpErrorException(
            status_code=404,
            code=ErrorCodes.INVALID_CREDENTIALS,
        )
        reset_payload = UserPasswordResetSerializer(data=request.data)
        if not reset_payload.is_valid():
            raise credential_error_exception
        try:
            user = Person.objects.get(phone_number=reset_payload.data["phone_number"])
        except Person.DoesNotExist:
            raise credential_error_exception
        except Person.MultipleObjectsReturned:
            raise credential_error_exception
        return user

    def reset_password(self, user: Person) -> str:
        otp, token = create_otp(user)
        send_email.apply_async(
            args=(
                user.id,
                "Ticketzone Account Support",
                f"Your ticketzone OTP is: {otp}",
            ),
            queue=settings.CELERY_NOTIFICATIONS_QUEUE,
        )
        return token

    def verify_otp(self, request: Request) -> str:
        credential_error_exception = HttpErrorException(
            status_code=400,
            code=ErrorCodes.INVALID_OTP,
        )
        otp_verification_payload = PasswordResetVerificationSerializer(
            data=request.data
        )
        if not otp_verification_payload.is_valid():
            raise credential_error_exception
        verification = verify_otp(
            str(otp_verification_payload.data["secret"]),
            str(otp_verification_payload.data["otp"]),
        )
        if not verification[0]:
            raise credential_error_exception

        user: Person = Person.objects.get(phone_number=verification[1])
        if "new_password" in otp_verification_payload.data:
            user.hashed_password = hash_password(
                otp_verification_payload.data["new_password"]
            )
            user.save()
        else:
            if partner := Partner.objects.get(owner_id=user.id):
                partner.verified = True
                partner.save()
            else:
                raise ObjectNotFoundException("Partner", user.id)

        return create_access_token(user)

    def get_or_create(self, person_data: Dict[str, Any]) -> Person:
        if phone := person_data.get("phone_number"):
            if person := Person.objects.filter(phone_number=phone).first():
                person.email = person_data.get("email") or person.email
                person.save()
                return person
        if "hashed_password" not in person_data:
            person_data["hashed_password"] = random_password()
        person = self.create(obj_data=person_data, serializer=PersonCreateSerializer)
        send_email.apply_async(
            args=(
                person.id,
                settings.POST_PARTNER_PERSON_CREATE_EMAIL_TITLE,
                settings.POST_PARTNER_PERSON_CREATE_EMAIL.format(
                    person.name,
                    person.phone_number,
                    person_data["hashed_password"],
                ),
            ),
            queue=settings.CELERY_NOTIFICATIONS_QUEUE,
        )

        return person


person_service = PersonService(Person)


class PartnerService(CRUDService[Partner, PartnerSerializer, PartnerUpdateSerializer]):
    def on_pre_create(self, obj_in: Dict[str, Any]) -> None:
        if person := obj_in.get("owner", None):
            obj_in["owner_id"] = str(
                person_service.create(
                    obj_data=person.copy(), serializer=PersonCreateSerializer
                ).id
            )
            del obj_in["owner"]

    def send_verification_email(self, partner: Partner) -> str:
        otp, token = create_otp(partner.owner)
        send_email.apply_async(
            args=(
                str(partner.owner.id),
                settings.POST_PARTNER_PERSON_CREATE_EMAIL_TITLE,
                settings.POST_PARTNER_PERSON_CREATE_EMAIL.format(
                    partner.owner.name, otp
                ),
            ),
            queue=settings.CELERY_NOTIFICATIONS_QUEUE,
        )
        return token

    def get_total_sales(self, partner_id: str) -> int:
        filters = {
            "ticket_type__event__partner_id": partner_id,
        }
        tickets: int = Ticket.objects.filter(**filters).count()
        return tickets

    def get_total_sales_revenue(self, partner_id: str) -> Dict[str, float]:
        filters = {
            "ticket_type__event__partner_id": partner_id,
        }
        tickets: QuerySet[Ticket] = Ticket.objects.filter(**filters).distinct()
        partner: Partner = Partner.objects.get(id=partner_id)
        sales_total = 0.0
        for ticket in tickets:
            sales_total += ticket.payment.amount

        expenses = 0.0
        try:
            sms: PartnerSMS = PartnerSMS.objects.get(partner_id=partner_id)
            sms_cost = sms.sms_used * sms.per_sms_rate
            expenses += sms_cost
        except PartnerSMS.DoesNotExist:
            pass
        return {
            "revenue": sales_total,
            "net": (100 - partner.comission_rate) / 100 * sales_total,
            "expenses": expenses,
        }

    def get_ranked_events_by_sales(self, partner_id: str) -> List[Event]:
        filters = {
            "partner_id": partner_id,
        }
        return sorted(
            Event.objects.filter(**filters), key=lambda event: (-1 * event.sales)
        )

    def get_total_redemtion_rate(self, partner_id: str) -> float:
        filters = {
            "partner_id": partner_id,
        }
        events: QuerySet[Event] = Event.objects.filter(**filters)
        try:
            return sum([event.redemption_rate for event in events]) / len(events)
        except ZeroDivisionError:
            return 0

    def add_promo_opt_in(self, partner_id: str, person_id: str) -> None:
        try:
            Partner.objects.get(id=partner_id)
        except Partner.DoesNotExist:
            raise ObjectNotFoundException("Partner", partner_id)
        try:
            Person.objects.get(id=person_id)
        except Person.DoesNotExist:
            raise ObjectNotFoundException("Person", person_id)
        PromoOptIn.objects.create(
            partner_id=partner_id,
            person_id=person_id,
        )

    def promo_optin_count(self, partner_id: str) -> int:
        return PromoOptIn.objects.filter(partner_id=partner_id).count()

    def balance(self, partner_id: str) -> float:
        ticket_filter = {
            "ticket_type__event__partner_id": partner_id,
            "payment__reconciled": False,
        }
        tickets: QuerySet[Ticket] = Ticket.objects.filter(**ticket_filter).distinct(
            "payment"
        )
        total_revenue = 0.0
        for ticket in tickets:
            total_revenue += ticket.payment.amount
            ticket.payment.reconciled = True
            ticket.payment.save()
        try:
            sms: PartnerSMS = PartnerSMS.objects.get(partner_id=partner_id)
            sms_cost = sms.sms_used * sms.per_sms_rate
            total_revenue -= sms_cost
        except PartnerSMS.DoesNotExist:
            pass
        return total_revenue


partner_service = PartnerService(Partner)


class PartnerPersonService(
    CRUDService[
        PartnerPerson, PartnerPersonCreateSerializer, PartnerPersonUpdateSerializer
    ]
):
    def on_pre_create(self, obj_in: Dict[str, Any]) -> None:
        if person := obj_in.get("person", None):
            obj_in["person_id"] = str(
                person_service.create(
                    obj_data=person.copy(), serializer=PersonCreateSerializer
                ).id
            )
            del obj_in["person"]

    def on_pre_update(self, obj_in: dict, obj: PartnerPerson) -> None:
        if person := obj_in.get("person", None):
            person_service.update(
                obj_data=person,
                serializer=PersonUpdateSerializer,
                obj_id=str(obj.person.id),
            )
            del obj_in["person"]

    def on_post_create(self, obj: PartnerPerson, obj_in: Dict[str, Any]) -> None:
        if person := obj_in.get("person", None):
            send_email.apply_async(
                args=(
                    obj.person_id,
                    settings.POST_PARTNER_PERSON_CREATE_EMAIL_TITLE,
                    settings.POST_PARTNER_PERSON_CREATE_EMAIL.format(
                        obj.person.name,
                        obj.person.phone_number,
                        person["hashed_password"],
                    ),
                ),
                queue=settings.CELERY_NOTIFICATIONS_QUEUE,
            )

    def modify_query(
        self,
        query: QuerySet,
        order_fields: Optional[List] = None,
        filters: Optional[dict] = None,
    ) -> QuerySet:
        if order_fields:
            if "state" in order_fields:
                order_fields.append("partnerpersonschedule")
                order_fields.append("is_active")
                del order_fields[order_fields.index("state")]
            if "-state" in order_fields:
                order_fields.append("-partnerpersonschedule")
                order_fields.append("-is_active")
                del order_fields[order_fields.index("-state")]
        return query

    def on_pre_delete(self, obj: PartnerPerson) -> None:
        Person.objects.filter(id=obj.person_id).delete()


partner_person_service = PartnerPersonService(PartnerPerson)


class PartnerSMSPackageSerivce(
    CRUDService[
        PartnerSMS, PartnerSMSPackageCreateSerializer, PartnerSMSPackageUpdateSerializer
    ]
):
    def get_latest_sms_package(self, *, partner_id: Union[str, int]) -> PartnerSMS:
        sms_package = (
            PartnerSMS.objects.filter(partner_id=partner_id)
            .order_by(*["created_at"])
            .first()
        )
        if not sms_package:
            raise HttpErrorException(
                status_code=404,
                code=ErrorCodes.NO_SMS_PACKAGE,
            )
        return sms_package


partner_sms_service = PartnerSMSPackageSerivce(PartnerSMS)


class PartnerPromoService(
    CRUDService[
        PartnerPromotion, PartnerPromoCreateSerializer, PartnerPromoUpdateSerializer
    ]
):
    def on_pre_update(self, obj_in: dict, obj: PartnerPromotion) -> None:
        if obj_in["message"]:
            obj.verified = False
            obj.save()


partner_promo_service = PartnerPromoService(PartnerPromotion)

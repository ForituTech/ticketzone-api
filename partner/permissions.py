from typing import Any, Union

from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from core.error_codes import ErrorCodes
from core.exceptions import HttpErrorException
from eticketing_api import settings
from partner.constants import PersonType
from partner.models import Partner, PartnerPerson
from partner.utils import decode_access_token, get_user_from_access_token

ACCESS_DENIED_EXCEPTION = HttpErrorException(
    status_code=403,
    code=ErrorCodes.ACCESS_DENIED,
)

NON_SELF_EXCEPTION = HttpErrorException(
    status_code=403,
    code=ErrorCodes.ACCESS_ONLY_FOR_SELF,
)

NO_PARTNERSHIP_EXCEPTION = HttpErrorException(
    status_code=403,
    code=ErrorCodes.NO_PARTNERSHIP,
)

NO_MEMBERSHIP_EXCEPTION = HttpErrorException(
    status_code=401, code=ErrorCodes.NO_MEMBERSHIP
)


def check_self(request: Request, pk: Union[str, int]) -> bool:
    token_key = settings.AUTH_HEADER
    if token_key not in request.META:
        raise ACCESS_DENIED_EXCEPTION

    user_data = decode_access_token(request.META[token_key])

    if user_data["user_id"] != pk:
        raise NON_SELF_EXCEPTION

    return True


def check_self_no_partnership(request: Request, pk: Union[str, int]) -> bool:
    token_key = settings.AUTH_HEADER
    if token_key not in request.META:
        raise ACCESS_DENIED_EXCEPTION

    user = get_user_from_access_token(request.META[token_key])

    if str(user.id) != pk:
        raise NON_SELF_EXCEPTION

    return True


def get_request_user_id(request: Request) -> str:
    token_key = settings.AUTH_HEADER
    if token_key not in request.META:
        raise ACCESS_DENIED_EXCEPTION

    user_data = decode_access_token(request.META[token_key])

    return user_data["user_id"]


def get_request_partner_id(request: Request) -> str:
    token_key = settings.AUTH_HEADER
    if token_key not in request.META:
        raise ACCESS_DENIED_EXCEPTION

    user_data = decode_access_token(request.META[token_key])

    return user_data["partner"]


def get_request_person(request: Request) -> PartnerPerson:
    user_id = get_request_user_id(request)
    partner_id = get_request_partner_id(request)

    try:
        person: PartnerPerson = PartnerPerson.objects.get(
            person_id=user_id, partner_id=partner_id
        )
        if not person.is_active:
            raise ACCESS_DENIED_EXCEPTION
        return person
    except PartnerPerson.DoesNotExist:
        raise NO_MEMBERSHIP_EXCEPTION


def get_request_person_id(request: Request) -> str:
    user_id = get_request_user_id(request)
    partner_id = get_request_partner_id(request)

    try:
        person: PartnerPerson = PartnerPerson.objects.get(
            person_id=user_id, partner_id=partner_id
        )
        if not person.is_active:
            raise ACCESS_DENIED_EXCEPTION
        return str(person.person_id)
    except PartnerPerson.DoesNotExist:
        if not Partner.objects.filter(**{"owner_id": user_id, "pk": partner_id}):
            raise NO_MEMBERSHIP_EXCEPTION
        return user_id


def get_request_partner_person_id(request: Request) -> str:
    """
    NOTE: This should only be used with permissions guarded
        endpoints
    """
    user_id = get_request_person_id(request)
    partner_id = get_request_partner_id(request)
    return str(PartnerPerson.objects.get(person_id=user_id, partner_id=partner_id).id)


def check_permissions(request: Request, person_type: PersonType) -> bool:
    token_key = settings.AUTH_HEADER
    if token_key not in request.META:
        raise ACCESS_DENIED_EXCEPTION

    user_data = decode_access_token(request.META[token_key])

    try:
        partner_person: PartnerPerson = PartnerPerson.objects.get(
            person_id=user_data["user_id"]
        )
        if not partner_person.is_active:
            raise ACCESS_DENIED_EXCEPTION
    except PartnerPerson.DoesNotExist:
        try:
            Partner.objects.get(owner_id=user_data["user_id"])
        except Partner.DoesNotExist:
            raise NO_PARTNERSHIP_EXCEPTION

    if user_data["membership"] != person_type.value:
        raise ACCESS_DENIED_EXCEPTION

    return True


class PartnerOwnerPermissions(BasePermission):
    message = "Access Denied (Partner Ownership)"

    def has_permission(self, request: Request, view: Any) -> bool:
        return check_permissions(request=request, person_type=PersonType.OWNER)


class PartnerMembershipPermissions(BasePermission):
    message = "Acces Denied (Partner Membership)"

    def has_permission(self, request: Request, view: Any) -> bool:
        try:
            return check_permissions(
                request=request, person_type=PersonType.PARTNER_MEMBER
            )
        except Exception:
            return check_permissions(request=request, person_type=PersonType.OWNER)


class TicketingAgentPermissions(BasePermission):
    message = "Access Denied (TicketingAgent)"

    def has_permission(self, request: Request, view: Any) -> bool:
        try:
            return check_permissions(
                request=request, person_type=PersonType.TICKETING_AGENT
            )
        except Exception:
            return check_permissions(request=request, person_type=PersonType.OWNER)


class CustomerPermissions(BasePermission):
    message = "Access Denied (Customer)"

    def has_permission(self, request: Request, view: Any) -> bool:
        return check_permissions(request=request, person_type=PersonType.CUSTOMER)


class LoggedInPermission(BasePermission):
    message = "You need to be authenticated to perform this action"

    def has_permission(self, request: Request, view: Any) -> bool:
        token_key = settings.AUTH_HEADER
        if token_key not in request.META:
            raise ACCESS_DENIED_EXCEPTION

        user = get_user_from_access_token(request.META[token_key])

        return user is not None

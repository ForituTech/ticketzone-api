from typing import Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from core.error_codes import ErrorCodes
from core.exceptions import HttpErrorException
from partner.constants import PersonType
from partner.utils import decode_access_token

ACCESS_DENIED_EXCEPTION = HttpErrorException(
    status_code=403,
    code=ErrorCodes.ACCESS_DENIED,
)


def check_permissions(request: Request, person_type: PersonType) -> bool:
    token_key = "Authorization"
    if token_key not in request.META:
        raise ACCESS_DENIED_EXCEPTION

    user_data = decode_access_token(request.META[token_key])

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
        return check_permissions(request=request, person_type=PersonType.PARTNER_MEMBER)


class TicketingAgentPermissions(BasePermission):
    message = "Access Denied (TicketingAgent)"

    def has_permission(self, request: Request, view: Any) -> bool:
        return check_permissions(
            request=request, person_type=PersonType.TICKETING_AGENT
        )


class CustomerPermissions(BasePermission):
    message = "Access Denied (Customer)"

    def has_permission(self, request: Request, view: Any) -> bool:
        return check_permissions(request=request, person_type=PersonType.CUSTOMER)

from drf_yasg.utils import swagger_auto_schema
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response

from core.views import AbstractPermissionedView
from partner.permissions import (
    LoggedInPermission,
    PartnerMembershipPermissions,
    check_self,
)
from payments.serilaizers import (
    PaymentCreateSerializer,
    PaymentReadSerializer,
    PaymentSerializer,
)
from payments.services import payment_service

paginator = PageNumberPagination()
paginator.page_size = 15


class PaymentsViewSet(AbstractPermissionedView):

    permissions_by_action = {
        "create": [LoggedInPermission],
        "update": [PartnerMembershipPermissions],
    }

    @swagger_auto_schema(
        request_body=PaymentSerializer, responses={200: PaymentReadSerializer}
    )
    def create(self, request: Request) -> Response:
        payment = payment_service.create(
            obj_data=request.data, serializer=PaymentCreateSerializer
        )
        # TODO: check_self should happend before creation
        try:
            check_self(request, str(payment.person_id))
        except Exception as exc:
            payment.delete()
            raise exc
        return Response(PaymentReadSerializer(payment).data)

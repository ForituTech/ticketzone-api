from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response

from core.views import AbstractPermissionedView
from partner.permissions import PartnerOwnerPermissions
from partner.serializers import PartnerSMSPackageReadSerializer
from partner.utils import get_request_membership_or_ownership
from payments.serilaizers import (
    PaymentCreateSerializer,
    PaymentCreateSerializerInner,
    PaymentMethodSerialzier,
    PaymentReadSerializer,
    SMSPaymentCreateSerializerInner,
)
from payments.services import payment_method_service, payment_service

paginator = PageNumberPagination()
paginator.page_size = 15


@swagger_auto_schema(method="GET", responses={200: PaymentMethodSerialzier(many=True)})
@api_view(["GET"])
def list_payment_methods(request: Request) -> Response:
    methods = payment_method_service.get_all()
    return Response(PaymentMethodSerialzier(methods, many=True).data)


@swagger_auto_schema(
    method="post",
    request_body=SMSPaymentCreateSerializerInner,
    responses={200: PartnerSMSPackageReadSerializer},
)
@api_view(["POST"])
@permission_classes([PartnerOwnerPermissions])
def fund_sms_package(request: Request) -> Response:
    obj_data = SMSPaymentCreateSerializerInner(
        data_in=request.data.copy(), data=request.data
    )
    obj_data.is_valid(raise_exception=True)
    partner_id = get_request_membership_or_ownership(request)[0]
    sms_package = payment_service.fund_sms_package(
        partner_id=partner_id, payment_in=obj_data
    )
    return Response(PartnerSMSPackageReadSerializer(sms_package).data)


class PaymentsViewSet(AbstractPermissionedView):
    @swagger_auto_schema(
        request_body=PaymentCreateSerializer, responses={200: PaymentReadSerializer}
    )
    def create(self, request: Request) -> Response:
        obj_data = payment_service.validate_ticket_types_and_person(request.data)
        payment = payment_service.create(
            obj_data=obj_data, serializer=PaymentCreateSerializerInner
        )
        return Response(PaymentReadSerializer(payment).data)

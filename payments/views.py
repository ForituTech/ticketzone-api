from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response

from core.views import AbstractPermissionedView
from payments.serilaizers import (
    PaymentCreateSerializer,
    PaymentCreateSerializerInner,
    PaymentMethodSerialzier,
    PaymentReadSerializer,
)
from payments.services import payment_method_service, payment_service

paginator = PageNumberPagination()
paginator.page_size = 15


@swagger_auto_schema(method="GET", responses={200: PaymentMethodSerialzier(many=True)})
@api_view(["GET"])
def list_payment_methods(request: Request) -> Response:
    methods = payment_method_service.get_all()
    return Response(PaymentMethodSerialzier(methods, many=True).data)


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

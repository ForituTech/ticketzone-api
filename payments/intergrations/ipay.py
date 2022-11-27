import hashlib
import hmac
import os
from typing import Optional

import requests

from partner.models import Partner
from payments.constants import PaymentStates, PaymentTransactionState
from payments.interfaces import PaymentProviderType
from payments.models import Payment, PaymentTransactionLogs
from payments.serilaizers import PaymentUpdateSerializer


class SharedMethods:
    INITIATOR_URL = "https://apis.ipayafrica.com/payments/v2/transact"

    def get_dict_hash(self, dict_: dict) -> str:
        value_string = ""
        for value in dict_.values():
            if isinstance(value, list):
                for nested_value_dict in value:
                    for nested_value in nested_value_dict.values():
                        value_string += nested_value
            if isinstance(value, str):
                value_string += value

        hash_obj = hmac.new(
            key=os.environ["iPAY_PROVIDER_KEY"].encode(),
            msg=value_string.encode(),
            digestmod=hashlib.sha256,
        )
        return hash_obj.hexdigest()

    def get_string_hash(self, string: str) -> str:
        hash_obj = hmac.new(
            key=os.environ["iPAY_PROVIDER_KEY"].encode(),
            msg=string.encode(),
            digestmod=hashlib.sha256,
        )
        return hash_obj.hexdigest()

    def construct_initiator_payload(self, payment: Payment) -> dict:
        pass

        payload = {
            "live": os.environ["PAYMENTS_LIVE"],
            "oid": payment.number,
            "inv": str(payment.id),
            "amount": f"{payment.amount}",
            "tel": f"{payment.person.phone_number}",
            "eml": f"{payment.person.email}",
            "vid": os.environ["iPAY_PROVIDER_ID"],
            "curr": "KES",
            "p1": str(payment.person.id),
            "p2": str(payment.id),
            "cst": "1",
            "crl": "2",
            "cbk": os.environ["iPAY_CALLBACK_URL"],
        }

        payload__with_hash_format = payload.copy()
        del payload__with_hash_format["crl"]
        payload["hash"] = self.get_dict_hash(payload__with_hash_format)

        return payload

    def validate_initiator_response(self, resp_data: dict) -> bool:
        values_string = "{}{}{}{}{}{}{}{}".format(
            resp_data["data"]["account"],
            resp_data["data"]["amount"],
            resp_data["data"]["oid"],
            resp_data["data"]["sid"],
            resp_data["data"]["payment_channels"][0]["name"],
            resp_data["data"]["payment_channels"][0]["paybill"],
            resp_data["data"]["payment_channels"][1]["name"],
            resp_data["data"]["payment_channels"][1]["paybill"],
        )
        return resp_data["data"].get("hash", None) == self.get_string_hash(
            values_string
        )

    def get_resp_sid(self, resp_data: dict) -> str:
        return resp_data["data"]["sid"]

    def validate_transaction_response(self, resp_data: dict) -> bool:
        pass

    def initiate_transaction(self, payment: Payment) -> Optional[str]:
        payload = self.construct_initiator_payload(payment=payment)
        res = requests.post(self.INITIATOR_URL, data=payload)
        if res.status_code >= 300:
            PaymentTransactionLogs(payment=payment, message=str(res.json())).save()
            return None
        if self.validate_initiator_response(resp_data=res.json()):
            return self.get_resp_sid(resp_data=res.json())
        else:
            PaymentTransactionLogs(
                payment=payment, message="Couldn't validate providers response"
            ).save()
            return None


class iPayMPesa(SharedMethods, PaymentProviderType):
    MOBILE_MONEY_URL = "https://apis.ipayafrica.com/payments/v2/transact/push/mpesa"

    def create_payment_payload(self, transation_id: str, phone: str) -> dict:
        payload = {
            "phone": phone,
            "vid": os.environ["iPAY_PROVIDER_ID"],
            "sid": transation_id,
        }
        payload["hash"] = self.get_dict_hash(dict_=payload)
        return payload

    def c2b_receive(self, *, payment: Payment) -> None:
        if transaction_id := self.initiate_transaction(payment=payment):
            payload = self.create_payment_payload(
                transation_id=transaction_id, phone=payment.person.phone_number
            )
            res = requests.post(self.MOBILE_MONEY_URL, data=payload)

            from payments.services import payment_service

            if int(res.json()["status"]):
                payment_state = (
                    PaymentStates.PENDING.value
                    if int(os.environ["PAYMENTS_LIVE"])
                    else PaymentStates.PAID.value
                )
                payment_service.update(
                    obj_data={"state": payment_state},
                    serializer=PaymentUpdateSerializer,
                    obj_id=str(payment.id),
                )
                PaymentTransactionLogs.objects.create(
                    payment=payment,
                    message=res.json()["text"],
                    state=PaymentTransactionState.INITIATED.value,
                ).save()
            else:
                payment_service.update(
                    obj_data={"state": PaymentStates.PENDING.value},
                    serializer=PaymentUpdateSerializer,
                    obj_id=str(payment.id),
                )
                PaymentTransactionLogs.objects.create(
                    payment=payment, message=str(res.json())
                ).save()

    def verify(self) -> bool:
        pass

    def b2c_send(self, *, amount: int, partner: Partner) -> PaymentStates:
        pass

    # partner disbursment
    def b2b_send(self, *, amount: int, partner: Partner) -> PaymentStates:
        pass

    def search(self, *, transaction_id: str) -> Optional[Payment]:
        pass


class iPayCard(SharedMethods, PaymentProviderType):
    def verify(self) -> bool:
        return True

    def c2b_receive(self, *, payment: Payment) -> None:
        payment.state = PaymentStates.PAID.value
        payment.save()

    def b2c_send(self, *, amount: int, partner: Partner) -> PaymentStates:
        pass

    # partner disbursment
    def b2b_send(self, *, amount: int, partner: Partner) -> PaymentStates:
        pass

    def search(self, *, transaction_id: str) -> Optional[Payment]:
        pass

from typing import Dict

from payments.constants import PaymentProviders
from payments.interfaces import PaymentProviderType
from payments.intergrations.ipay import iPayCard, iPayMPesa

active_payment_processor_mpesa = iPayMPesa()
active_payment_processor_card = iPayCard()
payment_processor_map: Dict[str, PaymentProviderType] = {
    PaymentProviders.MPESA.value: active_payment_processor_mpesa,
    PaymentProviders.BANK.value: active_payment_processor_card,
}

callback_url = "/payments/callback/"

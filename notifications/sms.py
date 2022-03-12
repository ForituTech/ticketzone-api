from typing import List

import africastalking

from eticketing_api import settings


class SMSClient:
    def __init__(self) -> None:
        africastalking.initialize(
            settings.AFRICAS_TALKING_USERNAME, settings.AFRICAS_TALKING_KEY
        )
        self.sms_client = africastalking.SMS

    def send(self, message: str, numbers: List[str]) -> None:
        self.sms_client.send(message, numbers)


sms_client = SMSClient()

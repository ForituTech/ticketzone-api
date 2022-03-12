from typing import Any, Dict, List, Optional

from pusher_push_notifications import PusherError, PushNotifications

from eticketing_api import settings


class PusherClient:
    """Pusher client for in-app push notifications"""

    def __init__(self) -> None:
        # Initialize and set the config params
        self.beams_client = PushNotifications(
            instance_id=settings.PUSHER_INSTANCE_ID,
            secret_key=settings.PUSHER_SECRET_KEY,
        )

    def push_web_notification(
        self, *, user_ids: List[str], body: str, data: Optional[Dict[str, Any]] = dict()
    ) -> Optional[Dict[str, str]]:
        try:
            response = self.beams_client.publish_to_users(
                user_ids=user_ids,
                publish_body={
                    "web": {
                        "notification": {
                            "body": body,
                        },
                        "data": data,
                    }
                },
            )
            return {"id": response["publishId"], "status": "SUCCESS"}
        except PusherError:
            return None

    def generate_token(self, user_id: str) -> str:
        return self.beams_client.generate_token(user_id)


pusher_client = PusherClient()

import hashlib
import hmac
from datetime import datetime

from django.test import TransactionTestCase
from fastapi.testclient import TestClient

from eticketing_api.asgi import app
from partner_api.auth.tests.fixtures import create_partner_api_credentials_obj

API_BASE_URL = "/v1/auth"


class AuthTestCase(TransactionTestCase):
    def setUp(self) -> None:
        # fastapi client
        self.fa_client = TestClient(app)

    def test_login_external_api(self) -> None:
        api_creds = create_partner_api_credentials_obj()
        now = datetime.now()

        value_string = f"{api_creds.id}{now}"
        hash_obj = hmac.new(
            key=api_creds.secret.encode(),
            msg=value_string.encode(),
            digestmod=hashlib.sha256,
        )
        secret = hash_obj.hexdigest()
        data = {"partner_key": str(api_creds.id), "now": str(now), "signature": secret}

        res = self.fa_client.post(f"{API_BASE_URL}/", json=data)
        assert res.status_code == 200
        assert "access_token" in res.text
        assert "refresh_token" in res.text

    def test_refresh_token(self) -> None:
        api_creds = create_partner_api_credentials_obj()
        now = datetime.now()

        value_string = f"{api_creds.id}{now}"
        hash_obj = hmac.new(
            key=api_creds.secret.encode(),
            msg=value_string.encode(),
            digestmod=hashlib.sha256,
        )
        secret = hash_obj.hexdigest()
        data = {"partner_key": str(api_creds.id), "now": str(now), "signature": secret}

        res = self.fa_client.post(f"{API_BASE_URL}/", json=data)
        assert res.status_code == 200

        refresh_res = self.fa_client.post(
            f"{API_BASE_URL}/refresh/",
            headers={"refresh-token": res.json()["refresh_token"]},
        )
        assert refresh_res.status_code == 200
        assert "access_token" in refresh_res.text
        assert "refresh_token" in refresh_res.text

from pydantic import BaseModel


class LoginCredentialsSerializer(BaseModel):
    partner_key: str
    now: str
    signature: str


class LoginResponseSerializer(BaseModel):
    access_token: str
    refresh_token: str

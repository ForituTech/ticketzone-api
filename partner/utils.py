import random
from datetime import datetime, timedelta
from typing import Any, Dict, Union

from jose import JWTError, jwt
from passlib.context import CryptContext

from core.error_codes import ErrorCodes
from core.exceptions import HttpErrorException
from eticketing_api.settings import SECRET_KEY
from partner.models import Person

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def random_password() -> str:
    pin = random.randint(1000, 9999)
    return str(pin)


def hash_password(plaintext_password: str) -> str:
    return pwd_context.hash(plaintext_password)


def verify_password(plaintext: str, hashed: str) -> bool:
    return pwd_context.verify(plaintext, hashed)


def create_access_token(
    user: Person, expires_delta: Union[timedelta, None] = None
) -> str:
    to_encode = {
        "phonenumber": user.phone_number,
        "user_type": user.person_type,
        "user_id": str(user.id),
    }
    expire = datetime.utcnow() + timedelta(minutes=1440)
    to_encode.update({"expiry": expire.strftime("%H:%M:%S %d-%b-%Y")})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    broken_token_exception = HttpErrorException(
        status_code=403,
        code=ErrorCodes.UNPROCESSABLE_TOKEN,
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        phonenumber: str = payload.get("phonenumber")
        if phonenumber is None:
            raise broken_token_exception
        return payload
    except JWTError:
        raise broken_token_exception


def get_user_from_access_token(token: str) -> Person:
    payload = decode_access_token(token)
    user_id = payload.get("user_id")
    user = Person.objects.get(pk=user_id)
    if not user:
        raise HttpErrorException(
            status_code=404,
            code=ErrorCodes.INVALID_CREDENTIALS,
        )
    return user

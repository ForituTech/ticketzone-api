import random
from datetime import datetime, timedelta
from typing import Any, Dict, Tuple, Union

from jose import JWTError, jwt
from passlib.context import CryptContext

from core.error_codes import ErrorCodes
from core.exceptions import HttpErrorException
from eticketing_api.settings import SECRET_KEY
from partner.constants import PersonType
from partner.models import Partner, PartnerPerson, Person

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


def get_membership_or_ownership(user: Person) -> Tuple[str, str]:
    non_existant_partneship_exception = HttpErrorException(
        status_code=404, code=ErrorCodes.NO_PARTNERSHIP
    )
    try:
        partner = Partner.objects.get(owner=user.id)
        membership = PersonType.OWNER.value
    except Partner.DoesNotExist:
        try:
            person: PartnerPerson = PartnerPerson.objects.get(person=user.id)
            membership = person.person_type
            partner = person.partner
        except PartnerPerson.DoesNotExist:
            raise non_existant_partneship_exception
    return (str(partner.id), membership)


def create_access_token(
    user: Person, expires_delta: Union[timedelta, None] = None
) -> str:
    membership = get_membership_or_ownership(user)
    to_encode = {
        "phone_number": user.phone_number,
        "user_id": str(user.id),
        "partner": membership[0],
        "membership": membership[1],
    }
    expire = datetime.utcnow() + timedelta(minutes=1440)
    to_encode.update({"expiry": expire.strftime("%H:%M:%S %d-%b-%Y")})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_access_token_lite(
    user: Person, expires_delta: Union[timedelta, None] = None
) -> str:
    to_encode = {
        "phone_number": user.phone_number,
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
    non_existant_membership_exception = HttpErrorException(
        status_code=404, code=ErrorCodes.INVALID_CREDENTIALS
    )
    multiple_user_members_exception = HttpErrorException(
        status_code=500, code=ErrorCodes.MULTIPLE_USERS_SAME_PHONENUMBER
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        phone_number: str = payload.get("phone_number", None)
        if (
            phone_number is None
            or "user_id" not in payload
            or "partner" not in payload
            or "membership" not in payload
        ):
            raise broken_token_exception
        try:
            Person.objects.get(phone_number=phone_number)
        except Person.DoesNotExist:
            raise non_existant_membership_exception
        except Person.MultipleObjectsReturned:
            raise multiple_user_members_exception
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

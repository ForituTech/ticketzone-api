import random

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def random_password() -> str:
    pin = random.randint(1000, 9999)
    return str(pin)


def hash_password(plaintext_password: str) -> str:
    return pwd_context.hash(plaintext_password)


def verify_password(plaintext: str, hashed: str) -> bool:
    return pwd_context.verify(plaintext, hashed)

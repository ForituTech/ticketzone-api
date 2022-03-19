import random
import string


def random_string() -> str:
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(10))

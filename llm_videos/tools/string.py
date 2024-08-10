
import secrets
import string

def random_string(length: int = 10) -> str:
    """Generate a random string of fixed length."""
    return "".join(secrets.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for i in range(length))
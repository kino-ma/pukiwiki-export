import hashlib
import secrets


def random_password(length: int = 64):
    p = secrets.token_urlsafe(length)

    return p


def sha256(text: str) -> str:
    m = hashlib.sha256()
    bytes = text.encode()
    m.update(bytes)
    hashed_bytes = m.digest()
    hashed_str = hashed_bytes.hex()
    return hashed_str


def hash_password(seed: str, password: str) -> str:
    with_seed = f"{seed}{password}"
    hashed = sha256(with_seed)
    return hashed

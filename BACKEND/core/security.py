from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
#PasswordHasher is a class from the argon2 Python package that helps you hash passwords and verify them later.
from argon2.exceptions import (
    VerifyMismatchError, #This exception occurs when the password you provide doesn't match the stored hash.
    VerificationError,#This is a broader error related to a failure during password verification. It can cover verification failures other than a straightforward password mismatch.
    InvalidHashError,#This indicates that the stored hash is malformed or doesn't have a valid Argon2 hash format.
)

from core.config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    ACCESS_TOKEN_MINUTES,
)

password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(
    password: str,
    hashed_password: str
) -> bool:
    try:
        return password_hasher.verify(
            hashed_password,
            password
        )
    except (
        VerifyMismatchError,
        VerificationError,
        InvalidHashError,
    ):
        return False


def create_access_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + timedelta(
            minutes=ACCESS_TOKEN_MINUTES
        ),
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token,
        JWT_SECRET_KEY,
        algorithms=[JWT_ALGORITHM],
        options={"require": ["sub", "exp"]},
    )


"""
hash_password() transforms the password before database storage.



verify_password() checks a submitted password against its hash.



create_access_token() creates a signed JWT with an expiry.



decode_access_token() validates the JWT signature and expiry.
"""
import secrets
#secrets: generates unpredictable security tokens and compares them safely.

from fastapi import HTTPException, Request, status
#Request: gives your endpoint access to incoming cookies and headers.
#status: provides readable HTTP status constants, such as 403 Forbidden.
from core.config import COOKIE_SECURE

CSRF_COOKIE = "csrf_token"
CSRF_HEADER = "X-CSRF-Token"


def set_csrf_cookie(response) -> str:
    token = secrets.token_urlsafe(32)

    response.set_cookie(
        key=CSRF_COOKIE,
        value=token,
        httponly=False,
        secure=COOKIE_SECURE,
        samesite="lax",
        path="/",
    )

    return token

"""
Argument	Meaning
key=CSRF_COOKIE	Names the cookie csrf_token.
value=token	Stores the generated token as its value.
httponly=False	Allows frontend JavaScript to read this cookie.
secure=COOKIE_SECURE	Requires HTTPS when enabled.
samesite="lax"	Restricts many cross-site cookie requests.
path="/"	Makes the cookie available across paths on that host.
"""


async def verify_csrf(request: Request) -> None:
    cookie_token = request.cookies.get(CSRF_COOKIE)#FastAPI reads the incoming request's cookies and retrieves the value of csrf_token.
    header_token = request.headers.get(CSRF_HEADER)
    """
    request.cookies.get(...) → reads the token from the incoming cookie.



    request.headers.get(...) → reads the token from the incoming HTTP header.



await verify_csrf(request) → runs your verification function before registration, login or logout continues.
    """

    if (
        not cookie_token
        or not header_token
        or not secrets.compare_digest(
            cookie_token, header_token
            #secrets.compare_digest() compares the strings using a timing-resistant comparison, which is preferable for security-sensitive comparisons.
        )
    ):
        print("CSRF cookie received:", bool(cookie_token))
        print("CSRF header received:", bool(header_token))
        print(
             "CSRF tokens match:",
             bool(cookie_token and header_token)
            and secrets.compare_digest(cookie_token, header_token),
)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing CSRF token",
        )



"""
CSRF stands for Cross-Site Request Forgery.
Imagine your application has a logged-in user. The browser stores an authentication cookie, and a malicious website tricks that browser into sending a request to your API.
If the browser automatically attaches the authentication cookie, your API might receive a request the user never intended to make.
CSRF protection helps your backend detect these unwanted requests.
"""        
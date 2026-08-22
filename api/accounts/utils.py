

from config import settings


def set_jwt_cookies(response, access, refresh):
    """
    Create a CSRF JWT token using the access and refresh tokens.
    """
    response.set_cookie(
        key="access_token",
        value=access,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax",
        path="/",
        max_age= int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds())
    )
    
    response.set_cookie(
        key="refresh_token",
        value=refresh,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax",
        max_age= int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        path="/",
    )
    return response
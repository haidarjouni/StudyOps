from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        access_token = request.COOKIES.get("access_token")
        if not access_token:
            return None  # No token provided, return None to indicate no authentication
        access_token = self.get_validated_token(access_token)
        return self.get_user(access_token), access_token

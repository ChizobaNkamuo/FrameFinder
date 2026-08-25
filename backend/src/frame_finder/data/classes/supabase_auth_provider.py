from supabase import Client
from src.frame_finder.data.interfaces.auth_provider import AuthProvider
from src.frame_finder.data_classes.auth_result import AuthResult
from src.frame_finder.pydantic_classes.user import User
from src.frame_finder.pydantic_classes.auth_response import AuthResponse
from fastapi.security import HTTPAuthorizationCredentials

class SupabaseAuthProvider(AuthProvider):

    _SIGN_IN_ERRORS = {
        "invalid_credentials": "Invalid email or password.",
        "email_not_confirmed": "Please confirm your email address before signing in.",
    }

    _SIGN_UP_ERRORS = {
        "user_already_exists": "An account with this email already exists.",
        "weak_password": "Password should be at least 6 characters",
    }

    _DEFAULT_ERROR = "Something went wrong. Please try again."

    def __init__(self, client: Client):
        self._client = client

    def sign_in(
        self,
        email: str,
        password: str,
    ) -> AuthResult:
        try:
            response = self._client.auth.sign_in_with_password({
                "email": email,
                "password": password,
            })

            return AuthResult(
                user_id=response.user.id,
                email=response.user.email,
                access_token=response.session.access_token,
                refresh_token=response.session.refresh_token,
            )

        except Exception as error:
            error_code = getattr(error, "code", None)
            error_message = self._SIGN_IN_ERRORS.get(
                error_code,
                self._DEFAULT_ERROR,
            )

            return AuthResult(
                success=False,
                error_code=error_code,
                error_message=error_message,
            )

    def sign_up(
        self,
        email: str,
        password: str,
    ) -> AuthResult:
        try:
            response = self._client.auth.sign_up({
                "email": email,
                "password": password,
            })
            return AuthResult(
                success=True,
                user_id=response.user.id,
                email=response.user.email,
            )

        except Exception as error:
            error_code = getattr(error, "code", None)
            error_message = self._SIGN_UP_ERRORS.get(
                error_code,
                self._DEFAULT_ERROR,
            )

            return AuthResult(
                success=False,
                error_code=error_code,
                error_message=error_message,
            )
            

    def get_current_user(
        self, credentials: HTTPAuthorizationCredentials,
    ) -> User:
        token = credentials.credentials
        response = self._client.auth.get_user(token)
        user = response.user

        if user:
            return User(
                id=user.id,
                email=user.email
            )


    def refresh(
        self,
        refresh_token: str,
    ) -> AuthResponse:

        response = (
            self._client.auth.refresh_session(
                refresh_token
            )
        )

        return AuthResponse(
            access_token=response.session.access_token,
            refresh_token=response.session.refresh_token,
            email=response.user.email
        )
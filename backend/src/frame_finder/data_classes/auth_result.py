from dataclasses import dataclass

@dataclass
class AuthResult():
    success: bool = True

    user_id: str | None = None
    email: str | None = None

    access_token: str | None = None
    refresh_token: str | None = None

    error_code: str | None = None
    error_message: str | None = None
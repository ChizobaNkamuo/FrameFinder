from abc import ABC, abstractmethod
from src.frame_finder.data_classes.auth_result import AuthResult
from src.frame_finder.pydantic_classes.user import User
from fastapi.security import HTTPAuthorizationCredentials

class AuthProvider(ABC):
    @abstractmethod
    def sign_up(
        self,
        email: str,
        password: str,
    ) -> AuthResult:
        pass

    @abstractmethod
    def sign_in(
        self,
        email: str,
        password: str,
    ) -> AuthResult:
        pass

    @abstractmethod
    def get_current_user(
        self, 
        credentials: HTTPAuthorizationCredentials,
    ) -> User:
        pass

    @abstractmethod
    def refresh(
        self,
        refresh_token: str,
    ) -> AuthResult:
        pass
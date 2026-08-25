from abc import ABC, abstractmethod
from src.frame_finder.data.interfaces.auth_provider import AuthProvider

class AuthProviderFactory(ABC):
    @abstractmethod
    def new(
        self
    ) -> AuthProvider:
        pass
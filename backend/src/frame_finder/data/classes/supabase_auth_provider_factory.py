from src.frame_finder.data.classes.supabase_auth_provider import SupabaseAuthProvider
from src.frame_finder.data.interfaces.auth_provider import AuthProvider
from src.frame_finder.data.interfaces.auth_provider_factory import AuthProviderFactory
from dotenv import load_dotenv
from supabase import create_client
import os

load_dotenv()

class SupabaseAuthProviderFactory(AuthProviderFactory):
    def new(self) -> AuthProvider:
        client = create_client(
            os.environ.get("SUPABASE_URL"),
            os.environ.get("SUPABASE_SECRET_KEY")
        )
        return SupabaseAuthProvider(client=client)
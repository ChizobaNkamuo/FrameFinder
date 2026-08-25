from src.frame_finder.data.classes.supabase_data_store import SupabaseDataStore
from src.frame_finder.data.interfaces.data_store import DataStore
from src.frame_finder.data.interfaces.data_store_factory import DataStoreFactory
from dotenv import load_dotenv
from supabase import create_client
import os

load_dotenv()

class SupabaseDataStoreFactory(DataStoreFactory):
    def new(self) -> DataStore:
        client = create_client(
            os.environ.get("SUPABASE_URL"),
            os.environ.get("SUPABASE_SECRET_KEY")
        )
        return SupabaseDataStore(client=client)
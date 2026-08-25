from src.frame_finder.data.classes.local_data_store import LocalDataStore
from src.frame_finder.data.interfaces.data_store import DataStore
from src.frame_finder.data.interfaces.data_store_factory import DataStoreFactory
from pathlib import Path

class LocalDataStoreFactory(DataStoreFactory):
    def new(self) -> DataStore:
        return LocalDataStore(root=Path("data"))
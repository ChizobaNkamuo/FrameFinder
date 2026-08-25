from abc import ABC, abstractmethod
from src.frame_finder.data.interfaces.data_store import DataStore

class DataStoreFactory(ABC):
    @abstractmethod
    def new(
        self
    ) -> DataStore:
        pass
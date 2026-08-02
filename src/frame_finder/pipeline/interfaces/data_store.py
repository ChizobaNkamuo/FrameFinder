from abc import ABC, abstractmethod
from frame_finder.data_classes.indexed_video import IndexedVideo

class DataStore(ABC):
    @abstractmethod
    def save(
        self,
        username: str,
        video_id: str,
        indexed_video: IndexedVideo,
    ) -> None:
        pass

    @abstractmethod
    def load(
        self,
        username: str,
        video_id: str,
    ) -> IndexedVideo:
        pass
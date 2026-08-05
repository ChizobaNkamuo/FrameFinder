from abc import ABC, abstractmethod
from typing import List
from frame_finder.data_classes.indexed_video import IndexedVideo
from frame_finder.data_classes.video_data import VideoData

class DataStore(ABC):
    @abstractmethod
    def save(
        self,
        username: str,
        video_id: str,
        filename: str,
        indexed_video: IndexedVideo
    ) -> None:
        pass

    @abstractmethod
    def load(
        self,
        username: str,
        video_id: str,
    ) -> VideoData:
        pass

    def load_all(
        self,
        username: str,
    ) -> List[VideoData]:
        pass


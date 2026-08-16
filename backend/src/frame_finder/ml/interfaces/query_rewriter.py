from abc import ABC, abstractmethod
from backend.src.frame_finder.data_classes.query import Query

class QueryRewriter(ABC):

    @abstractmethod
    def rewrite(self, query: str) -> Query:
        pass
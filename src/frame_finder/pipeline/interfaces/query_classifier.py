from abc import ABC, abstractmethod

class QueryClassifier(ABC):

    @abstractmethod
    def classify(self, query: str) -> str:
        """
        Classify the user's query as one of:
        - speech
        - vision
        - both
        """
        pass
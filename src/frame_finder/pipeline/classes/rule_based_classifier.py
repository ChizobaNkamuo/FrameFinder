from spacy.language import Language
import spacy
from frame_finder.pipeline.interfaces.query_classifier import QueryClassifier
from frame_finder.files import load_word_set

class RuleBasedClassifier(QueryClassifier):
    _SPEECH_WORDS = load_word_set("frame_finder.config", "speech_words.txt")
    _VISION_WORDS = load_word_set("frame_finder.config", "vision_words.txt")

    def __init__(self):
        self._nlp: Language = spacy.load("en_core_web_sm")

    def classify(self, query: str) -> str:

        doc = self._nlp(query)

        speech_score = 0
        vision_score = 0

        for token in doc:
            lemma = token.lemma_.lower()

            if lemma in self._SPEECH_WORDS:
                speech_score += 1

            if lemma in self._VISION_WORDS:
                vision_score += 1

        if speech_score > 0 and vision_score == 0:
            return "speech"

        if vision_score > 0 and speech_score == 0:
            return "vision"

        return "both"
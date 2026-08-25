from unittest.mock import MagicMock, patch
from src.frame_finder.pipeline.classes.rule_based_classifier import RuleBasedClassifier
import src.frame_finder.pipeline.classes.rule_based_classifier as rbc

def _token(lemma: str):
    token = MagicMock()
    token.lemma_ = lemma
    return token

def _classifier_with_doc(doc):
    fake_nlp = MagicMock(return_value=doc)

    with patch.object(
        rbc.spacy,
        "load",
        return_value=fake_nlp,
    ):
        return RuleBasedClassifier(), fake_nlp

def test_constructor_loads_spacy_model():
    fake_nlp = MagicMock()

    with patch.object(rbc.spacy, "load", return_value=fake_nlp) as mock_load:
        classifier = RuleBasedClassifier()

        mock_load.assert_called_once_with("en_core_web_sm")
        assert classifier._nlp is fake_nlp


def test_classify_returns_speech():
    classifier, fake_nlp = _classifier_with_doc([
        _token("where"),
        _token("be"),
        _token("openai"),
        _token("mention"),
    ])

    result = classifier.classify(
        "Where is OpenAI mentioned?"
    )

    fake_nlp.assert_called_once_with(
        "Where is OpenAI mentioned?"
    )

    assert result == "speech"


def test_classify_returns_vision():
    classifier, _ = _classifier_with_doc([
        _token("show"),
        _token("diagram"),
    ])

    result = classifier.classify(
        "Show me the diagram."
    )

    assert result == "vision"


def test_classify_returns_both_when_both_detected():
    classifier, _ = _classifier_with_doc([
        _token("show"),
        _token("mention"),
    ])

    result = classifier.classify(
        "Show me where OpenAI is mentioned."
    )

    assert result == "both"


def test_classify_returns_both_when_no_keywords_found():
    classifier, _ = _classifier_with_doc([
        _token("hello"),
        _token("world"),
    ])

    result = classifier.classify(
        "Hello world."
    )

    assert result == "both"
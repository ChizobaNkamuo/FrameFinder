from typing import List
from frame_finder.ml.interfaces.embedding_model import EmbeddingModel
from frame_finder.ml.interfaces.speech_transcriber import SpeechTranscriber
from frame_finder.pipeline.interfaces.query_classifier import QueryClassifier
from frame_finder.ml.interfaces.query_rewriter import QueryRewriter
from frame_finder.data_classes.transcript_segment import TranscriptSegment
from frame_finder.data_classes.indexed_video import IndexedVideo
from frame_finder.data_classes.query import Query
import torch.nn.functional as F
import numpy as np

class Pipeline:
    def __init__(self, 
                 speech_transcriber: SpeechTranscriber, embedding_model: EmbeddingModel,
                 query_classifier: QueryClassifier, query_rewriter: QueryRewriter
                 ):
        self._speech_transcriber = speech_transcriber
        self._embedding_model = embedding_model
        self._query_classifier = query_classifier
        self._query_rewriter = query_rewriter

    def transcribe(self, audio_path: str) -> dict:
        return self._speech_transcriber.transcribe(audio_path)

    def process_segments(
        self,
        segments: List[dict]
    ) -> List[TranscriptSegment]:

        transcript_segments = []

        for segment in segments:
            embedding = self._embedding_model.embed_text(segment["text"])
        
            transcript_segments.append(
                TranscriptSegment(
                    text=segment["text"],
                    start=segment["start"],
                    end=segment["end"],
                    embedding=embedding,
                )
            )

        return transcript_segments

    def rank_transcript_segments(
        self,
        query_embedding: np.ndarray,
        transcript_segments: List[TranscriptSegment],
    ) -> List[TranscriptSegment]:
        similarities = []

        for segment in transcript_segments:
            similarity = F.cosine_similarity(
                query_embedding,
                segment.embedding,
                dim=0
            )

            similarities.append((segment, similarity.item()))

        similarities.sort(
            key=lambda x: x[1],
            reverse=True,
        )

        return [
            segment
            for segment, _ in similarities
        ]

    def extract_query_info(self, query: str) -> Query:
        rewritten_query = self._query_rewriter.rewrite(query)
        classification = self._query_classifier.classify(query)
        query_embedding = self._embedding_model.embed_text(rewritten_query)

        return Query(
            intent=rewritten_query,
            classification=classification,
            embedding=query_embedding
            )

    def search_for_query(self, formatted_query: Query, indexed_video: IndexedVideo):
        ranked_transcript_segments = self.rank_transcript_segments(query_embedding=formatted_query.embedding, transcript_segments=indexed_video.transcript_segments)

        for segment in ranked_transcript_segments:
            print(segment.text + " ("  + str(segment.start) + "-" + str(segment.end) +")")

from typing import List
from frame_finder.ml.interfaces.embedding_model import EmbeddingModel
from frame_finder.ml.interfaces.speech_transcriber import SpeechTranscriber
from frame_finder.pipeline.interfaces.query_classifier import QueryClassifier
from frame_finder.ml.interfaces.query_rewriter import QueryRewriter
from frame_finder.pipeline.interfaces.frame_processor import FrameProcessor
from frame_finder.pipeline.interfaces.embedding_ranker import EmbeddingRanker
from frame_finder.pipeline.interfaces.data_store import DataStore
from frame_finder.data_classes.transcript_segment import TranscriptSegment
from frame_finder.data_classes.indexed_video import IndexedVideo
from frame_finder.data_classes.query import Query
from frame_finder.data_classes.video_frame import VideoFrame
from frame_finder.data_classes.embeddable import Embeddable
from frame_finder.data_classes.video_data import VideoData
import numpy as np
import uuid

class Pipeline:
    def __init__(self, 
                 speech_transcriber: SpeechTranscriber, embedding_model: EmbeddingModel,
                 query_classifier: QueryClassifier, query_rewriter: QueryRewriter,
                 frame_processor: FrameProcessor, embedding_ranker: EmbeddingRanker,
                 data_store: DataStore
                 ):
        self._speech_transcriber = speech_transcriber
        self._embedding_model = embedding_model
        self._query_classifier = query_classifier
        self._query_rewriter = query_rewriter
        self._frame_processor = frame_processor
        self._embedding_ranker = embedding_ranker
        self._data_store = data_store

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
                    segment["text"],
                    segment["start"],
                    segment["end"],
                    embedding,
                )
            )

        return transcript_segments

    def process_frames(
        self,
        video_path: str,
        sample_rate: float,
    ) -> List[VideoFrame]:
        return self._frame_processor.process_frames(video_path, sample_rate)

    def rank_embeddings(
        self,
        query_embedding: np.ndarray,
        items: List[Embeddable],
    ) -> List[Embeddable]:
        return self._embedding_ranker.rank_embeddings(query_embedding, items)

    def extract_query_info(self, query: str) -> Query:
        rewritten_query = self._query_rewriter.rewrite(query)
        classification = self._query_classifier.classify(query)
        query_embedding = self._embedding_model.embed_text(rewritten_query)

        return Query(
            rewritten_query,
            classification,
            query_embedding
            )

    def get_ranked_video(self, formatted_query: Query, indexed_video: IndexedVideo) -> IndexedVideo:
        query_classification = formatted_query.classification
        ranked_transcript_segments, ranked_video_frames = [], []

        if query_classification == "speech" or query_classification == "both":
            ranked_transcript_segments = self.rank_embeddings(formatted_query.embedding, indexed_video.transcript_segments)
            print("Transcripts")
            print("-----------------------------------------------------------------------------------------------------")
            for segment in ranked_transcript_segments:
                print(segment.text + " ("  + str(segment.start) + "-" + str(segment.end) +")")

        if query_classification == "vision" or query_classification == "both":
            ranked_video_frames = self.rank_embeddings(formatted_query.embedding, indexed_video.video_frames)
            print("Frames")
            print("-----------------------------------------------------------------------------------------------------")

            for frame in ranked_video_frames:
                print(" ("  + str(frame.timestamp) +")")

        return IndexedVideo(ranked_transcript_segments, ranked_video_frames)

    def index_video(self, username: str, video_path: str) -> None:
        transcripted_segments = self.transcribe(video_path)["segments"]
        processed_frames = self.process_frames(video_path, 10)
        processed_segments = self.process_segments(transcripted_segments)
        indexed_video = IndexedVideo(processed_segments, processed_frames)
        video_id = str(uuid.uuid4())

        self._data_store.save(username, video_id, indexed_video)

    def load_video(self, username: str, video_id: str) -> VideoData:
        return self._data_store.load(username, video_id)

    def load_all(self, username: str) -> List[VideoData]:
        return self._data_store.load_all(username)
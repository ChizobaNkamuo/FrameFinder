from typing import List
import cv2
from frame_finder.data_classes.video_frame import VideoFrame
from frame_finder.ml.interfaces.embedding_model import EmbeddingModel
from frame_finder.ml.classes.clip_embedding_model import CLIPEmbeddingModel
from frame_finder.pipeline.interfaces.frame_processor import FrameProcessor

class OpenCVFrameProcessor(FrameProcessor):
    def __init__(self, embedding_model: EmbeddingModel):
        self._embedding_model = embedding_model

    def process_frames(
        self,
        video_path: str,
        sample_rate: float,
    ) -> List[VideoFrame]:
        capture = cv2.VideoCapture(video_path)

        if not capture.isOpened():
            raise ValueError(f"Could not open video: {video_path}")

        fps = capture.get(cv2.CAP_PROP_FPS)

        if fps <= 0:
            capture.release()
            raise ValueError("Video has an invalid FPS.")

        frame_interval = max(1, round(sample_rate * fps))

        video_frames: List[VideoFrame] = []

        frame_number = 0

        try:
            while True:
                success, frame = capture.read()

                if not success:
                    break

                if frame_number % frame_interval == 0:

                    timestamp = frame_number / fps

                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    embedding = self._embedding_model.embed_image(frame)

                    video_frames.append(
                        VideoFrame(
                            timestamp=timestamp,
                            embedding=embedding,
                        )
                    )

                frame_number += 1
        finally:
            capture.release()

        return video_frames
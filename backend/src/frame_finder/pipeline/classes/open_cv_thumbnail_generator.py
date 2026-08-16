from pathlib import Path
from backend.src.frame_finder.pipeline.interfaces.thumbnail_generator import ThumbnailGenerator
import cv2
import numpy as np

class OpenCVThumbnailGenerator(ThumbnailGenerator):
    def generate_thumbnail(self, video_path: Path) -> np.ndarray:
        capture = cv2.VideoCapture(str(video_path))

        if not capture.isOpened():
            raise ValueError(f"Could not open video: {video_path}")

        success, frame = capture.read()
        capture.release()

        if not success:
            raise ValueError(f"Could not read first frame: {video_path}")

        return frame
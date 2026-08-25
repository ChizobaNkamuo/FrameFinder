from pathlib import Path
from fastapi import UploadFile
import shutil

class TemporaryStorage:

    def __init__(
        self,
        root: Path,
    ):
        self._root = root

    def store(
        self,
        user_id: str,
        video_id: str,
        file: UploadFile,
    ) -> Path:

        directory = (
            self._root
            / user_id
            / video_id
        )

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        video_path = directory / file.filename

        with video_path.open("wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer,
            )

        return video_path

    def remove(
        self,
        video_path: Path,
    ) -> None:

        video_path.unlink(missing_ok=True)

        directory = video_path.parent

        while directory != self._root:
            try:
                directory.rmdir()
            except OSError:
                break

            directory = directory.parent
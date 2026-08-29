from src.frame_finder.pipeline.interfaces.file_downloader import FileDownloader
from pathlib import Path
import requests

class RequestsFileDownloader(FileDownloader):
    def download(
        self,
        url: str,
        destination: Path,
    ) -> None:

        with requests.get(
            url,
            stream=True,
        ) as response:

            response.raise_for_status()

            with destination.open("wb") as file:

                for chunk in response.iter_content(
                    chunk_size=1024 * 1024,
                ):
                    if chunk:
                        file.write(chunk)
from src.frame_finder.pipeline.interfaces.worker_queue import WorkerQueue
import requests


class RunpodQueue(WorkerQueue):
    def __init__(
        self,
        runpod_endpoint: str,
        runpod_api_key = str
    ):
        self._runpod_endpoint = runpod_endpoint
        self._api_key = runpod_api_key

    def enqueue(self, user_id: str, video_id: str) -> str:
        response = requests.post(
            self._runpod_endpoint,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._api_key}",
            },
            json={
                "input": {
                    "user_id": user_id,
                    "video_id": video_id,
                }
            },
        )

        response.raise_for_status()

        return response.json()["id"]
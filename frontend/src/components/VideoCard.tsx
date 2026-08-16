import type { LightVideoResponse } from "../interfaces/videos";
import "./VideoCard.css";
import { API_URL } from "../config";
import VideoStatus from "./VideoStatus";
import { useNavigate } from "react-router-dom";

interface VideoCardProps {
    video: LightVideoResponse;
}

export default function VideoCard({
    video
}: VideoCardProps) {
    const navigate = useNavigate();

    const processing = video.status === "processing";
    const complete = video.status === "complete";
    const thumbnail_url = video.thumbnail_url;

    function handleClick() {
        if (processing) {
            return;
        }

        navigate(`/videos/${video.video_id}`);
    }

    return (
        <div
            className={`video-card ${processing ? "video-card-processing" : ""}`}
            onClick={handleClick}
        >
            <div className="video-card-thumbnail">
                {thumbnail_url !== "" && (
                    <img
                        src={API_URL + thumbnail_url}
                        alt={video.filename}
                    />
                )}

                <div
                    className={`video-card-play ${
                        processing ? "video-card-play-loading" : ""
                    }`}
                >
                    <span>▶</span>
                </div>
            </div>

            <div className="video-card-info">
                <h3>{video.filename}</h3>

                {!complete && (
                    <VideoStatus
                        stage={video.stage}
                        status={video.status}
                    />
                )}
            </div>
        </div>
    );
}
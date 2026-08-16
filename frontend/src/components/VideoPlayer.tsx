import "./VideoPlayer.css";
import { API_URL } from "../config";

type VideoPlayerProps = {
    videoId: string;
    videoRef: React.RefObject<HTMLVideoElement | null>;
};

export default function VideoPlayer({
    videoId, videoRef
}: VideoPlayerProps) {
    const videoUrl =
        `${API_URL}/videos/Chizoba/${videoId}/file`;


    return (
        <div className="video-player">
            <video
                ref={videoRef}
                className="video-player-video"
                src={videoUrl}
                controls
            />
        </div>
    );
}
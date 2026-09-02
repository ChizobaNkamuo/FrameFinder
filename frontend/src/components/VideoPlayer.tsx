import "./VideoPlayer.css";
import { apiFetchWithAccessToken } from "../api/auth";
import { useEffect, useState } from "react";

type VideoPlayerProps = {
    videoId: string;
    videoRef: React.RefObject<HTMLVideoElement | null>;
};

export default function VideoPlayer({
    videoId, videoRef
}: VideoPlayerProps) {
    const [videoURL, setVideoURL] = useState<string| null>(null);

    async function fetchVideoURL(): Promise<void> {
        const response = await apiFetchWithAccessToken(
            `/videos/${videoId}`,
        )

        if (response.ok) {
            const videoUrl = await response.json()
            setVideoURL(videoUrl)
        }
    }

    useEffect(() => {
        fetchVideoURL()
    }, [videoId])

    return (
        <div className="video-player">
            <video
                ref={videoRef}
                className="video-player-video"
                src={videoURL ?? undefined}
                controls
            />
        </div>
    );
}
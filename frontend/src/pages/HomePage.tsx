import { useEffect, useState } from "react";
import { getVideos } from "../api/videos";
import type { LightVideoResponse, VideoUpdates } from "../interfaces/videos";
import VideoCard from "../components/VideoCard";
import Title from "../components/Title";
import SearchBar from "../components/SearchBar";
import UploadButton from "../components/UploadButton";
import "./HomePage.css";

function mergeVideos(
    current: LightVideoResponse[],
    latest: LightVideoResponse[]
): LightVideoResponse[] {
    const latestById = new Map(
        latest.map(video => [video.video_id, video])
    );

    const merged = current.map(video =>
        latestById.get(video.video_id) ?? video
    );

    const currentIds = new Set(
        current.map(video => video.video_id)
    );

    return [
        ...merged,
        ...latest.filter(video => !currentIds.has(video.video_id))
    ];
}

export default function HomePage() {
    const [videos, setVideos] = useState<LightVideoResponse[]>([]);
    const [pollingTrigger, setPollingTrigger] = useState(0);
    const [searchQuery, setSearchQuery] = useState("");

    useEffect(() => {
        
        let interval: number | undefined;

        async function fetchVideos() {
            const latest_videos = await getVideos();
            setVideos(prev => mergeVideos(prev, latest_videos));

            return latest_videos;
        }

        async function initialise() {
            const latest_videos = await fetchVideos();
            if (latest_videos.some(video => video.status === "processing")) {
                interval = window.setInterval(fetchVideos, 10000);
            }
        }

        initialise();

        return () => {
            if (interval !== undefined) {
                clearInterval(interval);
            }
        };
    }, [pollingTrigger]);


    return (
        <div>
            <Title>
                FrameFinder
            </Title>
            
            <SearchBar onSearch={setSearchQuery} processing={false} searchOnChange={true}/>
            <h3>Your Videos</h3>
            <div className="video-grid">
                <UploadButton
                    onUpload={(video: LightVideoResponse) => {
                        setVideos(prev => [...prev, video]);
                    }}
                    UpdateVideo={(old_id: string, updates: VideoUpdates) => {
                        setVideos(prev =>
                            prev.map(video =>
                                video.video_id === old_id
                                    ? { ...video, ...updates }
                                    : video
                            )
                        );
                    }}
                    StartPoll = {() => setPollingTrigger(prev => prev + 1)}
                />

                {[...videos]
                    .filter(
                        v => v.filename.toLowerCase().includes(searchQuery)
                    ).sort((a, b) =>
                        new Date(a.created_at).getTime() -
                        new Date(b.created_at).getTime()
                    ).map(video => (
                    <VideoCard
                        key={video.video_id}
                        video={video}
                    />
                ))}
            </div>
        </div>
    );
}
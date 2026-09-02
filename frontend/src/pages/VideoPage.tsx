import { useParams } from "react-router-dom";
import { useState, useRef } from "react";

import BackButton from "../components/BackButton";
import VideoPlayer from "../components/VideoPlayer";
import SearchBar from "../components/SearchBar";
import SearchResults from "../components/SearchResults";
import { getSearchQueryResult } from "../api/videos";

import "./VideoPage.css";
import type { SearchResponse } from "../interfaces/videos";

export default function VideoPage() {
    const { videoId } = useParams<{ videoId: string }>();
    const [queryResults, setQueryResults] = useState<SearchResponse>();
    const [processingQuery, setProcessingQuery] = useState<boolean>(false);
    const [failedQuery, setfailedQuery] = useState<boolean>(false);
    const videoRef = useRef<HTMLVideoElement>(null);

    if (videoId === undefined) {
        return <div>Video not found.</div>;
    }

    async function fetchSearchResult(newQuery: string) {
        setProcessingQuery(true);
        setfailedQuery(false);
        setQueryResults(undefined);
        
        try {
            const latest_results = await getSearchQueryResult(
                videoId!,
                newQuery,
                10
            );
            setQueryResults(latest_results);
        }
        catch (error) {
            setfailedQuery(true);
        }

        setProcessingQuery(false);
    }

    async function handleTimestampClick(timestamp: number) {
        const video = videoRef.current;

        if (!video) {
            return;
        }

        video.currentTime = timestamp;

        try {
            await video.play();
        } catch (error) {
            console.error("Could not play video:", error);
        }
    }    

    return (
        <div className="video-page">
            <BackButton />

            <main className="video-page-content">
                <VideoPlayer videoId={videoId ?? null} videoRef={videoRef}/>

                <SearchBar onSearch={fetchSearchResult} processing={processingQuery} searchOnChange={false} />

                <SearchResults
                searchResponses={queryResults}
                failedQuery={failedQuery}
                onTimestampClick={(newTimeStamp) => {
                    handleTimestampClick(newTimeStamp);
                }}
                />
            </main>
        </div>
    );
}
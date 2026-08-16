import type { SearchResponse } from "../interfaces/videos";
import "./SearchResults.css";

type SearchResultsProps = {
    searchResponses: SearchResponse | undefined;
    onTimestampClick: (timestamp: number) => void;
    failedQuery: boolean;
};

function formatTimestamp(timestamp: number): string {
    const totalSeconds = Math.floor(timestamp);

    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;

    if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, "0")}:${seconds
            .toString()
            .padStart(2, "0")}`;
    }

    return `${minutes}:${seconds.toString().padStart(2, "0")}`;
}

function GetEmptyResults(failedQuery: boolean) {
    return (
        <div className="search-results">
            <div className="search-results-empty">
                {failedQuery ?
                "Could not fetch search results":
                "No results found"}
            </div>
        </div>
    );   
}

export default function SearchResults({
    searchResponses,
    onTimestampClick,
    failedQuery
}: SearchResultsProps) {
    if (!searchResponses) {
        return GetEmptyResults(failedQuery);
    }

    const transcriptResults = searchResponses.transcript_segments;
    const videoFrameResults = searchResponses.video_frames;

    const hasResults =
        transcriptResults.length > 0 ||
        videoFrameResults.length > 0;

    if (!hasResults) {
        return GetEmptyResults(failedQuery)
    }

    return (
        <div className="search-results">
            {transcriptResults.length > 0 && (
                <section className="search-results-section">
                    <h3>Transcript</h3>

                    <div className="search-results-list">
                        {transcriptResults.map((segment, index) => (
                            <div
                                className="search-result transcript-result"
                                key={`transcript-${segment.timestamp}-${index}`}
                            >
                                <button
                                    className="search-result-timestamp"
                                    type="button"
                                    onClick={() =>
                                        onTimestampClick(segment.timestamp)
                                    }
                                >
                                    {formatTimestamp(segment.timestamp)}
                                </button>

                                <p>{segment.text}</p>
                            </div>
                        ))}
                    </div>
                </section>
            )}

            {videoFrameResults.length > 0 && (
                <section className="search-results-section">
                    <h3>Visual Results</h3>

                    <div className="search-results-list">
                        {videoFrameResults.map((frame, index) => (
                            <div
                                className="search-result visual-result"
                                key={`frame-${frame.timestamp}-${index}`}
                            >
                                <button
                                    className="search-result-timestamp"
                                    type="button"
                                    onClick={() =>
                                        onTimestampClick(frame.timestamp)
                                    }
                                >
                                    {formatTimestamp(frame.timestamp)}
                                </button>
                            </div>
                        ))}
                    </div>
                </section>
            )}
        </div>
    );
}
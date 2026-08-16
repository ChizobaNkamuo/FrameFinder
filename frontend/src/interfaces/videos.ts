export interface LightVideoResponse {
    video_id: string;
    filename: string;
    thumbnail_url: string;
    status: string;
    stage: string;
    created_at: string;
}

export interface UploadResponse {
    video_id: string;
}

export type VideoUpdates = Partial<LightVideoResponse>;

export interface SearchResponse {
    video_frames: VideoFrame[];
    transcript_segments: TranscriptSegment[];
}

export interface TranscriptSegment {
    timestamp: number;
    text: string;
}

export interface VideoFrame {
    timestamp: number;
}
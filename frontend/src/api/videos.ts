import type { LightVideoResponse, SearchResponse, UploadResponse} from "../interfaces/videos";
import { apiFetchWithAccessToken } from "./auth";

export async function getVideos(): Promise<LightVideoResponse[]> {
    const response = await apiFetchWithAccessToken(`/videos`);

    if (!response.ok) {
        throw new Error("Failed to fetch videos");
    }

    return response.json();
}


export async function uploadVideo(
    file: File
): Promise<UploadResponse> {
    const formData = new FormData();

    formData.append("file", file);

    const response = await apiFetchWithAccessToken(
        `/index/upload`,
        {
            method: "POST",
            body: formData,
        }
    );

    if (!response.ok) {
        throw new Error("Failed to upload video");
    }

    return response.json();
}

export async function getSearchQueryResult(
    video_id: string,
    query: string,
    top_k: number
): Promise<SearchResponse> {

    const params = new URLSearchParams({
        query,
        top_k: top_k.toString(),
    });

    const response = await apiFetchWithAccessToken(
        `/search/${video_id}?${params.toString()}`,
        {
            method: "POST",
        }
    );

    if (!response.ok) {
        throw new Error("Failed to search query");
    }

    return response.json();
}
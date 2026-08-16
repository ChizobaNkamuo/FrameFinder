import type { LightVideoResponse, SearchResponse, UploadResponse} from "../interfaces/videos";
import { apiFetch } from "./client";

export async function getVideos(
    username: string
): Promise<LightVideoResponse[]> {
    
    const response = await apiFetch(`/videos/${username}`);

    if (!response.ok) {
        throw new Error("Failed to fetch videos");
    }

    return response.json();
}


export async function uploadVideo(
    username: string, 
    file: File
): Promise<UploadResponse> {
    const formData = new FormData();

    formData.append("file", file);

    const response = await apiFetch(
        `/index/upload/${username}`,
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
    username: string,
    video_id: string,
    query: string,
    top_k: number
): Promise<SearchResponse> {

    const params = new URLSearchParams({
        query,
        top_k: top_k.toString(),
    });

    const response = await apiFetch(
        `/search/${username}/${video_id}?${params.toString()}`,
        {
            method: "POST",
        }
    );

    if (!response.ok) {
        throw new Error("Failed to search query");
    }

    return response.json();
}
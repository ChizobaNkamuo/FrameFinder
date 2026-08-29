import { API_URL } from "../config";

export async function apiFetch(
    endpoint: string,
    options?: RequestInit,
) {
    console.log(`${API_URL}${endpoint}`);
    return fetch(`${API_URL}${endpoint}`, options);
}
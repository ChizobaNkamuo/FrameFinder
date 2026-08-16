import { API_URL } from "../config";

export async function apiFetch(
    endpoint: string,
    options?: RequestInit,
) {
    return fetch(`${API_URL}${endpoint}`, options);
}
import type { AuthResponse } from "../interfaces/auth";
import { API_URL } from "../config";
import { apiFetch } from "./client";

function saveSession(authResponse: AuthResponse) {
    localStorage.setItem(
        "session",
        JSON.stringify(authResponse),
    )
}

function clearSession() {
    localStorage.removeItem("session");
}

export function loadSession(): AuthResponse | null {
    const storedSession = localStorage.getItem("session")

    if (!storedSession) {
        return null
    }

    return JSON.parse(storedSession)
}

export function isTokenExpired(
    token: string,
    bufferSeconds = 30,
): boolean {
    const payload = JSON.parse(
        atob(token.split(".")[1])
    )

    const expiresAt =
        payload.exp * 1000

    return expiresAt <=
        Date.now() + bufferSeconds * 1000
}

async function refreshSession(
    refresh_token: string,
): Promise<AuthResponse> {
    const params = new URLSearchParams({
        refresh_token
    });

    const response = await apiFetch(
        `/auth/refresh?${params.toString()}`,
        {
            method: "POST",
        });

    if (!response.ok) {
        clearSession();
        window.dispatchEvent(
            new Event("auth-failure")
        );
        throw new Error("Authentication failed");
    }

    return response.json()
}

async function getAccessToken(): Promise<string | void> {
    var session = loadSession();
    if (!session) {
        window.dispatchEvent(
            new Event("auth-failure")
        );
        return;
    }

    if (isTokenExpired(session.access_token)) {
        session = await refreshSession(session.refresh_token);
        saveSession(session);
    }
  
    return session.access_token
}


export async function login(
    email: string,
    password: string) 
{
    const params = new URLSearchParams({
        email,
        password,
    });

    const response = await apiFetch(
        `/auth/login?${params.toString()}`,
        {
            method: "POST",
        });

    if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail.message);
    }

    const result = await response.json();
    saveSession(result);
}

export async function signup(
    email: string,
    password: string,
) {
    const params = new URLSearchParams({
        email,
        password,
    });

    const response = await apiFetch(
        `/auth/signup?${params.toString()}`,
        {
            method: "POST",
        });

    if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail.message);
    }

    const result = await response.json();
    saveSession(result);
}

export async function apiFetchWithAccessToken(
    path: string,
    options: RequestInit = {},
): Promise<Response> {
    const accessToken = await getAccessToken()

    return fetch(
        `${API_URL}${path}`,
        {
            ...options,
            headers: {
                ...options.headers,
                Authorization: `Bearer ${accessToken}`,
            },
        },
    )
}
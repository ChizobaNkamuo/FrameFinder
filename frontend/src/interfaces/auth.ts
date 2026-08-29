export interface User {
    id: string;
    email: string;
}

export interface AuthResponse {
    email: string;
    access_token: string;
    refresh_token: string;
}

import { BrowserRouter, Routes, Route, useNavigate, Outlet, Navigate } from "react-router-dom";
import HomePage from "./pages/HomePage";
import VideoPage from "./pages/VideoPage";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./main.css";
import LoginPage from "./pages/LoginPage";
import SignUpPage from "./pages/SignUpPage";
import { useEffect } from "react";
import { loadSession, isTokenExpired } from "./api/auth";

function RequireAuth() {
    const session = loadSession()

    if (!session || isTokenExpired(session.access_token)) {
        return <Navigate to="/" replace />
    }

    return <Outlet />
}

export default function App() {
    const navigate = useNavigate()

    useEffect(() => {
        const handleAuthFailure =
            () => navigate("/");

        window.addEventListener(
            "auth-failure",
            handleAuthFailure,
        )

        return () => {
            window.removeEventListener(
                "auth-failure",
                handleAuthFailure,
            )
        }
    }, [navigate])
    return (
            <Routes>
                <Route path="/" element={<LoginPage />} />
                <Route path="/signup" element={<SignUpPage />} />
                <Route element={<RequireAuth />}>
                    <Route path="/home" element={<HomePage />} />
                    <Route path="/videos/:videoId" element={<VideoPage />} />               
                </Route>
            </Routes>
    );
}

createRoot(document.getElementById("root")!).render(
    <StrictMode>
        <BrowserRouter>
            <App />
        </BrowserRouter>
    </StrictMode>
);
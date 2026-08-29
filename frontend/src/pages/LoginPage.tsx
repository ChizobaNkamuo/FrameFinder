import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Layers2, Eye } from "lucide-react";

import { login } from "../api/auth";
import "./AuthPage.css";

export default function LoginPage() {
    const navigate = useNavigate();

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const [error, setError] = useState("");
    const [processing, setProcessing] = useState(false);

    async function handleSubmit(event: FormEvent) {
        event.preventDefault();

        setError("");
        setProcessing(true);

        try {
            await login(
                email,
                password,
            );

            navigate("/home");
        } catch (error) {
            if (error instanceof Error) {
                setError(error.message)
            }

        } finally {
            setProcessing(false);
        }
    }

    return (
        <div className="auth-page">
            <div className="auth-card">
                <div className="auth-header">
                    <div className="auth-logo">
                        <Layers2 size={22} />
                    </div>

                    <h1>FrameFinder</h1>

                    <p>
                        Access your videos and search securely
                    </p>
                </div>

                <form
                    className="auth-form"
                    onSubmit={handleSubmit}
                >
                    <label>
                        Email

                        <input
                            type="email"
                            placeholder="Enter your email"
                            value={email}
                            onChange={event =>
                                setEmail(event.currentTarget.value)
                            }
                            required
                        />
                    </label>

                    <label>
                        Password

                        <div className="auth-password-input">
                            <input
                                type="password"
                                placeholder="Enter your password"
                                value={password}
                                onChange={event =>
                                    setPassword(event.currentTarget.value)
                                }
                                required
                            />

                            <Eye size={18} />
                        </div>
                    </label>

                    <div className="auth-options">
                        <label className="auth-checkbox">
                            <input type="checkbox" />

                            <span>Remember me</span>
                        </label>

                        <button
                            type="button"
                            className="auth-text-button"
                        >
                            Forgot password?
                        </button>
                    </div>

                    {error && (
                        <p className="auth-error">
                            {error}
                        </p>
                    )}

                    <button
                        type="submit"
                        className="auth-submit-button"
                        disabled={processing}
                    >
                        {processing
                            ? "Signing in..."
                            : "Sign In"
                        }
                    </button>
                </form>

                <p className="auth-switch">
                    Don't have an account?{" "}

                    <Link to="/signup">
                        Sign up
                    </Link>
                </p>
            </div>
        </div>
    );
}
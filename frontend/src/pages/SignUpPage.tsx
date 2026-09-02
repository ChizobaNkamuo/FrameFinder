import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Layers2, Eye, EyeOff } from "lucide-react";

import { signup } from "../api/auth";
import "./AuthPage.css";

export default function SignUpPage() {
    const navigate = useNavigate();

    const [email, setEmail] = useState("");

    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");

    const [error, setError] = useState("");
    const [processing, setProcessing] = useState(false);
    const [passwordHidden, setPasswordHidden] = useState(true);
    const [confirmPasswordHidden, setConfirmPasswordHidden] = useState(true);

    async function handleSubmit(event: FormEvent) {
        event.preventDefault();

        setError("");

        if (password !== confirmPassword) {
            setError("Passwords do not match.");
            return;
        }

        setProcessing(true);

        try {
            await signup(
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

                    <h1>Create an account</h1>

                    <p>
                        Create an account to start searching
                        your videos
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
                                type={passwordHidden ? "password" : "text"}
                                placeholder="Create a password"
                                value={password}
                                onChange={event =>
                                    setPassword(event.currentTarget.value)
                                }
                                required
                            />

                            <button
                                type="button"
                                onClick={() => setPasswordHidden(hidden => !hidden)}
                                aria-label={passwordHidden ? "Show password" : "Hide password"}
                            >
                                {passwordHidden
                                    ? <Eye size={18} />
                                    : <EyeOff size={18} />
                                }
                            </button>
                        </div>   
                    </label>

                    <label>
                        Confirm password

                        <div className="auth-password-input">
                            <input
                                type={confirmPasswordHidden ? "password" : "text"}
                                placeholder="Confirm your password"
                                value={confirmPassword}
                                onChange={event =>
                                    setConfirmPassword(event.currentTarget.value)
                                }
                                required
                            />

                            <button
                                type="button"
                                onClick={() => setConfirmPasswordHidden(hidden => !hidden)}
                                aria-label={confirmPasswordHidden ? "Show password" : "Hide password"}
                            >
                                {confirmPasswordHidden
                                    ? <Eye size={18} />
                                    : <EyeOff size={18} />
                                }
                            </button>
                        </div>   
                    </label>

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
                            ? "Creating account..."
                            : "Sign Up"
                        }
                    </button>
                </form>

                <p className="auth-switch">
                    Already have an account?{" "}

                    <Link to="/">
                        Sign in
                    </Link>
                </p>
            </div>
        </div>
    );
}
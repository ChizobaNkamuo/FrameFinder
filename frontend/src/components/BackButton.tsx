import { ArrowLeft } from "lucide-react";

import "./BackButton.css";

export default function BackButton() {
    return (
        <button
            className="back-button"
            type="button"
            onClick={() => window.history.back()}
        >
            <ArrowLeft size={18} />
            <span>Back to Videos</span>
        </button>
    );
}
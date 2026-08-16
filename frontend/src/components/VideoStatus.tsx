import "./VideoStatus.css";
import { CircleX } from "lucide-react";

interface VideoStatusProps {
    status: string;
    stage: string;
}

export default function VideoStatus({ status, stage }: VideoStatusProps) {
    var failed = status == "failed";

    return (
        <div className="video-status">
            {failed ? 
            <CircleX className="video-status-failed-icon"/>:
            <span className="video-status-spinner" />
            }
            <span className={failed ? "video-status-failed" : ""}>{stage}</span>
        </div>
    );
}
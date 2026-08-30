import { useRef } from "react";
import { Upload } from "lucide-react";
import "./UploadButton.css";
import { uploadVideo } from "../api/videos";
import type { LightVideoResponse, VideoUpdates } from "../interfaces/videos";

type UploadButtonProps = {
    onUpload: (video: LightVideoResponse) => void;
    StartPoll: () => void;
    UpdateVideo: (old_id: string, new_id: VideoUpdates) => void;
};

const MAX_FILE_SIZE = 50 * 1024 * 1024;

export default function UploadButton({onUpload, StartPoll, UpdateVideo}: UploadButtonProps) {
    const inputRef = useRef<HTMLInputElement>(null);

    function handleClick() {
        inputRef.current?.click();
    }

    async function handleFileChange(
        event: React.ChangeEvent<HTMLInputElement>
    ) {
        const selectedFile = event.target.files?.[0] ?? null;
        if (selectedFile == null) {
            return;
        }
        
        if (selectedFile.size > MAX_FILE_SIZE) {
            alert("Video must be smaller than 50 MB.");
            event.target.value = "";
            return;
        }

        var current_time = Date.now().toString();
        onUpload({
            video_id: current_time,
            filename: selectedFile.name,
            thumbnail_url: "",
            status: "processing",
            stage: "Uploading...",
            created_at: current_time
        });
        
        try {
            var result = await uploadVideo(selectedFile);

            const updates: VideoUpdates = {
                video_id: result.video_id
            };                
            UpdateVideo(current_time, updates);
            StartPoll();
        } catch (error) {
            const updates: VideoUpdates = {
                status: "failed",
                stage: "Upload failed",
            };     

            UpdateVideo(current_time, updates);
        }
        
    }

    return (
        <>
            <button
                className="upload-button"
                type="button"
                onClick={handleClick}
            >
                <Upload size={24} />

                <span>Upload Video</span>
            </button>

            <input
                ref={inputRef}
                type="file"
                accept="video/*"
                onChange={handleFileChange}
                hidden
            />
        </>
    );
}
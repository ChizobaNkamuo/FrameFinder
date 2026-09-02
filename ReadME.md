# FrameFinder

FrameFinder is a semantic video search application that allows users to upload videos and search for specific moments using natural-language queries. The system combines speech and visual information to find relevant points in a video, returning matching transcript segments and video frames.

You can try it [here](https://framefinder.up.railway.app/).

## Search Pipeline

A video is processed into two complementary forms of information:

- **Speech:** Whisper transcribes the video's audio into timestamped segments.
- **Vision:** Frames are sampled from the video and converted into CLIP embeddings.

When a user searches, the query is classified to determine if speech or visual searching (or both) should be used. The query is then rewritten using a small local LLM and embedded before being compared against the stored video embeddings. The most relevant transcript segments and video frames are then returned to the frontend.

# Architecture

FrameFinder is split into three main components:

- **Frontend:** Communicates with the FastAPI backend, which handles authentication, video management and search requests.
- **Video processing:** Performed asynchronously by a GPU-backed RunPod Serverless worker. This keeps computationally expensive ML workloads separate from the main API server.
- **Pipeline:** The backend uses a pipeline architecture to separate the different stages of processing and searching.

## Technologies

### Frontend

- React
- TypeScript

### Backend

- Python
- FastAPI
- Uvicorn

### Machine Learning

- **Whisper** - Speech transcription
- **CLIP** - Visual and text embeddings
- **Ollama** - Local LLM-based query rewriting
- **PyTorch** - Model inference

### Infrastructure

- **Supabase** - Authentication, database and object storage
- **RunPod Serverless** - GPU-based background video processing
- **Redis / RQ** - Background job queueing during development
- **Docker** - Containerisation
- **Railway** - Application hosting
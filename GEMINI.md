# Gemini Project: YouTube Transcript

## Project Overview

This project, "Gospel Keys," is a web application designed to transcribe and analyze music, particularly from YouTube videos. It leverages a sophisticated pipeline to process audio, separate piano tracks, transcribe them to MIDI, and perform musical analysis like chord detection.

The application is a monorepo with a frontend built using **React**, **Vite**, **TanStack Router**, **TanStack Query**, and **Zustand**. The backend is a **Python** service powered by **FastAPI**, which orchestrates a pipeline of audio processing and machine learning tools.

### Key Technologies:

*   **Frontend**: React, Vite, TanStack Router, TanStack Query, Zustand, Tailwind CSS
*   **Backend**: Python, FastAPI, uvicorn
*   **Audio Pipeline**: yt-dlp, ffmpeg, Demucs, basic-pitch, librosa
*   **Database**: PostgreSQL (with Redis for caching) - planned for future phases
*   **Containerization**: Docker, Docker Compose
*   **Testing**: Playwright for end-to-end tests

## Building and Running

The project is containerized using Docker and can be run with Docker Compose. There are separate configurations for production and development.

### Development (with Hot-Reloading)

To run the application in a development environment with hot-reloading for both the frontend and backend:

```bash
# Start the services in detached mode
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d

# To stop the services
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down
```

*   **Frontend**: Accessible at `http://localhost:3000`
*   **Backend**: Accessible at `http://localhost:8009`
*   **API Docs**: View the backend API documentation at `http://localhost:8009/docs`

### Production

To build and run the production version of the application:

```bash
# Start the services in detached mode
docker-compose up --build -d

# To stop the services
docker-compose down
```

## Development Conventions

*   **Monorepo Structure**: The project is organized as a monorepo with separate `frontend` and `backend` directories.
*   **State Management**: The frontend uses a combination of **Zustand** for global state and **TanStack Query** for managing server state, including caching and polling for transcription job status.
*   **API Communication**: The frontend communicates with the backend via a typed API client, with clear data contracts defined in both the frontend and backend.
*   **Asynchronous Operations**: The backend uses a pipeline model to handle long-running transcription jobs, with a job queue and status polling mechanism.
*   **Testing**: End-to-end tests are implemented with **Playwright**. Unit and integration tests are also present in both the frontend and backend.
*   **Styling**: The frontend uses **Tailwind CSS** for styling.

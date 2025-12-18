# Deployment Guide

Since your application is a **Full Stack App** (Frontend + Backend + Database), you cannot simply use GitHub Pages (which only supports static sites). You need a server to run the Python Backend and the Database.

Here are the best ways to deploy your app for a demo.

## Option 1: Render.com (Recommended for Free Demo)
Render allows you to deploy all 3 components easily from your GitHub repository.

### Prerequisites
1.  Create a GitHub Repository and push this code.
2.  Sign up for [Render.com](https://render.com).

### Steps
1.  **Database (PostgreSQL)**:
    *   New + -> PostgreSQL.
    *   Name: `db-platform`.
    *   Copy the `Internal DB URL`.

2.  **Backend (Web Service)**:
    *   New + -> Web Service.
    *   Connect your GitHub Repo.
    *   Root Directory: `.` (or leave empty).
    *   Runtime: **Python 3**.
    *   Build Command: `pip install -r requirements.txt`.
    *   Start Command: `uvicorn app.main:app --host 0.0.0.0 --port 10000`.
    *   **Environment Variables**:
        *   `DATABASE_URL`: Paste the Internal DB URL from step 1 (modify `postgres://` to `postgresql://` if needed).

3.  **Frontend (Static Site)**:
    *   New + -> Static Site.
    *   Connect your GitHub Repo.
    *   Root Directory: `frontend`.
    *   Build Command: `npm install && npm run build`.
    *   Publish Directory: `dist`.
    *   **Environment Variables**:
        *   `VITE_API_URL`: The URL of your Backend Web Service (e.g., `https://backend-xyz.onrender.com`).

## Option 2: Docker (If you have a server/VPS)
If you have a server (AWS EC2, DigitalOcean), you can run everything with one command.

1.  Current `docker-compose.yaml` only runs Backend + DB.
2.  You would need to add the frontend service to `docker-compose.yaml` (I can help with this if you choose this path).
3.  Run `docker-compose up -d --build`.

## Option 3: Local Demo (Ngrok)
If you just want to show it *from your computer* to your boss remotely without deploying:
1.  Run the app locally.
2.  Use **ngrok** to expose your localhost ports (Frontend 5173 / Backend 8000) to the internet.

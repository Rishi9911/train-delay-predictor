# Deployment Guide

## 1. Prerequisites
- [GitHub Account](https://github.com/)
- [Render Account](https://render.com/) (for Backend)
- [Neon Account](https://neon.tech/) (for Database)
- [Vercel Account](https://vercel.com/) (for Frontend)

## 2. Database (Neon)
1.  Create a new project in Neon.
2.  Copy the **Connection String** (e.g., `postgresql://user:pass@ep-xyz.aws.neon.tech/neondb`).
3.  Go to the **SQL Editor** in Neon and run the SQL commands to create your tables (`users`, `predictions`).

## 3. Backend (Render)
1.  Click **New +** -> **Web Service**.
2.  Connect your GitHub repo `train-delay-predictor`.
3.  **Root Directory**: `backend`
4.  **Runtime**: Python
5.  **Build Command**: `pip install -r requirements.txt`
6.  **Start Command**: `gunicorn app:app`
7.  **Environment Variables** (Add these):
    -   `DATABASE_URL`: (Paste your Neon connection string)
    -   `SECRET_KEY`: (Generate a random string)
    -   `FRONTEND_URL`: `https://your-vercel-app.vercel.app` (You will update this later after deploying frontend)
    -   `MAIL_PASSWORD`: (Your App Password)
    -   `MAIL_USERNAME`: (Your email)

## 4. Frontend (Vercel)
1.  Click **Add New...** -> **Project**.
2.  Import `train-delay-predictor`.
3.  **Framework Preset**: Create React App.
4.  **Root Directory**: `frontend`.
5.  **Environment Variables**:
    -   `REACT_APP_API_URL`: (Copy the Render Backend URL, e.g., `https://train-delay-backend.onrender.com`. **Important**: Do not add a trailing slash `/`).
6.  Click **Deploy**.

## 5. Final Connection
1.  Once Vercel is deployed, copy the URL (e.g., `https://train-delay-predictor.vercel.app`).
2.  Go back to **Render Dashboard** -> **Environment Variables**.
3.  Update the `FRONTEND_URL` to match your Vercel URL exactly.
4.  Render will redeploy automatically.

## 6. Testing
- Go to your Vercel URL.
- Register a new user.
- Try a prediction.

# AI Research Assistant

This is an AI-powered Research Assistant web application utilizing FastAPI for the backend and React/Vite/TypeScript for the frontend.

## Prerequisites

- Python 3.10+
- Node.js & npm

## Local Development Setup

### 1. Backend Setup

1. Navigate to the project root directory.
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables. Copy `.env.example` to `.env` and fill in the required keys:
   ```bash
   cp .env.example .env
   ```
5. Start the FastAPI backend:
   ```bash
   uvicorn app.main:app --reload
   ```
   The backend will be running at `http://localhost:8000`.

### 2. Frontend Setup

1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Configure environment variables. Copy `.env.example` (or configure `.env`) with the backend API URL:
   ```bash
   # Create/Update .env file in frontend directory
   VITE_API_URL=http://localhost:8000
   ```
4. Start the frontend development server:
   ```bash
   npm run dev
   ```
   The frontend will be running at `http://localhost:5173`.

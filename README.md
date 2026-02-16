# Chord Tracker

## Running Locally

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js (with npm)

### 1. Start the Database

```sh
docker compose up -d
```

This starts a PostgreSQL 16 instance on port 5432.

### 2. Start the Backend

```sh
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload
```

The API server runs at http://localhost:8000. You can view the interactive docs at http://localhost:8000/docs.

### 3. Start the Frontend

```sh
cd frontend
npm install
npm run dev
```

The Vite dev server runs at http://localhost:5173 and proxies `/api` requests to the backend.

## Appendix

- [Ralph](https://github.com/snarktank/ralph)

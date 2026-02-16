# Chord Tracker

## Running with Docker

### Prerequisites

- Docker and Docker Compose

### Start the full stack

```sh
docker compose up -d --build
```

- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs

To stop everything:

```sh
docker compose down
```

## Running Locally (without Docker)

### Prerequisites

- Docker and Docker Compose (for PostgreSQL)
- Python 3.11+
- Node.js (with npm)

### 1. Start the Database

```sh
docker compose up -d postgres
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

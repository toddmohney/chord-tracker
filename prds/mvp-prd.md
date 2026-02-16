# Chord Tracker — Product Requirements Document

## 1. Product Overview

**Chord Tracker** is a SaaS web application that enables musicians to visually build, save, and organize guitar chord diagrams. Users interact with an on-screen guitar neck to place finger markers on strings and frets, constructing chords that are saved into ordered sequences within songs.

**Target users:** Guitar players and musicians who want a visual tool for documenting chord progressions.

## 2. Tech Stack

| Layer      | Technology            |
|------------|-----------------------|
| Frontend   | React + TypeScript (Vite) |
| Backend    | Python + FastAPI      |
| Database   | PostgreSQL            |
| Auth       | JWT (access + refresh tokens) |

## 3. Information Architecture

```
User
 └── Project
      └── Song
           └── Chord (ordered sequence)
```

### Data Model

**User**
- id (UUID)
- email (unique)
- password_hash
- created_at

**Project**
- id (UUID)
- user_id (FK → User)
- name
- created_at, updated_at

**Song**
- id (UUID)
- project_id (FK → Project)
- name
- created_at, updated_at

**Chord**
- id (UUID)
- song_id (FK → Song)
- position (integer — order within the song)
- name (optional, e.g. "Am7")
- string_count (integer, default 6)
- tuning (string, default "EADGBE")
- markers (JSON array of {string, fret} objects)

## 4. Core Features (MVP)

### 4.1 User Authentication
- Sign up with email and password
- Log in / log out
- JWT-based session management (access token + refresh token)
- Protected API routes and frontend route guards

### 4.2 Project Management
- Create, rename, and delete projects
- List all projects for the logged-in user

### 4.3 Song Management
- Create, rename, and delete songs within a project
- List all songs in a project

### 4.4 Guitar Neck Editor
- Interactive UI component rendering a section of a guitar neck (frets and strings)
- Configurable number of strings (default: 6)
- Configurable tuning (default: EADGBE)
- Tap/click a fret-string intersection to place or remove a marker
- Visual display of placed markers on the neck
- Displays string labels based on current tuning

### 4.5 Chord Sequencing
- Add a new chord to a song (opens the guitar neck editor)
- Optionally name each chord
- Reorder chords within a song (drag-and-drop or move up/down)
- Remove a chord from a song
- View the full chord sequence for a song

### 4.6 Data Persistence
- All data persisted to PostgreSQL via REST API
- API follows RESTful conventions with JSON request/response bodies

## 5. API Endpoints

### Auth
| Method | Path              | Description         |
|--------|-------------------|---------------------|
| POST   | /auth/register    | Create new account  |
| POST   | /auth/login       | Log in, get tokens  |
| POST   | /auth/refresh     | Refresh access token|

### Projects
| Method | Path                  | Description           |
|--------|-----------------------|-----------------------|
| GET    | /projects             | List user's projects  |
| POST   | /projects             | Create a project      |
| GET    | /projects/:id         | Get a project         |
| PUT    | /projects/:id         | Update a project      |
| DELETE | /projects/:id         | Delete a project      |

### Songs
| Method | Path                          | Description          |
|--------|-------------------------------|----------------------|
| GET    | /projects/:id/songs           | List songs in project|
| POST   | /projects/:id/songs           | Create a song        |
| GET    | /songs/:id                    | Get a song           |
| PUT    | /songs/:id                    | Update a song        |
| DELETE | /songs/:id                    | Delete a song        |

### Chords
| Method | Path                          | Description               |
|--------|-------------------------------|---------------------------|
| GET    | /songs/:id/chords             | List chords in a song     |
| POST   | /songs/:id/chords             | Add a chord to a song     |
| PUT    | /chords/:id                   | Update a chord            |
| DELETE | /chords/:id                   | Delete a chord            |
| PUT    | /songs/:id/chords/reorder     | Reorder chords in a song  |

## 6. Implementation Steps

### Step 1: Project Scaffolding
- Initialize a monorepo or two-directory structure: `frontend/` and `backend/`
- Frontend: scaffold with Vite + React + TypeScript; install router (react-router), HTTP client (axios or fetch wrapper), and a CSS approach (CSS modules, Tailwind, or similar)
- Backend: scaffold FastAPI project with uvicorn; set up project structure (routers, models, schemas, database)
- Set up linting and formatting for both (ESLint/Prettier for frontend, Ruff for backend)
- Add a `docker-compose.yml` for PostgreSQL (dev environment)

### Step 2: Database Schema and Migrations
- Choose a migration tool (Alembic)
- Define SQLAlchemy models for User, Project, Song, Chord
- Create initial migration
- Seed script (optional) for development data

### Step 3: Authentication
- Backend: implement register, login, and refresh endpoints; password hashing (bcrypt); JWT creation and validation middleware
- Frontend: build sign-up and login pages; store tokens; add auth context/provider; implement route guards for protected pages

### Step 4: Project and Song CRUD
- Backend: implement REST endpoints for projects and songs with ownership checks
- Frontend: build project list page, project detail page (shows songs), song detail page
- Wire up API calls

### Step 5: Guitar Neck Component
- Build an SVG-based React component that renders a configurable guitar neck
- Accept props: `stringCount`, `tuning`, `markers`, `onMarkerToggle`
- Render frets (at least 5 visible, scrollable or paginated for more), strings, nut, and string labels
- Handle click events on fret-string intersections to toggle markers
- Display placed markers as circles/dots on the neck

### Step 6: Chord Model and Sequencing
- Backend: implement chord CRUD and reorder endpoints
- Frontend: build chord list view within a song; integrate guitar neck editor for creating/editing chords; implement reorder functionality (drag-and-drop or buttons)

### Step 7: Integration and Wiring
- Connect the guitar neck editor to the chord API (save/load markers)
- Ensure navigation flow: Projects → Songs → Chords → Editor
- Handle loading states, error states, and empty states throughout

### Step 8: Polish and Deploy
- Add input validation on frontend and backend
- Add error handling and user-friendly error messages
- Responsive layout for the guitar neck editor
- Write a README with setup instructions
- Configure production deployment (Docker, environment variables, CORS)

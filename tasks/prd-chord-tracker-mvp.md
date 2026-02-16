# PRD: Chord Tracker MVP

## Introduction

Chord Tracker is a SaaS web application that enables musicians to visually build, save, and organize guitar chord diagrams. Users interact with an on-screen guitar neck to place finger markers on strings and frets, constructing chords that are saved into ordered sequences within songs. The app is organized around a hierarchy of Projects → Songs → Chords, with JWT-based authentication protecting all user data.

## Goals

- Provide a visual, intuitive guitar neck editor for creating chord diagrams
- Allow users to organize chords into songs, and songs into projects
- Persist all data to PostgreSQL via a RESTful API
- Support responsive layout and touch interaction from day one
- Secure all user data behind JWT-based authentication

## User Stories

### US-001: Scaffold frontend project
**Description:** As a developer, I need a React + TypeScript frontend scaffolded with Vite, Tailwind CSS, and React Router so that I have a working foundation to build on.

**Acceptance Criteria:**
- [ ] Vite project initialized with React + TypeScript template in `frontend/`
- [ ] Tailwind CSS installed and configured
- [ ] React Router installed with a basic route structure (home, login, signup, dashboard)
- [ ] Proxy configured for API requests to backend during development
- [ ] `npm run dev` starts the dev server successfully
- [ ] Typecheck and lint pass

### US-002: Scaffold backend project
**Description:** As a developer, I need a FastAPI backend scaffolded with proper project structure so that I can build API endpoints.

**Acceptance Criteria:**
- [ ] FastAPI project created in `backend/` with uvicorn
- [ ] Project structure: `routers/`, `models/`, `schemas/`, `database/`, `auth/`
- [ ] SQLAlchemy configured with async support
- [ ] Alembic initialized for migrations
- [ ] Ruff configured for linting/formatting
- [ ] `docker-compose.yml` at project root with PostgreSQL service
- [ ] Backend starts and returns 200 on a health-check endpoint
- [ ] Lint passes

### US-003: Define database schema and migrations
**Description:** As a developer, I need SQLAlchemy models and an initial migration so that the database schema is in place.

**Acceptance Criteria:**
- [ ] SQLAlchemy models defined for User, Project, Song, Chord matching the data model
- [ ] Chord model stores `markers` as a JSON column (array of `{string, fret}` objects)
- [ ] Chord model has `position` integer for ordering within a song
- [ ] All models use UUID primary keys
- [ ] Initial Alembic migration generated and runs successfully against Postgres
- [ ] Lint passes

### US-004: User registration endpoint
**Description:** As a new user, I want to create an account with email and password so that I can save my work.

**Acceptance Criteria:**
- [ ] `POST /auth/register` accepts `{email, password}` and creates a user
- [ ] Password is hashed with bcrypt before storage
- [ ] Returns 201 with user info (no password hash) on success
- [ ] Returns 409 if email already exists
- [ ] Email validation (must be valid format)
- [ ] Password validation (minimum 8 characters)
- [ ] Tests pass for success and error cases
- [ ] Lint passes

### US-005: User login endpoint
**Description:** As a returning user, I want to log in so that I can access my projects.

**Acceptance Criteria:**
- [ ] `POST /auth/login` accepts `{email, password}` and returns access + refresh tokens
- [ ] Access token expires in 15 minutes
- [ ] Refresh token expires in 7 days
- [ ] Returns 401 for invalid credentials
- [ ] Tests pass
- [ ] Lint passes

### US-006: Token refresh endpoint
**Description:** As a logged-in user, I want my session to stay alive without re-entering credentials.

**Acceptance Criteria:**
- [ ] `POST /auth/refresh` accepts a refresh token and returns a new access token
- [ ] Returns 401 for expired or invalid refresh token
- [ ] Tests pass
- [ ] Lint passes

### US-007: Auth middleware
**Description:** As a developer, I need JWT validation middleware so that protected routes can identify the current user.

**Acceptance Criteria:**
- [ ] FastAPI dependency that extracts and validates JWT from `Authorization: Bearer <token>` header
- [ ] Dependency returns current user object or raises 401
- [ ] All subsequent API endpoints (projects, songs, chords) use this dependency
- [ ] Tests pass
- [ ] Lint passes

### US-008: Frontend auth pages and context
**Description:** As a user, I want signup and login pages so that I can create an account and access the app.

**Acceptance Criteria:**
- [ ] Signup page with email and password fields, submit button, link to login
- [ ] Login page with email and password fields, submit button, link to signup
- [ ] Auth context/provider that stores tokens and exposes `user`, `login`, `signup`, `logout`
- [ ] Tokens stored in memory (access) and httpOnly cookie or localStorage (refresh)
- [ ] Route guard redirects unauthenticated users to login
- [ ] Route guard redirects authenticated users away from login/signup to dashboard
- [ ] Typecheck and lint pass
- [ ] Verify in browser using dev-browser skill

### US-009: Project CRUD API
**Description:** As a developer, I need REST endpoints for project management so that the frontend can create and manage projects.

**Acceptance Criteria:**
- [ ] `GET /projects` returns all projects for the authenticated user
- [ ] `POST /projects` creates a project with `{name}` for the authenticated user
- [ ] `GET /projects/:id` returns a single project (404 if not found, 403 if not owner)
- [ ] `PUT /projects/:id` updates project name (403 if not owner)
- [ ] `DELETE /projects/:id` deletes project and cascades to songs/chords (403 if not owner)
- [ ] Tests pass for CRUD operations and authorization checks
- [ ] Lint passes

### US-010: Song CRUD API
**Description:** As a developer, I need REST endpoints for song management within projects.

**Acceptance Criteria:**
- [ ] `GET /projects/:id/songs` returns all songs in a project (validates project ownership)
- [ ] `POST /projects/:id/songs` creates a song with `{name}` in the project
- [ ] `GET /songs/:id` returns a single song (validates ownership through project)
- [ ] `PUT /songs/:id` updates song name
- [ ] `DELETE /songs/:id` deletes song and cascades to chords
- [ ] Tests pass
- [ ] Lint passes

### US-011: Chord CRUD API
**Description:** As a developer, I need REST endpoints for chord management within songs.

**Acceptance Criteria:**
- [ ] `GET /songs/:id/chords` returns all chords in a song, ordered by `position`
- [ ] `POST /songs/:id/chords` creates a chord with `{name?, markers, string_count?, tuning?}`
- [ ] New chord auto-assigned next position in sequence
- [ ] `PUT /chords/:id` updates chord fields (name, markers, tuning, string_count)
- [ ] `DELETE /chords/:id` deletes chord and re-normalizes positions
- [ ] `PUT /songs/:id/chords/reorder` accepts `{chord_ids: [...]}` and updates positions
- [ ] Tests pass
- [ ] Lint passes

### US-012: Project list page
**Description:** As a user, I want to see all my projects after logging in so that I can pick one to work on.

**Acceptance Criteria:**
- [ ] Dashboard page shows list of user's projects with name and last-updated date
- [ ] "New Project" button opens a form/modal to create a project
- [ ] Each project card links to the project detail page
- [ ] Empty state message when no projects exist
- [ ] Project can be renamed inline or via modal
- [ ] Project can be deleted with confirmation dialog
- [ ] Typecheck and lint pass
- [ ] Verify in browser using dev-browser skill

### US-013: Song list page
**Description:** As a user, I want to see all songs in a project so that I can select one to edit.

**Acceptance Criteria:**
- [ ] Project detail page shows list of songs with name and last-updated date
- [ ] "New Song" button creates a song
- [ ] Each song links to the song detail (chord sequence) page
- [ ] Empty state message when no songs exist
- [ ] Song can be renamed and deleted
- [ ] Breadcrumb navigation: Dashboard → Project
- [ ] Typecheck and lint pass
- [ ] Verify in browser using dev-browser skill

### US-014: Guitar neck editor component
**Description:** As a user, I want an interactive guitar neck where I can tap fret-string intersections to place or remove finger markers.

**Acceptance Criteria:**
- [ ] SVG-based React component renders a guitar neck with frets and strings
- [ ] Configurable via props: `stringCount` (default 6), `tuning` (default "EADGBE"), `markers`, `onMarkerToggle`
- [ ] Renders at least 5 frets with fret numbers
- [ ] String labels displayed based on tuning
- [ ] Tap/click a fret-string intersection to toggle a marker on/off
- [ ] Markers displayed as filled circles on the neck
- [ ] Nut (fret 0) visually distinct
- [ ] Touch-friendly: tap targets at least 44x44px
- [ ] Responsive: scales to fit container width on mobile and desktop
- [ ] Typecheck and lint pass
- [ ] Verify in browser using dev-browser skill

### US-015: Chord sequence view
**Description:** As a user, I want to see all chords in a song as an ordered sequence so that I can view and manage my chord progression.

**Acceptance Criteria:**
- [ ] Song detail page shows ordered list of chord cards
- [ ] Each chord card displays: chord name (if set), a mini guitar neck preview of the markers
- [ ] "Add Chord" button at the end of the sequence
- [ ] Empty state when song has no chords
- [ ] Breadcrumb navigation: Dashboard → Project → Song
- [ ] Typecheck and lint pass
- [ ] Verify in browser using dev-browser skill

### US-016: Add and edit chords
**Description:** As a user, I want to create new chords and edit existing ones using the guitar neck editor.

**Acceptance Criteria:**
- [ ] "Add Chord" opens the guitar neck editor in a modal or inline panel
- [ ] User can place markers by tapping fret-string intersections
- [ ] Optional chord name input field
- [ ] "Save" persists the chord to the API and adds it to the sequence
- [ ] Tapping an existing chord card opens the editor pre-populated with its markers
- [ ] "Save" on edit updates the chord via API
- [ ] "Cancel" discards changes
- [ ] Typecheck and lint pass
- [ ] Verify in browser using dev-browser skill

### US-017: Reorder and delete chords
**Description:** As a user, I want to reorder chords in a song and remove ones I don't need.

**Acceptance Criteria:**
- [ ] Drag-and-drop reordering on desktop (using a library like dnd-kit or similar)
- [ ] Move up/down buttons as alternative (essential for touch/mobile)
- [ ] Reorder persists via `PUT /songs/:id/chords/reorder`
- [ ] Delete button on each chord card with confirmation
- [ ] Typecheck and lint pass
- [ ] Verify in browser using dev-browser skill

### US-018: Chord template library
**Description:** As a user, I want to pick from a library of common chord shapes so that I don't have to manually place markers for well-known chords.

**Acceptance Criteria:**
- [ ] Built-in library of common open chords (A, Am, B, Bm, C, D, Dm, E, Em, F, G) with standard fingerings
- [ ] Include common barre chord shapes (e.g., F barre, B barre)
- [ ] "Browse Templates" button accessible from the chord editor
- [ ] Templates displayed in a searchable/filterable list or grid
- [ ] Selecting a template populates the guitar neck editor with the chord's markers and name
- [ ] User can modify the template markers before saving (template is a starting point, not locked)
- [ ] Templates are read-only and available to all users (not user-created in MVP)
- [ ] Typecheck and lint pass
- [ ] Verify in browser using dev-browser skill

### US-019: Responsive layout and navigation
**Description:** As a mobile user, I want the app to work well on my phone so that I can use it during practice.

**Acceptance Criteria:**
- [ ] All pages use responsive Tailwind layouts (mobile-first)
- [ ] Navigation works on mobile (hamburger menu or bottom nav)
- [ ] Guitar neck editor is usable on screens as small as 375px wide
- [ ] Touch targets meet minimum 44x44px
- [ ] No horizontal scrolling on any page at mobile widths
- [ ] Typecheck and lint pass
- [ ] Verify in browser using dev-browser skill

## Functional Requirements

- FR-1: The system must allow users to register with email and password
- FR-2: The system must authenticate users via JWT access and refresh tokens
- FR-3: All API routes except auth endpoints must require a valid access token
- FR-4: Users can only access their own projects, songs, and chords
- FR-5: The system must allow creating, renaming, and deleting projects
- FR-6: The system must allow creating, renaming, and deleting songs within a project
- FR-7: The system must render an SVG guitar neck with configurable strings, tuning, and fret count
- FR-8: Tapping a fret-string intersection must toggle a marker on/off
- FR-9: The system must allow adding chords to a song with optional name and marker data
- FR-10: The system must allow reordering chords within a song
- FR-11: The system must allow deleting chords, re-normalizing positions afterward
- FR-12: Deleting a project must cascade-delete its songs and chords
- FR-13: Deleting a song must cascade-delete its chords
- FR-14: The system must provide a built-in library of common chord templates (open and barre chords)
- FR-15: Selecting a chord template must populate the editor with its markers and name, editable before saving
- FR-16: The frontend must be responsive and touch-friendly on screens 375px and wider

## Non-Goals

- No social features (sharing, collaboration, public profiles)
- No audio playback or chord sound preview
- No chord recognition or auto-detection from audio
- No import/export of chord sheets (PDF, MusicXML, etc.)
- No offline support or PWA features
- No support for instruments other than guitar in MVP
- No admin panel or user management dashboard
- No payment or subscription features in MVP

## Design Considerations

- Use Tailwind CSS for all styling — no additional CSS frameworks
- SVG-based guitar neck for crisp rendering at any scale
- Mobile-first responsive design; the guitar neck editor is the most layout-critical component
- Use consistent color scheme for markers (consider color-blind-friendly palette)
- Mini chord previews in the sequence view should be compact SVG renderings of the full editor

## Technical Considerations

- **Frontend:** Vite + React 18+ + TypeScript + Tailwind CSS + React Router
- **Backend:** FastAPI + SQLAlchemy (async) + Alembic + bcrypt + python-jose (JWT)
- **Database:** PostgreSQL via `docker-compose.yml`
- **Chord markers** stored as JSON in PostgreSQL (`[{string: 1, fret: 2}, ...]`)
- **Drag-and-drop:** Use a lightweight library (dnd-kit recommended) for chord reordering
- **API client:** Use fetch with a wrapper that handles token refresh automatically
- **CORS:** Backend must allow frontend dev server origin

## Success Metrics

- User can go from signup to saving their first chord in under 2 minutes
- Guitar neck editor is usable on a 375px-wide mobile screen
- All CRUD operations respond in under 200ms
- Zero data loss — all chord placements persist immediately on save

## Open Questions

- Should the guitar neck show more than 5 frets, and if so, should it scroll or paginate?
  - No, let's start with 5 frets only and no scrolling or pagination
- Should there be a chord library/templates (e.g., common chords pre-built)?
  - Yes, a chord template library would be very useful
- Should undo/redo be supported in the editor for the MVP?
  - No, we can add this later if needed

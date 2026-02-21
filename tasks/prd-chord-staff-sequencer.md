# PRD: Chord Staff Sequencer

## Introduction

Add a chord sequencing view to the song detail page where users can arrange their song's chords onto a visual music staff. The staff resembles traditional sheet music: multiple lines of measures with barlines, a time signature, and support for repeat annotations (repeat barlines and numbered endings). Chords are dragged from the song's existing chord list onto beat slots within measures. The same chord can appear multiple times and in any order, making the staff independent from the existing chord list ordering.

## Goals

- Let users visually sequence chords on a music-staff-style UI within a song
- Support configurable time signatures (default 4/4)
- Display multiple lines of measures (like sheet music) with a fixed number of measures per line
- Allow repeat barline and numbered ending annotations
- Persist the sequence to the backend so it survives page reloads

## User Stories

### US-001: Create sequence data model and migrations
**Description:** As a developer, I need database tables to store chord sequences so that sequencing data can be persisted.

**Acceptance Criteria:**
- [ ] `sequence` table: `id`, `song_id` (FK → songs, unique), `time_signature_numerator` (int, default 4), `time_signature_denominator` (int, default 4), `measures_per_line` (int, default 4), `created_at`, `updated_at`
- [ ] `sequence_measure` table: `id`, `sequence_id` (FK → sequence), `position` (int, 0-based order), `repeat_start` (bool, default false), `repeat_end` (bool, default false), `ending_number` (int, nullable — 1 or 2)
- [ ] `sequence_beat` table: `id`, `measure_id` (FK → sequence_measure), `beat_position` (int, 1-based), `chord_id` (FK → chords, nullable)
- [ ] Alembic migration generated and applied successfully
- [ ] Typecheck passes

### US-002: Backend API for sequence CRUD
**Description:** As a developer, I need REST endpoints to create, read, and update a song's chord sequence so the frontend can persist changes.

**Acceptance Criteria:**
- [ ] `GET /api/songs/{song_id}/sequence` — returns full sequence with nested measures and beats; returns 404 if none exists
- [ ] `POST /api/songs/{song_id}/sequence` — creates a new sequence for the song (errors if one already exists)
- [ ] `PUT /api/songs/{song_id}/sequence` — replaces the full sequence (measures + beats) with the payload; used for bulk saves
- [ ] `DELETE /api/songs/{song_id}/sequence` — deletes the sequence and all child records
- [ ] All endpoints require authentication and verify the song belongs to the authenticated user
- [ ] Pydantic schemas defined for request/response
- [ ] Typecheck passes

### US-003: Display chord staff on song detail page
**Description:** As a user, I want to see a music-staff-style display on the song detail page so I can visualize chord sequences like sheet music.

**Acceptance Criteria:**
- [ ] A "Chord Sequence" section appears below the existing chord list on the song detail page
- [ ] Staff renders multiple lines, each containing `measures_per_line` measures (default 4)
- [ ] Each measure is separated by a vertical barline
- [ ] The time signature (e.g., "4/4") is displayed at the start of the first line
- [ ] Each measure shows `numerator` beat slots (e.g., 4 slots for 4/4)
- [ ] Empty beat slots display a placeholder (e.g., dashed outline)
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill

### US-004: Configure time signature
**Description:** As a user, I want to set the time signature for a song's sequence so the correct number of beats per measure is shown.

**Acceptance Criteria:**
- [ ] A time signature selector is displayed above the staff (numerator: 2–12; denominator: 2, 4, 8, 16)
- [ ] Default is 4/4 when creating a new sequence
- [ ] Changing the time signature updates the beat slot count in every measure immediately
- [ ] If existing beats exceed the new numerator, those beats are removed (with a confirmation dialog warning data will be lost)
- [ ] The updated time signature is persisted on save
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill

### US-005: Drag a chord from the chord list onto a beat slot
**Description:** As a user, I want to drag a chord from the song's chord list onto the staff so I can build my chord sequence.

**Acceptance Criteria:**
- [ ] Each chord in the existing chord list acts as a drag source
- [ ] Each beat slot in the staff is a drop target
- [ ] Dropping a chord onto an empty slot places it there and displays the chord name
- [ ] Dropping a chord onto an occupied slot replaces the existing chord
- [ ] A chord can be placed on multiple different beat slots (same chord used multiple times)
- [ ] The placement is reflected immediately in the UI without a full page reload
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill

### US-006: Remove a chord from a beat slot
**Description:** As a user, I want to clear a chord from a beat slot so I can correct mistakes or leave a beat empty.

**Acceptance Criteria:**
- [ ] Clicking a filled beat slot opens a small popover/context menu with a "Remove" option
- [ ] Selecting "Remove" clears the slot back to the empty placeholder state
- [ ] Removed chord data is reflected in the sequence state immediately
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill

### US-007: Add and remove measures
**Description:** As a user, I want to add or remove measures on the staff so I can match the length of my song.

**Acceptance Criteria:**
- [ ] An "Add Measure" button appends a new empty measure to the end of the staff
- [ ] A remove button (e.g., "×") on each measure deletes that measure and its beats
- [ ] Removing a measure with chords shows a confirmation dialog ("This will remove all chords in this measure")
- [ ] Measures are renumbered/repositioned correctly after removal
- [ ] Staff lines reflow automatically when measure count changes (e.g., a 5th measure starts a new line)
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill

### US-008: Add repeat barline annotations
**Description:** As a user, I want to mark sections of the staff with repeat barlines so I can indicate that a section should be played again.

**Acceptance Criteria:**
- [ ] Each measure has a toggle for "repeat start" (`:||` symbol before the measure) and "repeat end" (`||:` symbol after the measure)
- [ ] Toggling repeat start on a measure displays a bold repeat-start barline (`|:`) to the left of that measure
- [ ] Toggling repeat end on a measure displays a bold repeat-end barline (`:|`) to the right of that measure
- [ ] Both toggles can be active simultaneously on the same measure
- [ ] Repeat annotation state is persisted on save
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill

### US-009: Add numbered ending annotations
**Description:** As a user, I want to mark measures as 1st or 2nd endings so I can write out repeated sections with different endings.

**Acceptance Criteria:**
- [ ] Each measure has a selector for ending number: None, 1, or 2
- [ ] A measure marked as ending 1 displays a bracket labeled "1." above it
- [ ] A measure marked as ending 2 displays a bracket labeled "2." above it
- [ ] Only one ending number can be active per measure at a time
- [ ] Ending annotation state is persisted on save
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill

### US-010: Save and load sequence
**Description:** As a user, I want my chord sequence to be saved and reloaded when I return to the song so my work is not lost.

**Acceptance Criteria:**
- [ ] A "Save Sequence" button sends the full current sequence state to `PUT /api/songs/{song_id}/sequence`
- [ ] On page load, the frontend fetches the existing sequence via `GET /api/songs/{song_id}/sequence` and renders it
- [ ] If no sequence exists yet, the staff initializes with 4 empty measures in 4/4 time and a "Save Sequence" button
- [ ] A success/error toast is shown after save attempts
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill

## Functional Requirements

- FR-1: Each song has at most one sequence (one-to-one relationship)
- FR-2: A sequence contains an ordered list of measures; measures contain ordered beat slots
- FR-3: A beat slot may reference any chord belonging to the same song, or be empty
- FR-4: The number of beat slots per measure equals the time signature numerator
- FR-5: The staff displays measures grouped into lines; the number of measures per line defaults to 4
- FR-6: Chords are dragged from the song's chord list onto beat slots using drag-and-drop (reuse dnd-kit, already in the project)
- FR-7: Repeat start and repeat end barlines are independent toggles per measure
- FR-8: Numbered endings (1 or 2) are mutually exclusive options per measure
- FR-9: The full sequence state is persisted via a bulk `PUT` endpoint (not incremental per-beat updates)
- FR-10: All sequence API endpoints enforce ownership — only the song's owner may access them

## Non-Goals

- No audio playback or metronome
- No tempo/BPM setting
- No export to MusicXML, PDF, or image formats
- No support for mid-measure time signature changes
- No sub-beat chord placement (e.g., chords on eighth-note subdivisions)
- No support for more than 2 numbered endings
- No real-time collaboration

## Design Considerations

- Reuse `dnd-kit` (already installed) for drag-and-drop between the chord list and beat slots
- Staff lines should feel like sheet music: horizontal, with clear barlines and consistent measure widths
- Beat slots should be wide enough to display a chord name (e.g., "Cmaj7") without truncation
- Repeat barlines can be rendered as SVG or styled divs with double-line + dot symbols (`:||`, `||:`)
- Numbered ending brackets are rendered as an L-shaped bracket above the measure with a number label
- The chord list on the song detail page remains unchanged; it now also acts as a drag source palette

## Technical Considerations

- Backend: add `backend/routers/sequences.py`, `backend/models/sequence.py`, `backend/schemas/sequence.py`; register router in `main.py`
- Frontend: add `frontend/src/components/StaffDisplay.tsx` (staff container), `MeasureLine.tsx` (one line of measures), `MeasureBlock.tsx` (single measure with barlines + beat slots), `BeatSlot.tsx` (individual drop target)
- Frontend: add `frontend/src/api/sequences.ts` for API calls
- Frontend: update `SongDetail.tsx` to include the new staff section and load sequence on mount
- Drag sources (chord list items) and drop targets (beat slots) will both need dnd-kit context — wrap the song detail page in a shared `DndContext`
- Sequence save is a full replacement (`PUT`) to keep the API simple; no partial patch endpoints needed

## Success Metrics

- Users can drag a chord onto the staff in 2 or fewer interactions
- Staff correctly reflowing into multiple lines when measures exceed `measures_per_line`
- Sequence survives a full page reload without data loss
- Repeat annotations render visually distinguishable from normal barlines

## Open Questions

- Should `measures_per_line` be user-configurable per sequence, or always fixed at 4?
    - Let's got with 'fixed at 4' for now
- Should deleting a chord from the chord list automatically clear it from any beat slots in the sequence?
    - Yes
- Should there be a visual indicator when a chord used in the sequence has been deleted from the chord list (orphaned reference)?
    - No, since we're clearing the chord from the beat slots, there should be no orphaned refereneces

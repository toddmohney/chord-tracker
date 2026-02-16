# PRD: Starting Fret Number on Fretboard Chart

## Introduction

Currently the fretboard chart (`GuitarNeck` component) always displays frets 1–5 starting from the nut. This makes it impossible to accurately represent chords and scale patterns played higher up the neck (e.g., a barre chord at fret 7). This feature adds a configurable starting fret so the displayed fret range shifts accordingly (e.g., frets 5–9), while keeping the 5-fret window fixed.

## Goals

- Allow each chord to store and display a starting fret number
- Show correct fret numbers on the fretboard when the starting fret is not 1
- Provide a UI control in the chord editor for adjusting the starting fret
- Update chord templates to include starting fret data where appropriate
- Visually distinguish a non-nut starting position (no thick nut bar when starting fret > 0)

## User Stories

### US-001: Add `starting_fret` field to backend Chord model
**Description:** As a developer, I need to persist a starting fret per chord so it survives page reloads and is available via the API.

**Acceptance Criteria:**
- [ ] Add `starting_fret` integer column to `chords` table with default value `0` (0 means "from the nut")
- [ ] Create and run an Alembic migration for the new column
- [ ] Add `starting_fret` to `ChordCreate`, `ChordUpdate`, and `ChordResponse` Pydantic schemas
- [ ] Existing chords default to `starting_fret = 0` with no data loss
- [ ] Typecheck/lint passes
- [ ] Existing backend tests still pass

### US-002: Add `startingFret` prop to GuitarNeck component
**Description:** As a developer, I want the `GuitarNeck` component to accept a `startingFret` prop so it renders the correct fret range.

**Acceptance Criteria:**
- [ ] Add optional `startingFret` prop (default `0`) to `GuitarNeckProps`
- [ ] Fret number labels display `startingFret + 1` through `startingFret + fretCount` (e.g., if `startingFret = 4`, labels show 5, 6, 7, 8, 9)
- [ ] When `startingFret > 0`, the thick nut bar is hidden (replaced by a normal fret line)
- [ ] When `startingFret === 0`, the nut bar renders as it does today
- [ ] Marker positions remain visually correct — a marker at fret index 1 sits in the first fret space regardless of starting fret
- [ ] Tap targets continue to emit correct `fret` values relative to the starting fret (i.e., tapping the first fret space emits `startingFret + 1`)
- [ ] Typecheck/lint passes
- [ ] Verify in browser using dev-browser skill

### US-003: Add starting fret control to chord editor UI
**Description:** As a user, I want to adjust the starting fret in the chord editor so I can create chords at any neck position.

**Acceptance Criteria:**
- [ ] Display the current starting fret value near the fretboard (e.g., "Starting fret: 5")
- [ ] Provide increment (+) and decrement (−) buttons to change the starting fret
- [ ] Minimum starting fret is 0 (nut position); maximum is 19
- [ ] Changing the starting fret updates the fretboard immediately (fret labels shift)
- [ ] The starting fret value is saved when the chord is saved (persisted to backend)
- [ ] Typecheck/lint passes
- [ ] Verify in browser using dev-browser skill

### US-004: Update chord templates with starting fret data
**Description:** As a user browsing chord templates, I want templates to display at the correct neck position so I can learn proper finger placement.

**Acceptance Criteria:**
- [ ] Add `starting_fret` field to `ChordTemplate` interface (default `0`)
- [ ] Update templates that require a starting fret (e.g., B and Bm barre chords at fret 2 should have `starting_fret: 2` with markers adjusted to be relative to that starting fret)
- [ ] Template preview in the browser renders with the correct starting fret
- [ ] Typecheck/lint passes
- [ ] Verify in browser using dev-browser skill

### US-005: Display starting fret on chord card previews
**Description:** As a user viewing my saved chords, I want the mini fretboard previews to reflect the correct starting fret so I can tell chords apart at a glance.

**Acceptance Criteria:**
- [ ] Chord card previews pass `startingFret` to `GuitarNeck`
- [ ] Fret numbers on mini previews reflect the actual fret position
- [ ] Typecheck/lint passes
- [ ] Verify in browser using dev-browser skill

## Functional Requirements

- FR-1: Add `starting_fret` integer column (default `0`) to the `chords` database table via Alembic migration
- FR-2: Expose `starting_fret` in `ChordCreate`, `ChordUpdate`, and `ChordResponse` schemas
- FR-3: `GuitarNeck` component accepts an optional `startingFret` prop that offsets displayed fret numbers
- FR-4: When `startingFret > 0`, the nut bar is not rendered; a regular fret line appears instead
- FR-5: Tap/click events on the fretboard emit fret numbers offset by `startingFret` (e.g., first fret space emits `startingFret + 1`)
- FR-6: Chord editor includes +/− controls to adjust starting fret (range 0–19)
- FR-7: Starting fret value is persisted when saving a chord
- FR-8: `ChordTemplate` interface includes `starting_fret` with a default of `0`
- FR-9: Chord card previews display the correct starting fret

## Non-Goals

- No scrollable/infinite fretboard — the window stays fixed at 5 frets
- No changing the number of visible frets (stays at `fretCount` default of 5)
- No automatic detection of optimal starting fret from marker positions
- No fret dot inlay markers (3rd, 5th, 7th, 12th frets, etc.)

## Design Considerations

- The +/− buttons for starting fret should be placed to the left of the fretboard or above it, near the existing fret number labels
- Use the existing button/control styling from the app for consistency
- When `startingFret > 0`, consider showing a small visual indicator (e.g., the starting fret number displayed prominently at the top-left) so users know they are not at the nut

## Technical Considerations

- The `Marker.fret` values stored in the database are **absolute** fret numbers (e.g., fret 7 on the actual guitar neck). The `GuitarNeck` component should translate these to visual positions by subtracting `startingFret`
- When the user changes the starting fret in the editor, existing markers that fall outside the new visible range should be preserved in data but hidden visually to avoid data loss
- The backend migration must be backwards-compatible (default value so existing rows are unaffected)

## Success Metrics

- Users can create and save chords at any position on the neck (frets 0–19+)
- Chord templates for barre chords display at the correct neck position
- Starting fret is visible on both editor and card preview views

## Open Questions

- Should markers outside the visible fret window be shown as a subtle indicator (e.g., a count badge) or completely hidden?
    - Yes, show them as a subtle indicator
- Should the starting fret auto-adjust when loading a chord whose markers fall outside the default 0–5 range?
    - Yes

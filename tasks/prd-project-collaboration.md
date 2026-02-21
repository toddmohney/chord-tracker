# PRD: Project Collaboration with Role-Based Access

## Introduction

Allow project owners to invite other registered users to collaborate on their projects. Collaborators can be assigned one of three roles (Viewer, Editor, Admin) that control what actions they can take. Invitees receive an in-app notification when they log in and can accept or decline. Owners can monitor invitation status and remove collaborators at any time.

---

## Goals

- Enable project owners to invite other users (by email or username) to collaborate on a project
- Provide three access tiers: Viewer, Editor, and Admin
- Show pending invitations to invitees via a login banner/modal
- Give project owners a collaborators management page with real-time invitation status
- Allow project owners to remove collaborators at any time; collaborator contributions are preserved
- Enforce role-based permissions on both the API and UI

---

## Roles Reference

| Role    | View chords/songs | Edit/delete chords & songs | Rename project | Invite collaborators | Remove collaborators | Delete project |
|---------|:-----------------:|:--------------------------:|:--------------:|:--------------------:|:--------------------:|:--------------:|
| Owner   | ✅               | ✅                         | ✅             | ✅                  | ✅                   | ✅             |
| Admin   | ✅               | ✅                         | ✅             | ✅                  | ❌                   | ❌             |
| Editor  | ✅               | ✅                         | ❌             | ❌                  | ❌                   | ❌             |
| Viewer  | ✅               | ❌                         | ❌             | ❌                  | ❌                   | ❌             |

> **Owner** is the user who created the project. All other participants are collaborators assigned one of the three roles above.

---

## User Stories

### US-001: Add collaborators database schema
**Description:** As a developer, I need a database table to store project collaborations so that role and invitation state can persist.

**Acceptance Criteria:**
- [ ] Create `project_collaborators` table with columns: `id` (UUID PK), `project_id` (FK → projects), `inviter_id` (FK → users), `invitee_id` (FK → users), `role` (enum: `viewer` | `editor` | `admin`), `status` (enum: `pending` | `accepted` | `declined`), `created_at`, `updated_at`
- [ ] Add unique constraint on `(project_id, invitee_id)` to prevent duplicate invitations
- [ ] Generate and run Alembic migration successfully
- [ ] Typecheck passes

---

### US-002: Invite a collaborator to a project
**Description:** As a project owner or Admin, I want to invite another user by email or username and assign them a role so they can collaborate on my project.

**Acceptance Criteria:**
- [ ] POST `/projects/{project_id}/collaborators` endpoint accepts `{ "identifier": "<email or username>", "role": "viewer" | "editor" | "admin" }`
- [ ] API looks up user by email first, then by username if no email match found
- [ ] Returns 404 if no user matches the identifier
- [ ] Returns 409 if that user already has a `pending` or `accepted` collaboration on this project
- [ ] Returns 403 if the requesting user is not the Owner or Admin of the project
- [ ] Creates a `project_collaborators` record with `status: "pending"`
- [ ] Typecheck passes

---

### US-003: Display pending invitations banner on login
**Description:** As an invitee, I want to see a notification when I log in if I have pending project invitations so I can decide whether to join.

**Acceptance Criteria:**
- [ ] After login, if the authenticated user has any `pending` invitations, a modal/banner appears above the dashboard listing each pending invite: project name, inviter name, and assigned role
- [ ] Each invitation shows two buttons: "Accept" and "Decline"
- [ ] If there are no pending invitations, no modal/banner is shown
- [ ] The banner/modal is dismissible without accepting or declining (invitations remain pending)
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill

---

### US-004: Accept or decline an invitation
**Description:** As an invitee, I want to accept or decline a collaboration invitation so I can control which projects I participate in.

**Acceptance Criteria:**
- [ ] PATCH `/collaborators/{collaborator_id}` endpoint accepts `{ "status": "accepted" | "declined" }` and updates the record
- [ ] Only the invitee (the user referenced by `invitee_id`) can accept or decline; returns 403 otherwise
- [ ] Cannot transition from `accepted` or `declined` back to `pending`; returns 400 if attempted
- [ ] On acceptance, the project immediately appears in the invitee's dashboard
- [ ] On decline, the record is retained with `status: "declined"` (owner can see this on the collaborators page)
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill

---

### US-005: Collaborators management page
**Description:** As a project owner or Admin, I want a page that lists all collaborators and their invitation status so I can monitor who has access to my project.

**Acceptance Criteria:**
- [ ] A "Collaborators" tab or button is visible on the Project Detail page for Owners and Admins
- [ ] The collaborators page lists all collaborators with: avatar/name, email or username, assigned role, and invitation status (`pending` | `accepted` | `declined`)
- [ ] GET `/projects/{project_id}/collaborators` returns the list, accessible only to the project Owner and Admins
- [ ] Pending and declined invitations are visually distinguished from accepted ones (e.g., muted color or badge)
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill

---

### US-006: Remove a collaborator
**Description:** As a project owner, I want to remove a collaborator from my project so I can revoke their access.

**Acceptance Criteria:**
- [ ] DELETE `/projects/{project_id}/collaborators/{collaborator_id}` removes the collaboration record
- [ ] Only the project Owner can remove collaborators; returns 403 otherwise
- [ ] Owner cannot remove themselves (they are the owner, not a collaborator)
- [ ] The removed user's chords and songs contributions remain intact in the project
- [ ] After removal, the project no longer appears in the removed user's dashboard
- [ ] A confirmation dialog appears in the UI before the removal is sent ("Remove [name] from this project?")
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill

---

### US-007: Enforce role-based permissions on the API
**Description:** As a developer, I need the API to enforce access rules based on each user's role so that collaborators cannot perform actions beyond their permission tier.

**Acceptance Criteria:**
- [ ] A reusable `get_project_access(project_id, current_user)` dependency returns the user's effective role (`owner` | `admin` | `editor` | `viewer`) or raises 403 if they have no access
- [ ] All existing project/song/chord endpoints use this dependency instead of the current owner-only check
- [ ] Viewer requests to mutating endpoints (POST/PUT/PATCH/DELETE for songs and chords) return 403
- [ ] Editor requests to rename a project return 403
- [ ] Editor and Viewer requests to invite or remove collaborators return 403
- [ ] Typecheck passes

---

### US-008: Show shared projects on the dashboard
**Description:** As an accepted collaborator, I want to see the projects I've been invited to in my dashboard so I can access them easily.

**Acceptance Criteria:**
- [ ] GET `/projects` returns both owned projects and projects where the user has an `accepted` collaboration
- [ ] Shared projects are visually distinguished on the dashboard (e.g., a "Shared" badge or a different section heading)
- [ ] Clicking a shared project navigates to the project detail page with UI reflecting the user's role (edit controls hidden for Viewers)
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill

---

### US-009: Hide/disable UI controls based on role
**Description:** As a collaborator, I want the UI to reflect my permissions so I don't attempt actions I'm not allowed to perform.

**Acceptance Criteria:**
- [ ] Viewer: add/edit/delete buttons for songs and chords are hidden or disabled
- [ ] Editor: add/edit/delete buttons for songs and chords are visible and functional; project rename and collaborator controls are hidden
- [ ] Admin: all controls visible except the "Delete project" button
- [ ] Owner: all controls visible
- [ ] The user's role is returned from the project detail API response so the frontend can conditionally render controls
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill

---

## Functional Requirements

- **FR-1:** The system must store each collaboration with a role (`viewer`, `editor`, `admin`) and a status (`pending`, `accepted`, `declined`)
- **FR-2:** A user may only have one active collaboration record per project (unique constraint on `project_id` + `invitee_id`)
- **FR-3:** Invitations are looked up by email address first; if no match, by username
- **FR-4:** Only the project Owner and Admins may send invitations
- **FR-5:** Only the project Owner may remove collaborators
- **FR-6:** Pending invitations are surfaced as a login-time modal/banner if any exist
- **FR-7:** Accepted collaborators see the shared project in their dashboard, clearly labeled as shared
- **FR-8:** All project, song, and chord API endpoints must validate the requesting user's effective role before allowing mutations
- **FR-9:** When a collaborator is removed, their contributions (chords, songs) remain in the project
- **FR-10:** A declined invitation remains stored so the owner can see it on the collaborators page; the invitee is not re-notified

---

## Non-Goals (Out of Scope)

- Email notifications (no emails sent for invitations or removal — in-app only)
- Re-inviting a user who has declined (out of scope for MVP; declined invitations are final)
- Collaborators inviting other collaborators at the Editor tier (only Owner and Admin can invite)
- Granular per-song or per-chord permissions (access is project-wide)
- Real-time collaboration / simultaneous editing (no live sync or conflict resolution)
- Audit log or activity feed for collaborator actions
- Bulk invite (inviting multiple users at once)
- Transferring project ownership

---

## Design Considerations

- **Collaborators page:** Accessible via a "Collaborators" link/tab on the Project Detail page, visible only to Owner and Admins
- **Role badge:** Display a small role label (`Viewer`, `Editor`, `Admin`, `Owner`) on the project detail page so all participants know their access level at a glance
- **Invitation modal:** Appears on the Dashboard immediately after login if pending invites exist; should list all pending invites in one modal rather than one modal per invite
- **Shared project badge:** On the Dashboard, shared projects can show a small "Shared by [name]" label beneath the project title
- **Disabled controls:** Prefer hiding controls the user cannot use rather than showing them as disabled, to reduce confusion for Viewers

---

## Technical Considerations

- **New table:** `project_collaborators` — see US-001 for schema; requires an Alembic migration
- **Role dependency:** Introduce a `get_project_access()` FastAPI dependency that consolidates role resolution (owner check + collaborator lookup) for reuse across all routers
- **Dashboard query:** The `/projects` list endpoint needs a JOIN or UNION to include accepted collaborations alongside owned projects
- **Frontend role context:** The project detail API response should include a `my_role` field (`owner` | `admin` | `editor` | `viewer`) so the frontend can gate UI controls without a separate request
- **Pending invite check:** Add a `/users/me/invitations` endpoint (or include `pending_invitations` in the `/users/me` response) so the frontend can check for pending invites on login

---

## Success Metrics

- Project owners can send an invitation in under 30 seconds
- Invitees see their pending invitation immediately upon next login (no page reload required after acceptance)
- All role permission boundaries enforced — no API endpoint returns data or performs mutations for unauthorized roles
- Zero orphaned data: removing a collaborator does not delete any chords or songs

---

## Open Questions

- Should Admins be able to change a collaborator's role after invitation (e.g., promote a Viewer to Editor), or is the role fixed at invitation time?
- Should there be a maximum number of collaborators per project?
- If a user's account is deleted, should their collaborations be removed automatically via cascade?

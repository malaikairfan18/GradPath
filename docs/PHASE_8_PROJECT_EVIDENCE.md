# Phase 8 — Project Tracking and Skill Evidence

## 1. Objective

Phase 8 connects GradPath's project recommendation system with project assignment, progress tracking, and explicit skill-evidence submission.

It allows a candidate to select a recommended project, track its status, and submit an explanation of how the project demonstrates a particular skill.

Project completion does not automatically verify skills.

## 2. Implementation

### Main module

`src/gradpath/project_tracking.py`

The module integrates with the existing Phase 6 progress tracker and Phase 7 project catalogue.

### Project catalogue

`data/resources/project_catalogue.csv`

The catalogue defines project IDs, target roles, and the canonical skills associated with each project.

### Database tables

Phase 8 adds two SQLite tables.

**`project_assignments`**

Stores the candidate's project assignments, target role, status, and timestamps.

**`project_events`**

Records assignment and status-change events, including previous and new statuses.

The module reuses Phase 6 tables for learning activities, progress events, assessment attempts, skill evidence, and schema metadata.

## 3. Project assignment

The `assign_project()` function validates the candidate ID, project ID, target role, and compatibility between the project and the selected role.

Duplicate assignments for the same candidate, project, and target role are rejected.

New assignments begin with the `not_started` status.

Each assignment creates an event recording the initial assignment.

## 4. Project status tracking

The `update_project_status()` function enforces the following transitions:

- `not_started` → `in_progress`
- `not_started` → `abandoned`
- `in_progress` → `completed`
- `in_progress` → `abandoned`

Completed and abandoned projects cannot be reopened through the supported transitions.

Status changes are recorded in `project_events`. Start and completion timestamps are maintained when the corresponding statuses are reached.

## 5. Skill-evidence submission

The `submit_project_skill_evidence()` function validates that:

- The assignment exists.
- The supplied candidate owns the assignment.
- The skill ID exists in GradPath's canonical skill vocabulary.
- The skill belongs to the assigned project's catalogue entry.
- The evidence explanation is not empty.

Valid evidence is submitted to the Phase 6 `record_skill_evidence()` function.

Project evidence uses:

- Evidence type: `project`
- Source ID: the project assignment ID
- Initial verification status: `unverified`

Evidence submission records a candidate's claim; it does not independently prove proficiency. Evidence must not be treated as verified merely because a project was assigned or completed.

## 6. Database schema versioning

Phase 8 uses schema version 2.

The initialization process:

1. Checks the existing schema version before modifying the database.
2. Rejects unsupported schema versions newer than the implementation.
3. Reuses Phase 6 database initialization.
4. Creates the Phase 8 tables and indexes if needed.
5. Updates the schema version to 2 as part of the Phase 8 schema transaction.

Tests cover fresh initialization, repeatable initialization, upgrading from version 1, preservation of existing metadata, and rejection of a simulated newer schema version.

## 7. Testing

Test module: `src/test_project_tracking.py`

The test suite covers project assignment, role compatibility, duplicate assignments, valid and invalid status transitions, event history, evidence validation, candidate ownership, canonical skill validation, and database schema versioning.

The full GradPath test suite passed **44 tests** using:

```powershell
python -m unittest discover -s src -p "test_*.py" -v
```

The passing suite provides regression coverage for the tested behavior; it does not establish production readiness or independently validate real-world skill proficiency.

## 8. Limitations and future work

- Project assignments and evidence currently use candidate IDs supplied to the module; authentication and user-facing candidate management are outside this phase.
- Evidence remains unverified until a separate verification process is implemented.
- The module tracks project status but does not itself evaluate submitted project files or code quality.
- Integration with a user interface, project deliverables, automated assessment, and evidence review can be developed in later phases.

## 9. Key files

- `src/gradpath/project_tracking.py`
- `src/test_project_tracking.py`
- `src/gradpath/progress_tracker.py`
- `src/gradpath/project_recommendations.py`
- `data/resources/project_catalogue.csv`
- `data/processed/initial_skill_vocabulary.csv`
- `docs/PHASE_8_PROJECT_EVIDENCE.md`

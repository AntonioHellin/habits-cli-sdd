# Spec 001 — habits-cli-sdd MVP

## Context and Goals
Programming students frequently abandon new study habits due to a lack of visibility and consistency. habits-cli-sdd provides a lightweight, friction-free command-line tool to track daily study habits and visualize consecutive-day streaks directly in the terminal, motivating continuous daily practice.

## Target Audience
Students and developers who spend their time in the terminal. Designed as a single-user local application without accounts or remote synchronization.

## User Stories
- **H1:** As a student, I want to create habits with descriptive names so that I can define what I want to practice regularly.
- **H2:** As a student, I want to mark a habit as completed today so that I can log my daily consistency.
- **H3:** As a student, I want to list my habits alongside their current consecutive-day streak so that I stay motivated to keep it alive.

## Functional Requirements (EARS Acceptance Criteria)

### Habit Creation (H1)
- **RF-1:** WHEN the user executes `habits add <name>` with a non-empty, non-existing name (multi-word names supported with or without quotes), THE SYSTEM SHALL create the habit, persist it, and print a success confirmation message in English (exit code 0).
- **RF-2:** IF the specified name already exists (evaluated case-insensitively and ignoring leading or trailing whitespace), THEN THE SYSTEM SHALL reject the creation, print a conflict message in English, and exit with code 1.
- **RF-3:** IF the specified name is empty or consists solely of whitespace, THEN THE SYSTEM SHALL reject the command, print an error message in English, and exit with code 1.

### Habit Completion (H2)
- **RF-4:** WHEN the user executes `habits done <name>` and a matching habit exists (matched case-insensitively and stripped of outer whitespace), THE SYSTEM SHALL record the system local calendar date (`date.today()`) as completed for that habit and print a confirmation message in English (exit code 0).
- **RF-5:** IF the habit has already been marked as completed for today's local date, THEN THE SYSTEM SHALL inform the user that it was already completed today without creating duplicate records (idempotent operation, exit code 0).
- **RF-6:** IF no matching habit exists (case-insensitively), THEN THE SYSTEM SHALL display an error message in English suggesting running `habits list` and exit with code 1.

### Habit Listing and Streaks (H3)
- **RF-7:** WHEN the user executes `habits list`, THE SYSTEM SHALL output all habits line-by-line using the format `- <name>: <N> day(s) [<done today|pending>]`, sorted primarily by streak descending and secondarily alphabetically by name (case-insensitive) in case of ties (exit code 0).
- **RF-8:** WHILE there are no registered habits in storage, THE SYSTEM SHALL respond to `habits list` with an informative message in English inviting the user to add their first habit (exit code 0).

### Cross-Cutting and Storage Rules
- **RF-9:** THE SYSTEM SHALL calculate a habit's streak as the count of consecutive calendar days completed immediately preceding or including today (using system local date). IF a habit has no completion records, or its most recent record is prior to yesterday, THEN THE SYSTEM SHALL report a streak of 0. Recorded dates strictly in the future relative to system local date SHALL be ignored during streak computation.
- **RF-10:** THE SYSTEM SHALL persist all habit data locally in a single, human-readable JSON file.
- **RF-11:** IF the JSON storage file exists but contains invalid/corrupted JSON data, or cannot be accessed due to file system permission or I/O errors, THEN THE SYSTEM SHALL abort with an informative error message in English without overwriting or destroying existing data (exit code 1).
- **RF-12:** IF the user executes `habits` with no arguments or with an unrecognized subcommand, THEN THE SYSTEM SHALL output usage instructions in English and exit with a non-zero code.

## Non-Functional Requirements
- **Performance:** Instantaneous execution (< 1 second) on standard workstations.
- **Dependencies & Environment:** Self-contained and offline; zero runtime external dependencies (Python 3.12+ standard library only).
- **Portability:** Consistent cross-platform behavior across Windows, macOS, and Linux.
- **Language:** All user-facing text (prompts, errors, help, status messages) and internal identifiers strictly in English.

## Edge Cases Covered
- **Multiple completions on the same day:** Handled by RF-5 (idempotent; no duplicate entries, exit code 0).
- **Day skipped / inactive > 1 day:** Handled by RF-9 (streak resets to 0).
- **Completed yesterday but pending today:** Handled by RF-9 (streak is maintained throughout today).
- **Newly created habit or 0 completions:** Handled by RF-9 (streak reports 0).
- **Future dates in storage:** Handled by RF-9 (ignored in calculation).
- **Multi-word habit names:** Handled by RF-1 and RF-4 (supported with or without surrounding quotes).
- **Name case differences and whitespace:** Handled by RF-2 and RF-4 (trimmed and case-insensitive comparison).
- **First run with missing storage file:** Clean initialization with an empty structure.
- **Corrupted storage file or permission failure:** Handled by RF-11 (fail-safe; no data corruption, exit code 1).
- **Unrecognized command / missing arguments:** Handled by RF-12 (usage help, non-zero exit).

## Out of Scope (MVP)
- Editing or renaming existing habits.
- Deleting habits (`habits delete`).
- Backfilling or logging past/arbitrary dates (`habits done --date`).
- Advanced statistical analytics, charts, or terminal graphs.
- Notifications, background daemons, or scheduled reminders.
- TUI / interactive terminal UI or custom color schemes.
- User accounts, authentication, or cloud/network synchronization.

## Completion Criteria
- All functional requirements (RF-1 through RF-12) covered by automated unit/CLI tests with `pytest -q` passing green.
- Successful manual verification of the core workflow (`add` -> `done` -> `list`).

## Open Doubts
- None. All edge cases, parsing behaviors, streak definitions, and interface formats resolved during specification clarification.

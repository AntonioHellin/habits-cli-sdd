# Spec 002 — Mark Habit as Done Yesterday

## Context and Goals
Users occasionally forget to log their completed habits before going to bed, resulting in unintentional broken streaks even when they practiced consistently. This feature allows users to log a habit completion for yesterday (`--yesterday` / `-y`), enabling them to recover their streak without losing track of their actual consistency.

## Target Audience / Actors
Students and developers tracking their daily study habits who did the work yesterday but did not have access to their terminal or forgot to run the command before midnight.

## User Stories
- **H1:** As a student, I want to mark a habit as done for yesterday using a flag so that I do not break my streak if I forgot to run the CLI before the day ended.

## Functional Requirements (Acceptance Criteria in EARS)
- **RF-1:** WHEN the user executes `habits done <name> --yesterday` (or `habits done <name> -y`) for an existing habit that has not yet been logged for yesterday, THE SYSTEM SHALL record yesterday's local calendar date (`date.today() - timedelta(days=1)`) as completed for that habit and print `Marked '<name>' as done for yesterday.` to stdout (exit code 0).
- **RF-2:** IF the specified habit was already marked as completed for yesterday's local date, THEN THE SYSTEM SHALL print `Habit '<name>' is already marked as done for yesterday.` to stdout without duplicating entries (idempotent operation, exit code 0).
- **RF-3:** IF the specified habit does not exist (evaluated case-insensitively and stripped of outer whitespace), THEN THE SYSTEM SHALL display `Error: Habit '<name>' not found. Use 'habits list' to see available habits.` to stderr and exit with code 1.
- **RF-4:** IF the habit name argument is empty or consists solely of whitespace, THEN THE SYSTEM SHALL print `Error: Habit name cannot be empty.` to stderr and exit with code 1.
- **RF-5:** IF no habit name argument is provided to `habits done`, THEN THE SYSTEM SHALL print CLI usage instructions to stderr and exit with code 2.
- **RF-6:** WHEN a habit is marked done for yesterday, THE SYSTEM SHALL calculate and preserve the streak reflecting consecutive calendar days ending yesterday (or today if today was already completed), while leaving today's status as `[pending]` in `habits list` if today has not yet been marked (exit code 0).
- **RF-7:** IF the storage file is corrupted, unreadable, or cannot be saved during `habits done <name> --yesterday`, THEN THE SYSTEM SHALL print an error starting with `Error: ` to stderr, exit with code 1, and never destroy or overwrite the existing file.

## Non-Functional Requirements
- **Performance:** Instantaneous execution (< 1 second) with zero network calls.
- **Dependencies & Environment:** Built solely on Python 3.12+ standard library (using `argparse` flag support).
- **Portability:** Consistent behavior across Windows, macOS, and Linux based on system local time.
- **Atomic Date Reference:** Local date evaluated once at invocation (`target_date = date.today() - timedelta(days=1)`) to avoid midnight rollover races.
- **Language:** All command flags, user output messages, error text, and documentation strictly in English.

## Edge Cases
- **Yesterday already marked:** Handled by RF-2 (idempotent, prints `Habit '<name>' is already marked as done for yesterday.`, exit code 0).
- **Both yesterday and today marked:** Marking yesterday connects with today, producing a continuous streak (e.g. 2 days or more).
- **Today pending, yesterday marked:** Handled by RF-6 (streak continues ending yesterday; today remains `[pending]`).
- **Gap of multiple days before yesterday:** Marking yesterday produces a streak of 1 day (or extends consecutive days ending yesterday).
- **Habit created today marked for yesterday:** Fully permitted; habits do not constrain completions to be strictly on or after `created_at`.
- **Flag position flexibility:** Supported with flag before or after the name (e.g., `habits done "Study Python" --yesterday` or `habits done -y "Study Python"`).
- **Repeated or combined flag:** Invocations with repeated or combined flags (e.g. `-y --yesterday` or `-y -y`) are parsed cleanly without error.
- **Missing habit name:** Handled by RF-5 (exit code 2).
- **Empty habit name:** Handled by RF-4 (exit code 1).
- **Corrupted data file:** Handled by RF-7 (exit code 1, file preserved).

## Out of Scope
- Logging completions for dates prior to yesterday (e.g., two or more days ago).
- Arbitrary date arguments or date pickers (`--date YYYY-MM-DD`).
- Removing or un-marking previously logged dates (`habits undo`).
- Batch completion of multiple habits in a single invocation.

## Completion Criteria
- All functional requirements (RF-1 through RF-7) covered by automated unit and CLI acceptance tests with `pytest -q` passing green.
- Manual walkthrough verifying `habits done <name> --yesterday` logs completion, preserves/extends streak, and leaves today as `[pending]`.

## Open Questions
- None. All ambiguities, message formats, exit codes, and edge cases resolved.

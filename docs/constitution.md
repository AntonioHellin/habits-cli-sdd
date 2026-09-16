# Constitution — habits-cli-sdd

Non-negotiable principles governing every spec, plan, and task of the project:

1. **Stack simplicity**: Python 3.12+ and standard library only in production; pytest exclusively in development.
2. **The spec rules**: No behavior is implemented unless defined in the active spec; ask questions when in doubt.
3. **Logic and interface separation**: The core does not interact with console or I/O; the CLI is a thin, decoupled layer.
4. **Tests as quality gate**: Every task concludes with green tests; moving forward with failing tests is forbidden.
5. **Transparent persistence**: Local storage in a single human-readable JSON file, without databases or network.
6. **Language**: All code, identifiers, tests, documentation, and user-facing CLI messages strictly in English.

## MANDATORY: FOLLOW THE SUNFLOW ENGINEERING PROTOCOL

Before executing this request, strictly follow the repository's engineering and documentation conventions.

1. Read the root `AGENTS.md`, `learned.md`, and `progress.md` before making any changes.
2. Read the relevant directory-specific Markdown documentation before navigating or modifying that part of the codebase.
3. Follow all applicable nested `AGENTS.md` instructions.
4. Understand the existing implementation before creating, modifying, or deleting files.
5. Respect the established architecture, technology stack, naming conventions, coding standards, and existing business logic.
6. Do not duplicate existing functionality or introduce unnecessary dependencies.

### Mandatory documentation synchronization

Every codebase change MUST be accompanied by the appropriate documentation updates.

- **New file:** Immediately document it in its parent directory's `<directory_name>.md`.
- **New directory:** Create its corresponding `<directory_name>.md` and document all its contents.
- **Modified file:** Update its documented responsibility if its purpose or logic changes.
- **Deleted or renamed file:** Update all affected directory documentation and references.
- **Architectural or technical change:** Update root `learned.md`.
- **Requirement or task progress change:** Update root `progress.md`.
- **API or database change:** Update the relevant technical documentation.

Every directory's Markdown file must accurately describe its immediate subdirectories and every immediate file, using concise, meaningful one-line descriptions.

Never leave stale, incomplete or fabricated documentation.

### Mandatory completion procedure

Before considering this task complete:

1. Verify that the implementation works.
2. Run relevant tests, checks or builds.
3. Update all affected documentation.
4. Synchronize `learned.md` and `progress.md` where applicable.
5. Check that directory documentation accurately reflects the current filesystem.
6. Report what changed, what was tested, and what remains incomplete or blocked.

### Important restrictions

- Do not skip documentation updates even for small changes.
- Do not mark unimplemented functionality as completed.
- Do not silently change architectural decisions.
- Do not overwrite existing work without inspection.
- Do not claim successful testing without actually running the tests.
- If an instruction conflicts with the existing architecture, explain the conflict before proceeding.
- If a necessary architectural decision is unclear, ask before making an irreversible change.

**This protocol applies to every task, including bug fixes, refactoring, feature development, API changes, database modifications, configuration changes and exploratory technical work.**

Treat documentation maintenance as part of implementation, not as a separate optional task.

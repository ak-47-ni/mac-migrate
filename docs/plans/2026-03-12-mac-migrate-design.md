# Mac Migrate Design

**Goal**
Build a macOS-focused migration utility that safely exports and restores a developer workstation baseline: Homebrew packages, Conda environment definitions, Java inventory, and selected dotfiles such as shell, Git, and Codex configuration. Secrets, tokens, SSH keys, and login sessions stay out of scope.

**Why this shape**
The first version optimizes for repeatable rebuilds rather than full machine cloning. A Python CLI gives us a maintainable command surface, while shell wrappers keep usage simple on a fresh Mac.

## Scope
- Support macOS only in v1.
- Provide both a CLI and one-command shell entrypoints.
- Backup Homebrew state into a `Brewfile` when `brew` exists.
- Backup Conda environments as YAML definitions when `conda` exists.
- Backup Java inventory from installed runtimes and related tool metadata.
- Backup safe dotfiles and directories: `.zshrc`, `.zprofile`, `.gitconfig`, `.gitignore_global`, `.codex/` when present.
- Produce a manifest describing what was captured and what was skipped.
- Restore from the generated bundle with safety checks and clear skipped/manual steps.

## Non-Goals
- No migration of secrets, keychains, SSH material, browser sessions, or app login state.
- No package installation for tools not represented in the backup bundle.
- No GUI in v1.
- No cross-platform support in v1.

## Architecture
- Python package `mac_migrate` exposes `backup`, `restore`, and `doctor` subcommands.
- Collectors gather state into an output directory under `output/<timestamp>/`.
- Restorers consume the bundle and perform idempotent restore actions.
- Shell scripts call the Python CLI for users who want a single file entrypoint.
- Tests cover manifest generation, safe file collection, and restore command planning.

## Data Flow
1. User runs `scripts/backup.sh` or `python -m mac_migrate.cli backup`.
2. Collectors detect installed tools and export artifacts into a bundle directory.
3. A `manifest.json` file records included artifacts, skipped items, timestamps, and restore hints.
4. User copies the bundle to the new machine.
5. User runs `scripts/restore.sh <bundle>` or the CLI equivalent.
6. Restorers validate the bundle, perform restore steps, and print manual follow-up items.

## Safety Model
- Explicit allowlist for copied dotfiles.
- Refuse to read likely-secret files such as `.ssh`, `.npmrc`, `.pypirc`, `.aws`, or real `.env` files.
- Restore writes only allowlisted targets.
- Restore supports `--dry-run` for command preview.
- External commands are logged in the manifest and console output.

## Testing Strategy
- Use pytest.
- Start with red-green tests for backup manifest generation.
- Add tests for dotfile allowlist behavior.
- Add tests for restore planning and dry-run output.
- Keep command execution behind wrappers so tests can stub subprocess calls.

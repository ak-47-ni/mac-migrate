# Mac Migrate Release Command Design

**Goal**
Add a `release` command that creates a migration bundle, generates a default archive, and emits machine-readable and human-readable release metadata for transferring the bundle to a new Mac.

## Approved choices
- Add `release` as a dedicated command instead of overloading `backup`.
- Keep the existing bundle directory and zip archive behavior.
- Generate both `SHA256SUMS.txt` and `release.json` for each release.
- Keep the release command local-only in v1; no upload or remote publish step.

## Scope
- Add `mac-migrate release` and `scripts/release.sh`.
- Reuse the existing backup flow to create `output/<timestamp>/` and `output/<timestamp>.zip`.
- Generate `output/<timestamp>.SHA256SUMS.txt`.
- Generate `output/<timestamp>.release.json`.
- Print all generated paths at the end of the command.
- Update tests and README.

## Non-Goals
- No cloud upload, GitHub Release creation, or network transfer.
- No cryptographic signing beyond SHA-256 checksums.
- No change to the existing restore safety allowlist.

## Command Shape
- `python3 -m mac_migrate.cli release --output-root ./output`
- `python3 -m mac_migrate.cli release --output-root ./output --timestamp 20260312T130000Z`
- `./scripts/release.sh --output-root ./output`

## Output Contract
For a release timestamp `20260312T130000Z`, the command creates:
- `output/20260312T130000Z/`
- `output/20260312T130000Z.zip`
- `output/20260312T130000Z.SHA256SUMS.txt`
- `output/20260312T130000Z.release.json`

## Data Flow
1. `release` calls the existing backup flow with archive enabled.
2. The command verifies that the archive exists after backup completes.
3. The command reads `manifest.json` from the bundle.
4. The command computes SHA-256 for the zip archive and selected bundle files.
5. The command writes the checksum file.
6. The command writes the JSON release metadata file.
7. The command prints a concise summary with all artifact paths.

## Release Metadata
`release.json` should include:
- `timestamp`
- `bundle_dir`
- `archive_path`
- `archive_sha256`
- `archive_size_bytes`
- `manifest_path`
- `checksums_path`
- `manual_steps`
- `dotfiles`
- `tool_exports`
- `skipped`

## Checksum File
`SHA256SUMS.txt` should contain at least:
- SHA-256 for `<timestamp>.zip`
- SHA-256 for `<timestamp>/manifest.json`

Format should follow the standard `<sha256><two spaces><filename>` pattern so it works with common shell tooling.

## Error Handling
- If backup fails, `release` exits immediately and creates no summary artifacts.
- If the archive is missing after backup, `release` fails with a clear error.
- If `manifest.json` is missing or invalid JSON, `release` fails with a clear error.
- Missing tools such as `conda` are not fatal if backup already recorded them as skipped.

## Testing
- Add unit tests for checksum generation and release metadata generation.
- Add CLI tests for `release` success output.
- Verify the command produces all four expected artifacts.
- Verify `release.json` contains values derived from the manifest.
- Verify `SHA256SUMS.txt` uses the expected format.

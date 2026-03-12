# Mac Migrate Archive Enhancement Design

**Goal**
Add repository bootstrap and default zip archive generation to `mac-migrate`, while keeping the existing safe backup/restore workflow intact.

## Approved choices
- Keep the bundle directory after backup.
- Generate a zip archive by default.
- Add Git initialization for the project, but do not auto-commit.
- Allow restore from either a bundle directory or a `.zip` archive.

## Scope
- Create `.gitignore` with safe defaults for this repo.
- Initialize `.git` if it does not exist.
- Make backup produce both `output/<timestamp>/` and `output/<timestamp>.zip` by default.
- Add `--no-archive` to skip zip generation when needed.
- Make restore accept either the bundle directory or the zip file path.
- Update tests and README.

## Safety
- Zip only contains the generated safe bundle contents.
- Restore from zip extracts into a temporary directory before validation.
- Existing allowlist rules remain unchanged.

## Testing
- Test default archive creation.
- Test zip-based restore planning.
- Test CLI output includes archive path.
- Verify `.gitignore` content exists in the repo.

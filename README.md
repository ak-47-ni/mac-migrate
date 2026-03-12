# mac-migrate

A safe macOS developer environment migration utility.

## Scope
- Homebrew package export via `Brewfile`
- Conda environment definitions as `environment.yml`
- Java inventory export
- Safe dotfile backup and restore for shell, Git, and selected Codex config
- Default zip archive generation for each backup bundle
- Release metadata generation with checksums for transfer verification

## Safety
- Does not copy SSH keys, tokens, or login state
- Only restores allowlisted paths
- Restore defaults to preview mode unless `--apply` is used
- Zip restore extracts into a temporary directory before restore planning or apply

## Usage
```bash
python3 -m mac_migrate.cli backup --output-root ./output
python3 -m mac_migrate.cli backup --output-root ./output --no-archive
python3 -m mac_migrate.cli release --output-root ./output
python3 -m mac_migrate.cli restore ./output/20260312T120000Z
python3 -m mac_migrate.cli restore ./output/20260312T120000Z.zip
python3 -m mac_migrate.cli restore ./output/20260312T120000Z.zip --apply
python3 -m mac_migrate.cli doctor
```

Shell wrappers:
```bash
./scripts/backup.sh --output-root ./output
./scripts/release.sh --output-root ./output
./scripts/restore.sh ./output/20260312T120000Z.zip --apply
```

## License
- Licensed under `GPL-3.0`. See `LICENSE`.

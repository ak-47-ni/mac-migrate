# mac-migrate

> Safely export, package, and restore a macOS developer environment when moving to a new machine.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-macOS-000000?logo=apple&logoColor=white)

## Why

Every time a programmer switches to a new Mac, the same annoying work comes back:
reinstalling `Homebrew`, rebuilding `Conda` environments, checking Java versions,
restoring shell aliases, Git config, and tools like Codex.

`mac-migrate` is built for that exact problem.
It does **not** try to do a full machine clone.
Instead, it focuses on a safer, repeatable workflow:
export what matters, package it, verify it, and restore it on the new machine.

## What It Does

| Command | Purpose |
| --- | --- |
| `backup` | Create a safe migration bundle and a default `.zip` archive |
| `release` | Create a bundle plus `SHA256SUMS.txt` and `release.json` for transfer verification |
| `restore` | Preview or apply a restore from a bundle directory or `.zip` archive |
| `doctor` | Check whether the current Mac has the expected tools and safe config files |

## Quick Start

Clone the repository:

```bash
git clone https://github.com/ak-47-ni/mac-migrate.git
cd mac-migrate
```

Check the current machine:

```bash
python3 -m mac_migrate.cli doctor
```

Create a portable migration release on the old Mac:

```bash
./scripts/release.sh --output-root ./output
```

Preview restore actions on the new Mac:

```bash
./scripts/restore.sh ./output/<timestamp>.zip
```

Apply the restore when the preview looks correct:

```bash
./scripts/restore.sh ./output/<timestamp>.zip --apply
```

If you also want to execute `brew` and `conda` restore commands:

```bash
./scripts/restore.sh ./output/<timestamp>.zip --apply --apply-tooling
```

## Typical Workflow

### On the old Mac

Create a release package:

```bash
./scripts/release.sh --output-root ./output
```

This generates:

- `output/<timestamp>/`
- `output/<timestamp>.zip`
- `output/<timestamp>.SHA256SUMS.txt`
- `output/<timestamp>.release.json`

Copy the `.zip`, `SHA256SUMS.txt`, and `release.json` to the new machine.

### On the new Mac

Preview the restore first:

```bash
./scripts/restore.sh ./output/<timestamp>.zip
```

Then apply the safe file restore:

```bash
./scripts/restore.sh ./output/<timestamp>.zip --apply
```

Optionally restore package/tooling definitions too:

```bash
./scripts/restore.sh ./output/<timestamp>.zip --apply --apply-tooling
```

## Release Artifacts

A `release` run produces four useful outputs:

- `output/<timestamp>/` — the unpacked migration bundle
- `output/<timestamp>.zip` — the transfer archive for the new machine
- `output/<timestamp>.SHA256SUMS.txt` — checksum file for validating the archive
- `output/<timestamp>.release.json` — machine-readable metadata about the release contents

The metadata file includes the timestamp, bundle path, archive path, archive hash,
archive size, manual follow-up steps, exported dotfiles, tool exports, and skipped items.

## Safe by Default

This project is intentionally conservative.
It only restores allowlisted configuration files and avoids copying high-risk secrets.

Included examples:

- `.zshrc`
- `.zprofile`
- `.gitconfig`
- `.gitignore_global`
- selected files under `.codex/`

Not migrated:

- `.ssh` keys
- login sessions
- tokens and secret auth files
- non-allowlisted files under your home directory

This keeps the workflow closer to **rebuild + verify** than **blindly clone everything**.

## Commands

Use the Python CLI directly:

```bash
python3 -m mac_migrate.cli backup --output-root ./output
python3 -m mac_migrate.cli backup --output-root ./output --no-archive
python3 -m mac_migrate.cli release --output-root ./output
python3 -m mac_migrate.cli restore ./output/20260312T120000Z
python3 -m mac_migrate.cli restore ./output/20260312T120000Z.zip
python3 -m mac_migrate.cli restore ./output/20260312T120000Z.zip --apply
python3 -m mac_migrate.cli doctor
```

Or use the shell wrappers:

```bash
./scripts/backup.sh --output-root ./output
./scripts/release.sh --output-root ./output
./scripts/restore.sh ./output/20260312T120000Z.zip --apply
```

## Roadmap

- Add a cleaner installation story for first-time users
- Add richer GitHub homepage content such as screenshots or a short demo GIF
- Explore Windows and Linux support beyond macOS
- Add optional publish targets for release bundles

## License

Licensed under `GPL-3.0`. See `LICENSE`.

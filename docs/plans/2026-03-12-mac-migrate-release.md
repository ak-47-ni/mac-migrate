# Mac Migrate Release Command Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a `release` command that wraps backup, emits checksum metadata, and produces a portable release manifest for migration bundles.

**Architecture:** Keep `backup` focused on bundle creation and archiving, and add a new `release` module that layers checksum and metadata generation on top. Wire the CLI and shell wrapper to the new release flow, then lock behavior in with focused pytest coverage.

**Tech Stack:** Python 3 standard library, pytest, Bash

---

### Task 1: Add failing tests for release artifacts

**Files:**
- Modify: `tests/test_cli.py`
- Create: `tests/test_release.py`

**Step 1: Write the failing test**

```python
def test_create_release_writes_checksum_and_metadata(tmp_path):
    result = create_release(...)
    assert result.archive_path.exists()
    assert result.checksums_path.exists()
    assert result.metadata_path.exists()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_release.py tests/test_cli.py::test_cli_release_creates_release_artifacts -v`
Expected: FAIL because the release module and CLI command do not exist.

**Step 3: Write minimal implementation**

Create the release module, result dataclass, and CLI plumbing needed to generate the artifacts.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_release.py tests/test_cli.py::test_cli_release_creates_release_artifacts -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add tests/test_release.py tests/test_cli.py mac_migrate/release.py mac_migrate/cli.py
git commit -m "feat: add release artifact generation"
```

### Task 2: Implement checksum and metadata formatting

**Files:**
- Modify: `mac_migrate/release.py`
- Test: `tests/test_release.py`

**Step 1: Write the failing test**

```python
def test_release_metadata_contains_manifest_values(tmp_path):
    result = create_release(...)
    payload = json.loads(result.metadata_path.read_text())
    assert payload["manual_steps"]
    assert payload["archive_sha256"]
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_release.py::test_release_metadata_contains_manifest_values -v`
Expected: FAIL because metadata is incomplete.

**Step 3: Write minimal implementation**

Compute SHA-256, archive size, and manifest-derived fields, then write the checksum and JSON files.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_release.py::test_release_metadata_contains_manifest_values -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add mac_migrate/release.py tests/test_release.py
git commit -m "feat: add release metadata and checksums"
```

### Task 3: Add CLI and shell wrapper support

**Files:**
- Modify: `mac_migrate/cli.py`
- Create: `scripts/release.sh`
- Modify: `README.md`
- Test: `tests/test_cli.py`

**Step 1: Write the failing test**

```python
def test_cli_release_creates_release_artifacts(tmp_path, capsys):
    exit_code = cli.main(["release", ...])
    assert exit_code == 0
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli.py::test_cli_release_creates_release_artifacts -v`
Expected: FAIL because the CLI command and wrapper do not exist.

**Step 3: Write minimal implementation**

Add the argparse subcommand, shell wrapper, and README examples.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli.py::test_cli_release_creates_release_artifacts -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add mac_migrate/cli.py scripts/release.sh README.md tests/test_cli.py
git commit -m "feat: add release command entrypoints"
```

### Task 4: Run full verification

**Files:**
- Modify: `README.md`

**Step 1: Re-read docs and command output expectations**

Confirm README examples match the final CLI behavior.

**Step 2: Run full verification**

Run: `pytest -q && bash -n scripts/backup.sh scripts/restore.sh scripts/release.sh && python3 -m mac_migrate.cli release --output-root /tmp/mac-migrate-release-check --timestamp 20260312T130000Z`
Expected: tests pass, wrapper syntax is valid, and the command creates the release artifacts.

**Step 3: Commit**

```bash
git add README.md scripts/release.sh
git commit -m "docs: document release workflow"
```

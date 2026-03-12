# Mac Migrate Archive Enhancement Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add git bootstrap, default zip archive generation, and zip restore support to the macOS migration utility.

**Architecture:** Extend backup to optionally archive the generated bundle directory into a sibling zip file. Extend restore to resolve either a directory bundle or a zip archive into a validated bundle path, while keeping all write operations behind the existing allowlist.

**Tech Stack:** Python 3 standard library, pytest, Bash, Git

---

### Task 1: Add failing tests for archive behavior

**Files:**
- Modify: `tests/test_backup.py`
- Modify: `tests/test_restore.py`
- Modify: `tests/test_cli.py`

**Step 1: Write the failing tests**
- Add a backup test that expects `<timestamp>.zip` to be created by default.
- Add a restore test that passes a zip archive and expects planned actions.
- Add a CLI test that expects archive path output.

**Step 2: Run tests to verify they fail**
Run: `pytest tests/test_backup.py tests/test_restore.py tests/test_cli.py -q`
Expected: FAIL because archive support does not exist.

**Step 3: Write minimal implementation**
Implement archive creation and zip resolution.

**Step 4: Run tests to verify they pass**
Run: `pytest tests/test_backup.py tests/test_restore.py tests/test_cli.py -q`
Expected: PASS.

### Task 2: Add repo bootstrap

**Files:**
- Create: `.gitignore`
- Modify: `README.md`

**Step 1: Add repo bootstrap assets**
Create `.gitignore` and initialize `.git` when missing.

**Step 2: Verify repo bootstrap**
Run: `git rev-parse --show-toplevel`
Expected: exit 0 inside `/Users/ljs/mac-migrate`.

### Task 3: Final verification

**Files:**
- Modify: `README.md`

**Step 1: Update docs**
Document default zip output and zip restore usage.

**Step 2: Run full verification**
Run: `pytest -q && bash -n scripts/backup.sh scripts/restore.sh && python3 -m mac_migrate.cli doctor >/tmp/mac_migrate_doctor.txt`
Expected: all tests pass, shell syntax is valid, CLI command exits 0.

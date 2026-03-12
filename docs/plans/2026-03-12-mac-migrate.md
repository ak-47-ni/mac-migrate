# Mac Migrate Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a macOS-only migration utility with a Python CLI and shell wrappers that can safely back up and restore Homebrew packages, Conda environment definitions, Java inventory, and selected dotfiles without touching secrets.

**Architecture:** The project uses a small Python package for command parsing and migration logic, plus shell wrappers for convenience. Backup collectors export artifacts into timestamped bundle directories, restore logic replays only allowlisted actions, and tests lock in manifest shape and safety behavior.

**Tech Stack:** Python 3 standard library, pytest, Bash

---

### Task 1: Scaffold project metadata

**Files:**
- Create: `pyproject.toml`
- Create: `README.md`
- Create: `mac_migrate/__init__.py`
- Create: `tests/test_smoke.py`

**Step 1: Write the failing test**

```python
def test_package_exposes_version():
    import mac_migrate
    assert isinstance(mac_migrate.__version__, str)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_smoke.py -v`
Expected: FAIL because package files do not exist yet.

**Step 3: Write minimal implementation**

Create the package metadata and expose `__version__`.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_smoke.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add pyproject.toml README.md mac_migrate/__init__.py tests/test_smoke.py
git commit -m "feat: scaffold mac migrate package"
```

### Task 2: Add backup bundle creation

**Files:**
- Create: `mac_migrate/backup.py`
- Create: `tests/test_backup.py`

**Step 1: Write the failing test**

```python
def test_backup_creates_manifest_for_allowlisted_dotfiles(tmp_path):
    ...
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_backup.py::test_backup_creates_manifest_for_allowlisted_dotfiles -v`
Expected: FAIL because backup logic is missing.

**Step 3: Write minimal implementation**

Implement bundle directory creation, allowlisted dotfile copying, and manifest generation.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_backup.py::test_backup_creates_manifest_for_allowlisted_dotfiles -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add mac_migrate/backup.py tests/test_backup.py
git commit -m "feat: add safe backup bundle creation"
```

### Task 3: Capture tool inventories

**Files:**
- Modify: `mac_migrate/backup.py`
- Create: `mac_migrate/system_tools.py`
- Modify: `tests/test_backup.py`

**Step 1: Write the failing test**

```python
def test_backup_records_tool_exports_when_commands_exist(tmp_path):
    ...
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_backup.py::test_backup_records_tool_exports_when_commands_exist -v`
Expected: FAIL because command export support is absent.

**Step 3: Write minimal implementation**

Add command wrappers for Brew, Conda, and Java inventory export with test doubles.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_backup.py::test_backup_records_tool_exports_when_commands_exist -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add mac_migrate/backup.py mac_migrate/system_tools.py tests/test_backup.py
git commit -m "feat: export brew conda and java inventories"
```

### Task 4: Add restore planning and dry-run

**Files:**
- Create: `mac_migrate/restore.py`
- Modify: `tests/test_backup.py`
- Create: `tests/test_restore.py`

**Step 1: Write the failing test**

```python
def test_restore_plan_lists_safe_actions_from_manifest(tmp_path):
    ...
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_restore.py::test_restore_plan_lists_safe_actions_from_manifest -v`
Expected: FAIL because restore planning does not exist.

**Step 3: Write minimal implementation**

Implement bundle validation, dry-run planning, and restore of allowlisted dotfiles.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_restore.py::test_restore_plan_lists_safe_actions_from_manifest -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add mac_migrate/restore.py tests/test_restore.py tests/test_backup.py
git commit -m "feat: add restore planning and dry run"
```

### Task 5: Add CLI and shell wrappers

**Files:**
- Create: `mac_migrate/cli.py`
- Create: `scripts/backup.sh`
- Create: `scripts/restore.sh`
- Create: `tests/test_cli.py`

**Step 1: Write the failing test**

```python
def test_cli_backup_creates_bundle(tmp_path, monkeypatch, capsys):
    ...
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli.py::test_cli_backup_creates_bundle -v`
Expected: FAIL because the CLI entrypoint does not exist.

**Step 3: Write minimal implementation**

Add argparse subcommands for `backup`, `restore`, and `doctor`, then wire shell wrappers to the CLI.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli.py::test_cli_backup_creates_bundle -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add mac_migrate/cli.py scripts/backup.sh scripts/restore.sh tests/test_cli.py
git commit -m "feat: add cli and wrapper scripts"
```

### Task 6: Verify end-to-end behavior

**Files:**
- Modify: `README.md`
- Modify: `tests/test_cli.py`

**Step 1: Write the failing test**

```python
def test_cli_doctor_reports_detected_tools(monkeypatch, capsys):
    ...
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli.py::test_cli_doctor_reports_detected_tools -v`
Expected: FAIL because doctor output is incomplete.

**Step 3: Write minimal implementation**

Complete doctor output and update usage docs.

**Step 4: Run test to verify it passes**

Run: `pytest -q`
Expected: PASS with all tests green.

**Step 5: Commit**

```bash
git add README.md tests/test_cli.py
git commit -m "docs: finalize usage and verification"
```

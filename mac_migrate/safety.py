"""Allowlist and path safety helpers."""

from __future__ import annotations

from pathlib import Path

SAFE_HOME_FILES = (
    ".zshrc",
    ".zprofile",
    ".gitconfig",
    ".gitignore_global",
)
SAFE_CODEX_FILES = (
    ".codex/AGENTS.md",
    ".codex/config.toml",
    ".codex/config.yaml",
    ".codex/config.yml",
    ".codex/settings.json",
)


def allowlisted_relative_paths() -> tuple[str, ...]:
    return SAFE_HOME_FILES + SAFE_CODEX_FILES


def is_allowlisted_relative_path(relative_path: str) -> bool:
    normalized = relative_path.strip().replace("\\", "/")
    return normalized in allowlisted_relative_paths()


def iter_existing_allowlisted_paths(home_dir: Path) -> list[tuple[str, Path]]:
    matches: list[tuple[str, Path]] = []
    for relative_path in allowlisted_relative_paths():
        source = home_dir / relative_path
        if source.is_file():
            matches.append((relative_path, source))
    return matches


def collect_codex_skips(home_dir: Path) -> list[dict[str, str]]:
    codex_dir = home_dir / ".codex"
    skipped: list[dict[str, str]] = []
    if not codex_dir.is_dir():
        return skipped
    for candidate in codex_dir.rglob("*"):
        if not candidate.is_file():
            continue
        relative_path = candidate.relative_to(home_dir).as_posix()
        if not is_allowlisted_relative_path(relative_path):
            skipped.append({"path": relative_path, "reason": "not allowlisted"})
    return skipped


def resolve_home_target(home_dir: Path, relative_path: str) -> Path:
    target = home_dir / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    return target

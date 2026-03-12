"""Restore logic for migration bundles."""

from __future__ import annotations

import json
import shutil
import tempfile
import zipfile
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterator, Sequence

from .safety import is_allowlisted_relative_path, resolve_home_target
from .system_tools import command_exists, run_command

CommandRunner = Callable[[Sequence[str]], object]
CommandExists = Callable[[str], bool]


@dataclass(frozen=True)
class RestoreAction:
    description: str
    kind: str
    relative_path: str | None = None
    command: tuple[str, ...] = ()


@dataclass
class RestoreResult:
    applied: list[str] = field(default_factory=list)
    planned: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)


@contextmanager
def prepared_bundle_path(bundle_path: Path) -> Iterator[Path]:
    if bundle_path.is_dir():
        yield bundle_path
        return
    if bundle_path.suffix != ".zip":
        raise ValueError(f"unsupported bundle path: {bundle_path}")
    with tempfile.TemporaryDirectory(prefix="mac_migrate_") as temp_dir:
        temp_root = Path(temp_dir)
        with zipfile.ZipFile(bundle_path) as archive:
            archive.extractall(temp_root)
        manifest_paths = list(temp_root.rglob("manifest.json"))
        if not manifest_paths:
            raise FileNotFoundError("manifest.json not found in archive")
        yield manifest_paths[0].parent



def _load_manifest(bundle_dir: Path) -> dict:
    manifest_path = bundle_dir / "manifest.json"
    return json.loads(manifest_path.read_text(encoding="utf-8"))



def _iter_dotfile_actions(bundle_dir: Path, home_dir: Path, manifest: dict) -> list[RestoreAction]:
    actions: list[RestoreAction] = []
    for relative_path in manifest.get("artifacts", {}).get("dotfiles", []):
        if not is_allowlisted_relative_path(relative_path):
            continue
        source = bundle_dir / "dotfiles" / relative_path
        target = home_dir / relative_path
        if not source.exists():
            continue
        actions.append(
            RestoreAction(
                description=f"Copy {relative_path} -> {target}",
                kind="copy",
                relative_path=relative_path,
            )
        )
    return actions



def _iter_tool_actions(bundle_dir: Path, which: CommandExists) -> list[RestoreAction]:
    actions: list[RestoreAction] = []
    brewfile = bundle_dir / "Brewfile"
    if brewfile.exists():
        if which("brew"):
            actions.append(
                RestoreAction(
                    description=f"Run brew bundle --file {brewfile}",
                    kind="command",
                    command=("brew", "bundle", "--file", str(brewfile)),
                )
            )
        else:
            actions.append(RestoreAction(description="brew unavailable; skip Brewfile restore", kind="skip"))

    conda_dir = bundle_dir / "conda"
    if conda_dir.is_dir():
        for env_file in sorted(conda_dir.glob("*.environment.yml")):
            if which("conda"):
                actions.append(
                    RestoreAction(
                        description=f"Run conda env create -f {env_file}",
                        kind="command",
                        command=("conda", "env", "create", "-f", str(env_file)),
                    )
                )
            else:
                actions.append(
                    RestoreAction(
                        description=f"conda unavailable; skip {env_file.name}",
                        kind="skip",
                    )
                )
    return actions



def plan_restore_actions(
    *,
    bundle_dir: Path,
    home_dir: Path,
    which: CommandExists = command_exists,
) -> list[RestoreAction]:
    with prepared_bundle_path(bundle_dir) as resolved_bundle_dir:
        manifest = _load_manifest(resolved_bundle_dir)
        return _iter_dotfile_actions(resolved_bundle_dir, home_dir, manifest) + _iter_tool_actions(
            resolved_bundle_dir,
            which,
        )



def restore_bundle(
    *,
    bundle_dir: Path,
    home_dir: Path,
    dry_run: bool = True,
    apply_tooling: bool = False,
    which: CommandExists = command_exists,
    runner: CommandRunner = run_command,
) -> RestoreResult:
    result = RestoreResult()
    with prepared_bundle_path(bundle_dir) as resolved_bundle_dir:
        actions = plan_restore_actions(bundle_dir=resolved_bundle_dir, home_dir=home_dir, which=which)
        result.planned = [action.description for action in actions]
        if dry_run:
            return result

        for action in actions:
            if action.kind == "copy" and action.relative_path:
                source = resolved_bundle_dir / "dotfiles" / action.relative_path
                target = resolve_home_target(home_dir, action.relative_path)
                shutil.copy2(source, target)
                result.applied.append(action.relative_path)
                continue
            if action.kind == "command" and apply_tooling:
                runner(list(action.command))
                result.applied.append(" ".join(action.command))
                continue
            if action.kind != "copy":
                result.skipped.append(action.description)
    return result

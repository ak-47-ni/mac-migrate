"""System command helpers for backup and restore."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Callable, Sequence

CommandRunner = Callable[[Sequence[str]], subprocess.CompletedProcess]
CommandExists = Callable[[str], bool]


def command_exists(command: str) -> bool:
    return shutil.which(command) is not None


def run_command(args: Sequence[str]) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, check=False, text=True)


def derive_conda_env_name(env_path: str) -> str:
    path = Path(env_path)
    if path.parent.name == "envs":
        return path.name
    return "base"


def export_brew_bundle(
    bundle_dir: Path,
    manifest: dict,
    *,
    which: CommandExists,
    runner: CommandRunner,
) -> None:
    if not which("brew"):
        manifest["skipped"].append({"path": "Brewfile", "reason": "brew unavailable"})
        return
    brewfile = bundle_dir / "Brewfile"
    result = runner(["brew", "bundle", "dump", "--file", str(brewfile), "--force"])
    manifest["commands"].append("brew bundle dump --file Brewfile --force")
    if result.returncode == 0 and brewfile.exists():
        manifest["artifacts"]["tool_exports"].append("Brewfile")
        return
    manifest["skipped"].append({"path": "Brewfile", "reason": "brew export failed"})


def export_conda_envs(
    bundle_dir: Path,
    manifest: dict,
    *,
    which: CommandExists,
    runner: CommandRunner,
) -> None:
    if not which("conda"):
        manifest["skipped"].append({"path": "conda", "reason": "conda unavailable"})
        return
    result = runner(["conda", "env", "list", "--json"])
    manifest["commands"].append("conda env list --json")
    if result.returncode != 0:
        manifest["skipped"].append({"path": "conda", "reason": "conda env list failed"})
        return
    payload = json.loads(result.stdout or "{}")
    env_paths = payload.get("envs", [])
    conda_dir = bundle_dir / "conda"
    conda_dir.mkdir(parents=True, exist_ok=True)
    for env_path in env_paths:
        env_name = derive_conda_env_name(env_path)
        export_result = runner(["conda", "env", "export", "--name", env_name, "--no-builds"])
        manifest["commands"].append(f"conda env export --name {env_name} --no-builds")
        if export_result.returncode != 0:
            manifest["skipped"].append({"path": f"conda/{env_name}.environment.yml", "reason": "conda export failed"})
            continue
        target = conda_dir / f"{env_name}.environment.yml"
        target.write_text(export_result.stdout, encoding="utf-8")
        manifest["artifacts"]["tool_exports"].append(f"conda/{target.name}")


def export_java_inventory(
    bundle_dir: Path,
    manifest: dict,
    *,
    which: CommandExists,
    runner: CommandRunner,
) -> None:
    if not which("java"):
        manifest["skipped"].append({"path": "java", "reason": "java unavailable"})
        return
    java_dir = bundle_dir / "java"
    java_dir.mkdir(parents=True, exist_ok=True)
    result = runner(["java", "-version"])
    manifest["commands"].append("java -version")
    if result.returncode != 0:
        manifest["skipped"].append({"path": "java/java-version.txt", "reason": "java version failed"})
        return
    output = "".join(part for part in (result.stdout, result.stderr) if part)
    target = java_dir / "java-version.txt"
    target.write_text(output, encoding="utf-8")
    manifest["artifacts"]["tool_exports"].append("java/java-version.txt")

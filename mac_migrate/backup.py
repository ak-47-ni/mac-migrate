"""Backup logic for safe migration bundles."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from .safety import collect_codex_skips, iter_existing_allowlisted_paths
from .system_tools import (
    command_exists,
    export_brew_bundle,
    export_conda_envs,
    export_java_inventory,
    run_command,
)


def _timestamp_value(timestamp: str | None) -> str:
    if timestamp:
        return timestamp
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")



def create_archive_for_bundle(bundle_dir: Path) -> Path:
    archive_base = bundle_dir.parent / bundle_dir.name
    archive_path = shutil.make_archive(
        str(archive_base),
        "zip",
        root_dir=bundle_dir.parent,
        base_dir=bundle_dir.name,
    )
    return Path(archive_path)



def create_backup_bundle(
    *,
    home_dir: Path,
    output_root: Path,
    timestamp: str | None = None,
    archive: bool = True,
    which=command_exists,
    runner=run_command,
) -> Path:
    bundle_name = _timestamp_value(timestamp)
    bundle_dir = output_root / bundle_name
    bundle_dir.mkdir(parents=True, exist_ok=False)
    dotfiles_dir = bundle_dir / "dotfiles"
    dotfiles_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "bundle_name": bundle_name,
        "created_at": bundle_name,
        "artifacts": {"dotfiles": [], "tool_exports": []},
        "skipped": [],
        "manual_steps": [
            "Re-authenticate Codex and other CLI tools on the new machine.",
            "Review Java inventory and install the required JDK manually if needed.",
        ],
        "commands": [],
        "archive": f"{bundle_name}.zip" if archive else None,
    }

    for relative_path, source in iter_existing_allowlisted_paths(home_dir):
        target = dotfiles_dir / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        manifest["artifacts"]["dotfiles"].append(relative_path)

    manifest["skipped"].extend(collect_codex_skips(home_dir))

    export_brew_bundle(bundle_dir, manifest, which=which, runner=runner)
    export_conda_envs(bundle_dir, manifest, which=which, runner=runner)
    export_java_inventory(bundle_dir, manifest, which=which, runner=runner)

    manifest_path = bundle_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    if archive:
        create_archive_for_bundle(bundle_dir)

    return bundle_dir

"""Release artifact generation for migration bundles."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from .backup import create_backup_bundle
from .system_tools import command_exists, run_command


@dataclass(frozen=True)
class ReleaseResult:
    bundle_dir: Path
    archive_path: Path
    checksums_path: Path
    metadata_path: Path



def _sha256_for_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()



def create_release(
    *,
    home_dir: Path,
    output_root: Path,
    timestamp: str | None = None,
    which=command_exists,
    runner=run_command,
) -> ReleaseResult:
    bundle_dir = create_backup_bundle(
        home_dir=home_dir,
        output_root=output_root,
        timestamp=timestamp,
        archive=True,
        which=which,
        runner=runner,
    )
    bundle_name = bundle_dir.name
    archive_path = output_root / f"{bundle_name}.zip"
    if not archive_path.exists():
        raise FileNotFoundError(f"archive not found: {archive_path}")

    manifest_path = bundle_dir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"manifest not found: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    archive_sha256 = _sha256_for_file(archive_path)
    manifest_sha256 = _sha256_for_file(manifest_path)

    checksums_path = output_root / f"{bundle_name}.SHA256SUMS.txt"
    checksums_path.write_text(
        "\n".join(
            [
                f"{archive_sha256}  {archive_path.name}",
                f"{manifest_sha256}  {bundle_name}/manifest.json",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    metadata_path = output_root / f"{bundle_name}.release.json"
    metadata = {
        "timestamp": bundle_name,
        "bundle_dir": str(bundle_dir),
        "archive_path": str(archive_path),
        "archive_sha256": archive_sha256,
        "archive_size_bytes": archive_path.stat().st_size,
        "manifest_path": str(manifest_path),
        "checksums_path": str(checksums_path),
        "manual_steps": manifest.get("manual_steps", []),
        "dotfiles": manifest.get("artifacts", {}).get("dotfiles", []),
        "tool_exports": manifest.get("artifacts", {}).get("tool_exports", []),
        "skipped": manifest.get("skipped", []),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8")

    return ReleaseResult(
        bundle_dir=bundle_dir,
        archive_path=archive_path,
        checksums_path=checksums_path,
        metadata_path=metadata_path,
    )

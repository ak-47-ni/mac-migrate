import hashlib
import json
from pathlib import Path

from mac_migrate.release import create_release



def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()



def test_create_release_writes_checksum_and_metadata(tmp_path: Path) -> None:
    home_dir = tmp_path / "home"
    output_root = tmp_path / "output"
    home_dir.mkdir()
    output_root.mkdir()
    (home_dir / ".zshrc").write_text("export TEST=1\n", encoding="utf-8")

    result = create_release(
        home_dir=home_dir,
        output_root=output_root,
        timestamp="20260312T130000Z",
    )

    assert result.bundle_dir.exists()
    assert result.archive_path.exists()
    assert result.checksums_path.exists()
    assert result.metadata_path.exists()



def test_release_metadata_contains_manifest_values(tmp_path: Path) -> None:
    home_dir = tmp_path / "home"
    output_root = tmp_path / "output"
    home_dir.mkdir()
    output_root.mkdir()
    (home_dir / ".zshrc").write_text("export TEST=1\n", encoding="utf-8")
    (home_dir / ".gitconfig").write_text("[user]\n\tname = Test\n", encoding="utf-8")

    result = create_release(
        home_dir=home_dir,
        output_root=output_root,
        timestamp="20260312T130500Z",
    )

    payload = json.loads(result.metadata_path.read_text(encoding="utf-8"))
    checksums = result.checksums_path.read_text(encoding="utf-8")
    manifest = json.loads((result.bundle_dir / "manifest.json").read_text(encoding="utf-8"))

    assert payload["timestamp"] == "20260312T130500Z"
    assert payload["archive_path"].endswith("20260312T130500Z.zip")
    assert payload["archive_sha256"] == _sha256(result.archive_path)
    assert payload["archive_size_bytes"] == result.archive_path.stat().st_size
    assert payload["manual_steps"] == manifest["manual_steps"]
    assert payload["dotfiles"] == manifest["artifacts"]["dotfiles"]
    assert payload["tool_exports"] == manifest["artifacts"]["tool_exports"]
    assert payload["skipped"] == manifest["skipped"]
    assert f"{_sha256(result.archive_path)}  20260312T130500Z.zip" in checksums
    assert "20260312T130500Z/manifest.json" in checksums

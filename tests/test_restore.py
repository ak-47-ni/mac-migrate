import json
import shutil
from pathlib import Path

from mac_migrate.restore import plan_restore_actions, restore_bundle



def _make_archive_from_bundle(bundle_dir: Path) -> Path:
    archive_base = bundle_dir.parent / bundle_dir.name
    archive_path = shutil.make_archive(str(archive_base), "zip", root_dir=bundle_dir.parent, base_dir=bundle_dir.name)
    return Path(archive_path)



def test_restore_plan_lists_safe_actions_from_manifest(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    (bundle_dir / "dotfiles" / ".codex").mkdir(parents=True)
    (bundle_dir / "conda").mkdir(parents=True)
    (bundle_dir / "dotfiles" / ".zshrc").write_text("export TEST=1\n", encoding="utf-8")
    (bundle_dir / "dotfiles" / ".codex" / "config.toml").write_text("model='gpt-5'\n", encoding="utf-8")
    (bundle_dir / "Brewfile").write_text('brew "wget"\n', encoding="utf-8")
    (bundle_dir / "conda" / "dev.environment.yml").write_text("name: dev\n", encoding="utf-8")
    (bundle_dir / "manifest.json").write_text(
        json.dumps(
            {
                "artifacts": {
                    "dotfiles": [".zshrc", ".codex/config.toml"],
                    "tool_exports": ["Brewfile", "conda/dev.environment.yml"],
                },
                "skipped": [],
                "manual_steps": [],
            }
        ),
        encoding="utf-8",
    )

    actions = plan_restore_actions(
        bundle_dir=bundle_dir,
        home_dir=tmp_path / "target-home",
        which=lambda command: command in {"brew", "conda"},
    )

    descriptions = [action.description for action in actions]
    assert any("Copy .zshrc" in item for item in descriptions)
    assert any("Copy .codex/config.toml" in item for item in descriptions)
    assert any("brew bundle" in item for item in descriptions)
    assert any("conda env create -f" in item for item in descriptions)



def test_restore_plan_accepts_zip_archive(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    (bundle_dir / "dotfiles").mkdir(parents=True)
    (bundle_dir / "dotfiles" / ".zshrc").write_text("export TEST=1\n", encoding="utf-8")
    (bundle_dir / "manifest.json").write_text(
        json.dumps(
            {
                "artifacts": {
                    "dotfiles": [".zshrc"],
                    "tool_exports": [],
                },
                "skipped": [],
                "manual_steps": [],
            }
        ),
        encoding="utf-8",
    )
    archive_path = _make_archive_from_bundle(bundle_dir)

    actions = plan_restore_actions(
        bundle_dir=archive_path,
        home_dir=tmp_path / "target-home",
        which=lambda command: False,
    )

    assert any("Copy .zshrc" in action.description for action in actions)



def test_restore_bundle_applies_allowlisted_dotfiles(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    home_dir = tmp_path / "target-home"
    home_dir.mkdir()
    (bundle_dir / "dotfiles").mkdir(parents=True)
    (bundle_dir / "dotfiles" / ".gitconfig").write_text("[user]\n\tname = Restored\n", encoding="utf-8")
    (bundle_dir / "manifest.json").write_text(
        json.dumps(
            {
                "artifacts": {
                    "dotfiles": [".gitconfig"],
                    "tool_exports": [],
                },
                "skipped": [],
                "manual_steps": [],
            }
        ),
        encoding="utf-8",
    )

    result = restore_bundle(
        bundle_dir=bundle_dir,
        home_dir=home_dir,
        dry_run=False,
        apply_tooling=False,
        which=lambda command: False,
        runner=lambda args: None,
    )

    assert result.applied == [".gitconfig"]
    assert (home_dir / ".gitconfig").read_text(encoding="utf-8").startswith("[user]")

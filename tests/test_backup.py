import json
import subprocess
import zipfile
from pathlib import Path

from mac_migrate.backup import create_backup_bundle


def _completed(args: list[str], stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=args, returncode=0, stdout=stdout, stderr=stderr)


def test_backup_creates_manifest_for_allowlisted_dotfiles(tmp_path: Path) -> None:
    home_dir = tmp_path / "home"
    output_root = tmp_path / "output"
    home_dir.mkdir()
    output_root.mkdir()

    (home_dir / ".zshrc").write_text("export PATH=/opt/homebrew/bin:$PATH\n", encoding="utf-8")
    (home_dir / ".gitconfig").write_text("[user]\n\tname = Test\n", encoding="utf-8")
    (home_dir / ".codex").mkdir()
    (home_dir / ".codex" / "config.toml").write_text("model = \"gpt-5\"\n", encoding="utf-8")
    (home_dir / ".codex" / "auth.json").write_text('{"token": "secret"}\n', encoding="utf-8")
    (home_dir / ".ssh").mkdir()
    (home_dir / ".ssh" / "id_rsa").write_text("private\n", encoding="utf-8")

    bundle_dir = create_backup_bundle(
        home_dir=home_dir,
        output_root=output_root,
        timestamp="20260312T120000Z",
        which=lambda command: False,
        runner=lambda args: _completed(list(args)),
    )

    archive_path = output_root / "20260312T120000Z.zip"
    assert bundle_dir == output_root / "20260312T120000Z"
    assert archive_path.exists()
    assert (bundle_dir / "dotfiles" / ".zshrc").read_text(encoding="utf-8").startswith("export PATH")
    assert (bundle_dir / "dotfiles" / ".gitconfig").exists()
    assert (bundle_dir / "dotfiles" / ".codex" / "config.toml").exists()
    assert not (bundle_dir / "dotfiles" / ".codex" / "auth.json").exists()
    assert not (bundle_dir / "dotfiles" / ".ssh" / "id_rsa").exists()

    with zipfile.ZipFile(archive_path) as archive:
        names = set(archive.namelist())
        assert "20260312T120000Z/manifest.json" in names
        assert "20260312T120000Z/dotfiles/.zshrc" in names

    manifest = json.loads((bundle_dir / "manifest.json").read_text(encoding="utf-8"))
    assert ".zshrc" in manifest["artifacts"]["dotfiles"]
    assert ".gitconfig" in manifest["artifacts"]["dotfiles"]
    assert ".codex/config.toml" in manifest["artifacts"]["dotfiles"]
    skipped_paths = {item["path"] for item in manifest["skipped"]}
    assert ".codex/auth.json" in skipped_paths



def test_backup_records_tool_exports_when_commands_exist(tmp_path: Path) -> None:
    home_dir = tmp_path / "home"
    output_root = tmp_path / "output"
    home_dir.mkdir()
    output_root.mkdir()

    def fake_which(command: str) -> bool:
        return command in {"brew", "conda", "java"}

    def fake_runner(args: list[str] | tuple[str, ...]) -> subprocess.CompletedProcess:
        command = list(args)
        if command[:3] == ["brew", "bundle", "dump"]:
            file_index = command.index("--file") + 1
            Path(command[file_index]).write_text('brew "wget"\n', encoding="utf-8")
            return _completed(command)
        if command[:4] == ["conda", "env", "list", "--json"]:
            return _completed(command, stdout='{"envs": ["/opt/conda", "/opt/conda/envs/dev"]}')
        if command[:3] == ["conda", "env", "export"]:
            return _completed(command, stdout="name: dev\ndependencies:\n  - python=3.11\n")
        if command[:2] == ["java", "-version"]:
            return _completed(command, stderr='openjdk version "21.0.2"\n')
        raise AssertionError(f"unexpected command: {command}")

    bundle_dir = create_backup_bundle(
        home_dir=home_dir,
        output_root=output_root,
        timestamp="20260312T120500Z",
        which=fake_which,
        runner=fake_runner,
    )

    assert (bundle_dir / "Brewfile").read_text(encoding="utf-8") == 'brew "wget"\n'
    assert (bundle_dir / "conda" / "base.environment.yml").exists()
    assert (bundle_dir / "conda" / "dev.environment.yml").read_text(encoding="utf-8").startswith("name: dev")
    assert "21.0.2" in (bundle_dir / "java" / "java-version.txt").read_text(encoding="utf-8")

    manifest = json.loads((bundle_dir / "manifest.json").read_text(encoding="utf-8"))
    assert "Brewfile" in manifest["artifacts"]["tool_exports"]
    assert "conda/base.environment.yml" in manifest["artifacts"]["tool_exports"]
    assert "conda/dev.environment.yml" in manifest["artifacts"]["tool_exports"]
    assert "java/java-version.txt" in manifest["artifacts"]["tool_exports"]

from pathlib import Path

from mac_migrate import cli



def test_cli_backup_creates_bundle(tmp_path: Path, capsys) -> None:
    home_dir = tmp_path / "home"
    output_root = tmp_path / "output"
    home_dir.mkdir()
    output_root.mkdir()
    (home_dir / ".zshrc").write_text("export TEST=1\n", encoding="utf-8")

    exit_code = cli.main([
        "backup",
        "--home",
        str(home_dir),
        "--output-root",
        str(output_root),
        "--timestamp",
        "20260312T121000Z",
    ])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert (output_root / "20260312T121000Z" / "manifest.json").exists()
    assert (output_root / "20260312T121000Z.zip").exists()
    assert "Backup created" in output
    assert ".zip" in output



def test_cli_release_creates_release_artifacts(tmp_path: Path, capsys) -> None:
    home_dir = tmp_path / "home"
    output_root = tmp_path / "output"
    home_dir.mkdir()
    output_root.mkdir()
    (home_dir / ".zshrc").write_text("export TEST=1\n", encoding="utf-8")

    exit_code = cli.main([
        "release",
        "--home",
        str(home_dir),
        "--output-root",
        str(output_root),
        "--timestamp",
        "20260312T131000Z",
    ])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert (output_root / "20260312T131000Z" / "manifest.json").exists()
    assert (output_root / "20260312T131000Z.zip").exists()
    assert (output_root / "20260312T131000Z.SHA256SUMS.txt").exists()
    assert (output_root / "20260312T131000Z.release.json").exists()
    assert "Release created" in output
    assert "SHA256SUMS" in output
    assert "release.json" in output



def test_cli_doctor_reports_detected_tools(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        cli,
        "collect_doctor_report",
        lambda: {
            "platform": "darwin",
            "tools": {"brew": True, "conda": False, "java": True},
            "dotfiles": {".zshrc": True, ".gitconfig": False, ".codex/config.toml": True},
        },
    )

    exit_code = cli.main(["doctor"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "brew: installed" in output
    assert "conda: missing" in output
    assert ".codex/config.toml: found" in output

from pathlib import Path

import mac_migrate



def test_package_exposes_version() -> None:
    assert isinstance(mac_migrate.__version__, str)



def test_project_has_gitignore_template() -> None:
    gitignore = Path(".gitignore")
    assert gitignore.exists()
    contents = gitignore.read_text(encoding="utf-8")
    assert "output/" in contents
    assert ".pytest_cache/" in contents

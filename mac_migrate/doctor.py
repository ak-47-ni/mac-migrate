"""Environment checks for mac-migrate."""

from __future__ import annotations

import sys
from pathlib import Path

from .safety import allowlisted_relative_paths
from .system_tools import command_exists


def collect_doctor_report(home_dir: Path | None = None) -> dict:
    target_home = home_dir or Path.home()
    return {
        "platform": sys.platform,
        "tools": {
            "brew": command_exists("brew"),
            "conda": command_exists("conda"),
            "java": command_exists("java"),
        },
        "dotfiles": {
            relative_path: (target_home / relative_path).exists()
            for relative_path in allowlisted_relative_paths()
        },
    }

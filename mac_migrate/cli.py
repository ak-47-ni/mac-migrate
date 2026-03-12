"""CLI entrypoint for mac-migrate."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .backup import create_backup_bundle
from .doctor import collect_doctor_report
from .release import create_release
from .restore import plan_restore_actions, restore_bundle



def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mac-migrate")
    subparsers = parser.add_subparsers(dest="command", required=True)

    backup_parser = subparsers.add_parser("backup", help="Create a migration bundle")
    backup_parser.add_argument("--home", default=str(Path.home()))
    backup_parser.add_argument("--output-root", default="output")
    backup_parser.add_argument("--timestamp", default=None)
    backup_parser.add_argument("--no-archive", action="store_true")

    release_parser = subparsers.add_parser("release", help="Create a release bundle with checksums")
    release_parser.add_argument("--home", default=str(Path.home()))
    release_parser.add_argument("--output-root", default="output")
    release_parser.add_argument("--timestamp", default=None)

    restore_parser = subparsers.add_parser("restore", help="Preview or apply a migration bundle")
    restore_parser.add_argument("bundle")
    restore_parser.add_argument("--home", default=str(Path.home()))
    restore_parser.add_argument("--apply", action="store_true")
    restore_parser.add_argument("--apply-tooling", action="store_true")

    subparsers.add_parser("doctor", help="Inspect this machine for migration readiness")
    return parser



def _run_backup(args: argparse.Namespace) -> int:
    bundle_dir = create_backup_bundle(
        home_dir=Path(args.home),
        output_root=Path(args.output_root),
        timestamp=args.timestamp,
        archive=not args.no_archive,
    )
    archive_path = bundle_dir.with_suffix(".zip")
    print(f"Backup created at {bundle_dir}")
    if archive_path.exists():
        print(f"Archive created at {archive_path}")
    return 0



def _run_release(args: argparse.Namespace) -> int:
    result = create_release(
        home_dir=Path(args.home),
        output_root=Path(args.output_root),
        timestamp=args.timestamp,
    )
    print("Release created:")
    print(f"- bundle: {result.bundle_dir}")
    print(f"- archive: {result.archive_path}")
    print(f"- checksums: {result.checksums_path}")
    print(f"- metadata: {result.metadata_path}")
    return 0



def _run_restore(args: argparse.Namespace) -> int:
    bundle_dir = Path(args.bundle)
    home_dir = Path(args.home)
    if not args.apply:
        actions = plan_restore_actions(bundle_dir=bundle_dir, home_dir=home_dir)
        print("Restore plan:")
        for action in actions:
            print(f"- {action.description}")
        return 0

    result = restore_bundle(
        bundle_dir=bundle_dir,
        home_dir=home_dir,
        dry_run=False,
        apply_tooling=args.apply_tooling,
    )
    print("Restore applied:")
    for item in result.applied:
        print(f"- {item}")
    for item in result.skipped:
        print(f"- skipped: {item}")
    return 0



def _run_doctor() -> int:
    report = collect_doctor_report()
    print(f"platform: {report['platform']}")
    print("tools:")
    for name, available in report["tools"].items():
        status = "installed" if available else "missing"
        print(f"{name}: {status}")
    print("dotfiles:")
    for name, present in report["dotfiles"].items():
        status = "found" if present else "missing"
        print(f"{name}: {status}")
    return 0



def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.command == "backup":
        return _run_backup(args)
    if args.command == "release":
        return _run_release(args)
    if args.command == "restore":
        return _run_restore(args)
    return _run_doctor()


if __name__ == "__main__":
    raise SystemExit(main())

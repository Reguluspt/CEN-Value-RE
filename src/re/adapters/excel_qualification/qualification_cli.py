"""Command-line skeleton for Windows Excel qualification."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.re.adapters.excel_qualification.com_runner import WindowsExcelCOMRunner
from src.re.application.services.excel_qualification import (
    QualificationStatus,
    qualify_workbook,
    write_qualification_report,
)
from src.re.application.services.golden_fixture import load_checkpoint_manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cenvalue-re-excel-qualify")
    parser.add_argument("--workbook", required=True)
    parser.add_argument("--profile-id", required=True)
    parser.add_argument("--profile-version", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--report", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    manifest = load_checkpoint_manifest(args.manifest)
    report = qualify_workbook(
        workbook_path=Path(args.workbook),
        profile_id=args.profile_id,
        profile_version=args.profile_version,
        manifest=manifest,
        runner=WindowsExcelCOMRunner(),
    )
    write_qualification_report(report, args.report)
    if report.status is QualificationStatus.PASS:
        return 0
    if report.status is QualificationStatus.NOT_QUALIFIED:
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

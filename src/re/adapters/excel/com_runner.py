"""Windows Microsoft Excel Desktop COM qualification runner.

The import of pywin32 is lazy so non-Windows/core usage remains available.
This adapter opens workbooks with UpdateLinks=0, performs CalculateFullRebuild,
reads required checkpoints, and returns evidence to the application service.
"""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import platform
import time
from typing import Any, Callable

from src.re.ports.excel_qualification import (
    ExcelCheckpointValue,
    ExcelExecutionEvidence,
    ExcelRunnerProbe,
)


RUNNER_ID = "windows-excel-com"
RUNNER_VERSION = "1"


class ExcelCOMUnavailable(RuntimeError):
    pass


def _sha256(path: str | Path) -> str:
    digest = sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_dispatch() -> Callable[[str], Any]:
    try:
        from win32com.client import DispatchEx
    except ImportError as exc:
        raise ExcelCOMUnavailable("pywin32 COM library unavailable") from exc
    return DispatchEx


def _checkpoint_parts(checkpoint_id: str) -> tuple[str, str]:
    if checkpoint_id.count("!") != 1:
        raise ValueError(f"checkpoint must use Sheet!A1 form: {checkpoint_id}")
    sheet, cell = checkpoint_id.split("!", 1)
    sheet = sheet.strip()
    if len(sheet) >= 2 and sheet[0] == "'" and sheet[-1] == "'":
        sheet = sheet[1:-1].replace("''", "'")
    if not sheet or not cell.strip():
        raise ValueError(f"checkpoint must use Sheet!A1 form: {checkpoint_id}")
    return sheet, cell.strip()


def _excel_value_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    return str(value)


class WindowsExcelCOMRunner:
    def __init__(
        self,
        *,
        dispatch_factory: Callable[[str], Any] | None = None,
        calculation_timeout_seconds: float = 120.0,
        poll_interval_seconds: float = 0.05,
    ) -> None:
        if calculation_timeout_seconds <= 0 or poll_interval_seconds <= 0:
            raise ValueError("calculation timing values must be positive")
        self._dispatch_factory = dispatch_factory
        self._timeout = calculation_timeout_seconds
        self._poll = poll_interval_seconds

    def _dispatch(self) -> Any:
        if platform.system() != "Windows" and self._dispatch_factory is None:
            raise ExcelCOMUnavailable("Microsoft Excel COM requires Windows")
        factory = self._dispatch_factory or _load_dispatch()
        return factory("Excel.Application")

    def probe(self) -> ExcelRunnerProbe:
        if platform.system() != "Windows" and self._dispatch_factory is None:
            return ExcelRunnerProbe(
                available=False,
                runner_id=RUNNER_ID,
                runner_version=RUNNER_VERSION,
                reason_code="UNSUPPORTED_PLATFORM",
                reason="Microsoft Excel Desktop COM qualification requires Windows",
            )
        app = None
        try:
            app = self._dispatch()
            version = str(app.Version)
            return ExcelRunnerProbe(
                available=True,
                runner_id=RUNNER_ID,
                runner_version=RUNNER_VERSION,
                reason_code="EXCEL_AVAILABLE",
                reason="Microsoft Excel Desktop COM automation is available",
                excel_version=version,
            )
        except Exception as exc:
            return ExcelRunnerProbe(
                available=False,
                runner_id=RUNNER_ID,
                runner_version=RUNNER_VERSION,
                reason_code="EXCEL_APPLICATION_UNAVAILABLE",
                reason=f"Microsoft Excel Desktop COM unavailable: {type(exc).__name__}",
            )
        finally:
            if app is not None:
                try:
                    app.Quit()
                except Exception:
                    pass

    def run(
        self,
        workbook_path: str,
        checkpoint_ids: tuple[str, ...],
    ) -> ExcelExecutionEvidence:
        path = Path(workbook_path).resolve()
        if not path.is_file():
            raise FileNotFoundError(path)

        app = self._dispatch()
        workbook = None
        try:
            app.Visible = False
            app.DisplayAlerts = False
            if hasattr(app, "AskToUpdateLinks"):
                app.AskToUpdateLinks = False
            excel_version = str(app.Version)
            workbook = app.Workbooks.Open(
                str(path),
                UpdateLinks=0,
                ReadOnly=True,
                IgnoreReadOnlyRecommended=True,
            )
            app.CalculateFullRebuild()
            deadline = time.monotonic() + self._timeout
            while int(getattr(app, "CalculationState", 0)) != 0:
                if time.monotonic() >= deadline:
                    raise TimeoutError("Excel full recalculation did not reach xlDone")
                time.sleep(self._poll)

            values = []
            for checkpoint_id in checkpoint_ids:
                sheet_name, cell = _checkpoint_parts(checkpoint_id)
                raw = workbook.Worksheets(sheet_name).Range(cell).Value2
                values.append(
                    ExcelCheckpointValue(
                        checkpoint_id=checkpoint_id,
                        value=_excel_value_text(raw),
                    )
                )
            return ExcelExecutionEvidence(
                runner_id=RUNNER_ID,
                runner_version=RUNNER_VERSION,
                excel_version=excel_version,
                workbook_sha256=_sha256(path),
                actual_excel_evidence=True,
                full_recalculation_performed=True,
                opened_without_link_updates=True,
                checkpoint_values=tuple(values),
            )
        finally:
            if workbook is not None:
                try:
                    workbook.Close(SaveChanges=False)
                except Exception:
                    pass
            try:
                app.Quit()
            except Exception:
                pass

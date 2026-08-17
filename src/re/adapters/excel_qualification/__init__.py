"""Windows Excel qualification adapter package."""

from .com_runner import ExcelCOMUnavailable, WindowsExcelCOMRunner

__all__ = ["ExcelCOMUnavailable", "WindowsExcelCOMRunner"]

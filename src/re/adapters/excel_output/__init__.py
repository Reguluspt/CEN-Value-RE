"""Supported-profile workbook output adapter package."""

from .n08_0038 import N08_0038_OUTPUT_PROFILE
from .openpyxl_writer import (
    OpenPyxlWorkbookOutputWriter,
    UnsupportedWorkbookOutputProfileError,
    WorkbookOutputError,
    WorkbookSourceHashMismatchError,
    WorkbookStructuralRegressionError,
    WorkbookWriteContractError,
)
from .profile import (
    WorkbookCompatibilityBinding,
    WorkbookFixedSourceBinding,
    WorkbookOutputConsumer,
    WorkbookOutputProfile,
    WorkbookValueKind,
    WorkbookWriteBinding,
)

SUPPORTED_WORKBOOK_OUTPUT_PROFILES = (N08_0038_OUTPUT_PROFILE,)

__all__ = [
    "N08_0038_OUTPUT_PROFILE",
    "OpenPyxlWorkbookOutputWriter",
    "SUPPORTED_WORKBOOK_OUTPUT_PROFILES",
    "UnsupportedWorkbookOutputProfileError",
    "WorkbookCompatibilityBinding",
    "WorkbookFixedSourceBinding",
    "WorkbookOutputConsumer",
    "WorkbookOutputError",
    "WorkbookOutputProfile",
    "WorkbookSourceHashMismatchError",
    "WorkbookStructuralRegressionError",
    "WorkbookValueKind",
    "WorkbookWriteBinding",
    "WorkbookWriteContractError",
]

"""Declarative write/output contract layered on a frozen ExcelTemplateProfile."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ..excel.profile import ExcelTemplateProfile


class WorkbookValueKind(str, Enum):
    TEXT = "TEXT"
    DECIMAL = "DECIMAL"
    FRACTION = "FRACTION"


@dataclass(frozen=True, slots=True)
class WorkbookWriteBinding:
    cell: str
    source_key: str
    value_kind: WorkbookValueKind
    required: bool = True

    def __post_init__(self) -> None:
        if "!" not in self.cell or not self.cell.strip():
            raise ValueError("write binding cell must use Sheet!A1 form")
        if not self.source_key.strip():
            raise ValueError("write binding source_key must not be blank")


@dataclass(frozen=True, slots=True)
class WorkbookCompatibilityBinding:
    transformation_id: str
    cell: str
    source_key: str
    value_kind: WorkbookValueKind
    required: bool = True

    def __post_init__(self) -> None:
        if not self.transformation_id.strip():
            raise ValueError("transformation_id must not be blank")
        if "!" not in self.cell or not self.cell.strip():
            raise ValueError("compatibility binding cell must use Sheet!A1 form")
        if not self.source_key.strip():
            raise ValueError("compatibility binding source_key must not be blank")


@dataclass(frozen=True, slots=True)
class WorkbookOutputConsumer:
    cell: str
    semantic_key: str
    expected_formula: str

    def __post_init__(self) -> None:
        if "!" not in self.cell or not self.cell.strip():
            raise ValueError("output consumer cell must use Sheet!A1 form")
        if not self.semantic_key.strip():
            raise ValueError("output consumer semantic_key must not be blank")
        if not self.expected_formula.strip():
            raise ValueError("output consumer formula must not be blank")


@dataclass(frozen=True, slots=True)
class WorkbookOutputProfile:
    template_profile: ExcelTemplateProfile
    source_exemplar_sha256: str
    write_bindings: tuple[WorkbookWriteBinding, ...]
    compatibility_bindings: tuple[WorkbookCompatibilityBinding, ...] = ()
    output_consumers: tuple[WorkbookOutputConsumer, ...] = ()

    def __post_init__(self) -> None:
        if len(self.source_exemplar_sha256) != 64 or any(
            ch not in "0123456789abcdef" for ch in self.source_exemplar_sha256
        ):
            raise ValueError("source_exemplar_sha256 must be lowercase SHA-256 hex")

        write_cells = [item.cell for item in self.write_bindings]
        compat_cells = [item.cell for item in self.compatibility_bindings]
        all_cells = write_cells + compat_cells
        if len(all_cells) != len(set(all_cells)):
            raise ValueError("workbook output writable cells must be unique")

        formula_cells = {item.cell for item in self.template_profile.formula_signatures}
        overlap = sorted(set(all_cells) & formula_cells)
        if overlap:
            raise ValueError(
                "workbook output bindings may not target protected formula signatures: "
                + ", ".join(overlap)
            )

        transformations = {
            item.transformation_id: item
            for item in self.template_profile.compatibility_transformations
        }
        for binding in self.compatibility_bindings:
            transformation = transformations.get(binding.transformation_id)
            if transformation is None:
                raise ValueError(
                    f"undeclared compatibility transformation {binding.transformation_id}"
                )
            if binding.cell not in transformation.affected_cells:
                raise ValueError(
                    f"{binding.cell} is not declared by transformation {binding.transformation_id}"
                )

        consumer_cells = [item.cell for item in self.output_consumers]
        if len(consumer_cells) != len(set(consumer_cells)):
            raise ValueError("output consumer cells must be unique")

    @property
    def profile_id(self) -> str:
        return self.template_profile.profile_id

    @property
    def profile_version(self) -> str:
        return self.template_profile.profile_version

    @property
    def allowed_write_cells(self) -> frozenset[str]:
        return frozenset(
            [item.cell for item in self.write_bindings]
            + [item.cell for item in self.compatibility_bindings]
        )

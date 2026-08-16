"""Deterministic Golden Fixture loader/comparator; no valuation or Excel runtime."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP, localcontext
from enum import Enum
from hashlib import sha256
import json
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from src.re.domain.common.numeric import to_decimal


class GoldenFixtureFormatError(ValueError):
    pass


class ComparisonKind(str, Enum):
    EXACT_DECIMAL = "EXACT_DECIMAL"
    EXACT_INTEGER = "EXACT_INTEGER"
    DECIMAL_SCALE = "DECIMAL_SCALE"
    ABSOLUTE_TOLERANCE = "ABSOLUTE_TOLERANCE"
    EXACT_TEXT = "EXACT_TEXT"


@dataclass(frozen=True, slots=True)
class ComparisonPolicy:
    kind: ComparisonKind
    scale: int | None = None
    tolerance: Decimal | None = None
    rounding_increment: Decimal | None = None

    def __post_init__(self) -> None:
        if self.kind is ComparisonKind.DECIMAL_SCALE:
            if self.scale is None or self.scale < 0:
                raise GoldenFixtureFormatError("DECIMAL_SCALE requires non-negative scale")
        elif self.scale is not None:
            raise GoldenFixtureFormatError("scale only valid for DECIMAL_SCALE")
        if self.kind is ComparisonKind.ABSOLUTE_TOLERANCE:
            if self.tolerance is None or self.tolerance < 0:
                raise GoldenFixtureFormatError("ABSOLUTE_TOLERANCE requires non-negative tolerance")
        elif self.tolerance is not None:
            raise GoldenFixtureFormatError("tolerance only valid for ABSOLUTE_TOLERANCE")
        inc = self.rounding_increment
        if inc is not None and (inc <= 0 or inc != inc.to_integral_value()):
            raise GoldenFixtureFormatError("rounding_increment must be positive whole base-unit amount")


@dataclass(frozen=True, slots=True)
class CheckpointSpec:
    checkpoint_id: str
    label: str
    expected: Decimal | str
    policy: ComparisonPolicy
    unit: str
    fixture_pointer: str | None = None


@dataclass(frozen=True, slots=True)
class GoldenFixtureSnapshot:
    fixture_id: str
    status: str
    semantic_sha256: str
    payload: Mapping[str, Any]
    source_path: str

    @property
    def partial_input_coverage(self) -> bool:
        return "PARTIAL INPUT COVERAGE" in self.status


@dataclass(frozen=True, slots=True)
class CheckpointManifest:
    manifest_id: str
    version: int
    fixture_id: str
    status: str
    source_contract: str
    tolerance_contract: str
    semantic_sha256: str
    checkpoint_set_sha256: str
    checkpoints: tuple[CheckpointSpec, ...]
    source_path: str

    @property
    def checkpoint_ids(self) -> tuple[str, ...]:
        return tuple(x.checkpoint_id for x in self.checkpoints)


@dataclass(frozen=True, slots=True)
class GoldenFixtureBundle:
    fixture: GoldenFixtureSnapshot
    manifest: CheckpointManifest


@dataclass(frozen=True, slots=True)
class CheckpointOutcome:
    checkpoint_id: str
    passed: bool
    expected: Decimal | str
    actual: Decimal | str | None
    reason: str
    difference: Decimal | None = None


@dataclass(frozen=True, slots=True)
class CheckpointReport:
    manifest_id: str
    manifest_version: int
    checkpoint_set_sha256: str
    passed: bool
    outcomes: tuple[CheckpointOutcome, ...]
    missing_checkpoint_ids: tuple[str, ...]
    unexpected_checkpoint_ids: tuple[str, ...]

    @property
    def passed_count(self) -> int:
        return sum(x.passed for x in self.outcomes)

    @property
    def failed_count(self) -> int:
        return len(self.outcomes) - self.passed_count


def _reject_float(token: str) -> None:
    raise GoldenFixtureFormatError(f"binary-float JSON token forbidden: {token}")


def _reject_constant(token: str) -> None:
    raise GoldenFixtureFormatError(f"non-finite JSON token forbidden: {token}")


def _read_json(path: str | Path) -> tuple[dict[str, Any], str]:
    p = Path(path)
    try:
        raw = json.loads(
            p.read_text(encoding="utf-8"),
            parse_float=_reject_float,
            parse_constant=_reject_constant,
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise GoldenFixtureFormatError(f"invalid golden JSON: {p}") from exc
    if not isinstance(raw, dict):
        raise GoldenFixtureFormatError("golden JSON root must be object")
    return raw, str(p)


def _digest(value: Any) -> str:
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return sha256(data.encode("utf-8")).hexdigest()


def _freeze(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({k: _freeze(v) for k, v in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(v) for v in value)
    if isinstance(value, float):
        raise GoldenFixtureFormatError("binary float escaped parser")
    return value


def _text(data: Mapping[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise GoldenFixtureFormatError(f"{key} must be non-empty string")
    return value


def _decimal(value: Any, field: str) -> Decimal:
    try:
        return to_decimal(value, field_name=field)
    except (TypeError, ValueError) as exc:
        raise GoldenFixtureFormatError(str(exc)) from exc


def load_golden_fixture(path: str | Path) -> GoldenFixtureSnapshot:
    raw, source = _read_json(path)
    if not isinstance(raw.get("expected"), dict):
        raise GoldenFixtureFormatError("fixture expected must be object")
    return GoldenFixtureSnapshot(_text(raw, "fixture_id"), _text(raw, "status"), _digest(raw), _freeze(raw), source)


def _policy(raw: Any, cid: str) -> ComparisonPolicy:
    if not isinstance(raw, dict):
        raise GoldenFixtureFormatError(f"{cid}: comparison must be object")
    try:
        kind = ComparisonKind(raw.get("kind"))
    except ValueError as exc:
        raise GoldenFixtureFormatError(f"{cid}: invalid comparison kind") from exc
    scale = raw.get("scale")
    if scale is not None and (isinstance(scale, bool) or not isinstance(scale, int)):
        raise GoldenFixtureFormatError(f"{cid}: scale must be integer")
    return ComparisonPolicy(
        kind,
        scale,
        None if raw.get("tolerance") is None else _decimal(raw["tolerance"], f"{cid}.tolerance"),
        None if raw.get("rounding_increment") is None else _decimal(raw["rounding_increment"], f"{cid}.rounding_increment"),
    )


def _expected(value: Any, policy: ComparisonPolicy, cid: str) -> Decimal | str:
    if policy.kind is ComparisonKind.EXACT_TEXT:
        if not isinstance(value, str):
            raise GoldenFixtureFormatError(f"{cid}: text expected required")
        return value
    result = _decimal(value, f"{cid}.expected")
    if policy.kind is ComparisonKind.EXACT_INTEGER and result != result.to_integral_value():
        raise GoldenFixtureFormatError(f"{cid}: expected integer not integral")
    return result


def _set_payload(items: list[CheckpointSpec]) -> list[dict[str, Any]]:
    out = []
    for x in items:
        comparison: dict[str, Any] = {"kind": x.policy.kind.value}
        if x.policy.scale is not None: comparison["scale"] = x.policy.scale
        if x.policy.tolerance is not None: comparison["tolerance"] = str(x.policy.tolerance)
        if x.policy.rounding_increment is not None: comparison["rounding_increment"] = str(x.policy.rounding_increment)
        out.append({"checkpoint_id": x.checkpoint_id, "label": x.label, "expected": str(x.expected), "unit": x.unit, "fixture_pointer": x.fixture_pointer, "comparison": comparison})
    return out


def load_checkpoint_manifest(path: str | Path) -> CheckpointManifest:
    raw, source = _read_json(path)
    version = raw.get("version")
    if isinstance(version, bool) or not isinstance(version, int) or version < 1:
        raise GoldenFixtureFormatError("version must be positive integer")
    rows = raw.get("checkpoints")
    if not isinstance(rows, list) or not rows:
        raise GoldenFixtureFormatError("checkpoints must be non-empty list")
    seen: set[str] = set(); items: list[CheckpointSpec] = []
    for row in rows:
        if not isinstance(row, dict): raise GoldenFixtureFormatError("checkpoint must be object")
        cid = _text(row, "checkpoint_id")
        if cid in seen: raise GoldenFixtureFormatError(f"duplicate checkpoint_id: {cid}")
        seen.add(cid); pol = _policy(row.get("comparison"), cid)
        pointer = row.get("fixture_pointer")
        if pointer is not None and (not isinstance(pointer, str) or not pointer.startswith("/")):
            raise GoldenFixtureFormatError(f"{cid}: invalid fixture pointer")
        items.append(CheckpointSpec(cid, _text(row, "label"), _expected(row.get("expected"), pol, cid), pol, _text(row, "unit"), pointer))
    if raw.get("checkpoint_count") != len(items):
        raise GoldenFixtureFormatError("checkpoint_count mismatch")
    return CheckpointManifest(
        _text(raw, "manifest_id"), version, _text(raw, "fixture_id"), _text(raw, "status"),
        _text(raw, "source_contract"), _text(raw, "tolerance_contract"), _digest(raw),
        _digest(_set_payload(items)), tuple(items), source,
    )


def resolve_json_pointer(payload: Any, pointer: str) -> Any:
    if pointer == "": return payload
    if not pointer.startswith("/"): raise GoldenFixtureFormatError("invalid JSON pointer")
    current = payload
    for encoded in pointer.split("/")[1:]:
        token = encoded.replace("~1", "/").replace("~0", "~")
        if isinstance(current, Mapping) and token in current:
            current = current[token]
        elif isinstance(current, tuple):
            try: current = current[int(token)]
            except (ValueError, IndexError) as exc: raise GoldenFixtureFormatError(f"pointer not found: {pointer}") from exc
        else: raise GoldenFixtureFormatError(f"pointer not found: {pointer}")
    return current


def _prec(*values: Decimal) -> int:
    return max(50, *(len(v.as_tuple().digits) + abs(v.adjusted()) + 20 for v in values))


def _diff(left: Decimal, right: Decimal) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = _prec(left, right); return left - right


def compare_checkpoint(spec: CheckpointSpec, actual: Any) -> CheckpointOutcome:
    if spec.policy.kind is ComparisonKind.EXACT_TEXT:
        ok = isinstance(actual, str) and actual == spec.expected
        return CheckpointOutcome(spec.checkpoint_id, ok, spec.expected, actual if isinstance(actual, str) else None, "exact text match" if ok else "text mismatch")
    try: got = _decimal(actual, f"{spec.checkpoint_id}.actual")
    except GoldenFixtureFormatError as exc: return CheckpointOutcome(spec.checkpoint_id, False, spec.expected, None, str(exc))
    expected = spec.expected; assert isinstance(expected, Decimal); kind = spec.policy.kind
    if kind is ComparisonKind.EXACT_INTEGER:
        ok = got == got.to_integral_value() and got == expected; reason = "exact integer match" if ok else "integer mismatch"
    elif kind is ComparisonKind.EXACT_DECIMAL:
        ok = got == expected; reason = "exact decimal match" if ok else "decimal mismatch"
    elif kind is ComparisonKind.DECIMAL_SCALE:
        assert spec.policy.scale is not None; q = Decimal(1).scaleb(-spec.policy.scale)
        with localcontext() as ctx:
            ctx.prec = _prec(got, expected, q); ok = got.quantize(q, rounding=ROUND_HALF_UP) == expected.quantize(q, rounding=ROUND_HALF_UP)
        reason = f"equal at scale {spec.policy.scale}" if ok else f"mismatch at scale {spec.policy.scale}"
    elif kind is ComparisonKind.ABSOLUTE_TOLERANCE:
        assert spec.policy.tolerance is not None; delta = abs(_diff(got, expected)); ok = delta <= spec.policy.tolerance
        reason = "within tolerance" if ok else "exceeds tolerance"
    else: raise AssertionError(kind)
    return CheckpointOutcome(spec.checkpoint_id, ok, expected, got, reason, _diff(got, expected))


def load_golden_bundle(fixture_path: str | Path, manifest_path: str | Path) -> GoldenFixtureBundle:
    fixture = load_golden_fixture(fixture_path); manifest = load_checkpoint_manifest(manifest_path)
    if fixture.fixture_id != manifest.fixture_id: raise GoldenFixtureFormatError("fixture_id mismatch")
    bundle = GoldenFixtureBundle(fixture, manifest)
    for spec in manifest.checkpoints:
        if spec.fixture_pointer is None: continue
        raw = resolve_json_pointer(fixture.payload, spec.fixture_pointer)
        ok = raw == spec.expected if isinstance(spec.expected, str) else _decimal(raw, spec.checkpoint_id) == spec.expected
        if not ok: raise GoldenFixtureFormatError(f"fixture binding mismatch for {spec.checkpoint_id}")
    return bundle


def evaluate_checkpoint_results(manifest: CheckpointManifest, actual_results: Mapping[str, Any], *, strict_checkpoint_set: bool = True) -> CheckpointReport:
    expected_ids = set(manifest.checkpoint_ids); actual_ids = set(actual_results)
    missing = tuple(sorted(expected_ids - actual_ids)); unexpected = tuple(sorted(actual_ids - expected_ids)); outcomes = []
    for spec in manifest.checkpoints:
        outcomes.append(compare_checkpoint(spec, actual_results[spec.checkpoint_id]) if spec.checkpoint_id in actual_results else CheckpointOutcome(spec.checkpoint_id, False, spec.expected, None, "missing checkpoint result"))
    passed = not missing and all(x.passed for x in outcomes) and (not strict_checkpoint_set or not unexpected)
    return CheckpointReport(manifest.manifest_id, manifest.version, manifest.checkpoint_set_sha256, passed, tuple(outcomes), missing, unexpected)

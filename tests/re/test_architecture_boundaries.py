"""Architecture guardrails for the CenValue RE bounded context."""

from __future__ import annotations

import ast
from pathlib import Path

RE_ROOT = Path(__file__).resolve().parents[2] / "src" / "re"
DOMAIN_ROOT = RE_ROOT / "domain"
CORE_ROOTS = (DOMAIN_ROOT, RE_ROOT / "application", RE_ROOT / "ports")

DOMAIN_FORBIDDEN_PREFIXES = (
    "flask",
    "sqlalchemy",
    "openpyxl",
    "pydantic",
    "fastapi",
    "uvicorn",
    "google",
    "openai",
    "langchain",
    "playwright",
    "sqlite3",
    "aiosqlite",
    "api",
    "src.database_manager",
    "src.sqlite_store",
    "re.adapters",
)
CORE_FORBIDDEN_PREFIXES = (
    "re.adapters",
)


def _normalize_absolute_module(module: str) -> str:
    """Normalize repository-root imports to the canonical RE namespace."""
    if module == "src":
        return module
    if module.startswith("src."):
        return module[len("src.") :]
    return module


def _module_name_for_path(path: Path) -> str:
    relative = path.relative_to(RE_ROOT).with_suffix("")
    parts = ["re", *relative.parts]
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _package_for_path(path: Path) -> str:
    module = _module_name_for_path(path)
    if path.name == "__init__.py":
        return module
    return module.rpartition(".")[0]


def _resolve_from_base(current_package: str, node: ast.ImportFrom) -> str:
    if node.level == 0:
        return _normalize_absolute_module(node.module or "")

    package_parts = current_package.split(".") if current_package else []
    parents_to_trim = node.level - 1
    if parents_to_trim > len(package_parts):
        return ""

    base_parts = package_parts[: len(package_parts) - parents_to_trim]
    if node.module:
        base_parts.extend(node.module.split("."))
    return _normalize_absolute_module(".".join(base_parts))


def _imports_from_tree(tree: ast.AST, current_package: str) -> list[str]:
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.extend(_normalize_absolute_module(alias.name) for alias in node.names)
            continue
        if not isinstance(node, ast.ImportFrom):
            continue

        base = _resolve_from_base(current_package, node)
        if base:
            found.append(base)

        # Capture aliases too. This is required for forms such as
        # ``from src.re import adapters`` and ``from ... import adapters``.
        for alias in node.names:
            if alias.name == "*":
                continue
            target = f"{base}.{alias.name}" if base else alias.name
            found.append(_normalize_absolute_module(target))
    return found


def _imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return _imports_from_tree(tree, _package_for_path(path))


def _python_files(root: Path):
    return sorted(root.rglob("*.py"))


def _starts_with_any(module: str, prefixes: tuple[str, ...]) -> bool:
    return any(module == prefix or module.startswith(prefix + ".") for prefix in prefixes)


def test_domain_has_no_framework_or_adapter_dependencies() -> None:
    violations: list[str] = []
    for path in _python_files(DOMAIN_ROOT):
        for module in _imports(path):
            if _starts_with_any(module, DOMAIN_FORBIDDEN_PREFIXES):
                violations.append(f"{path.relative_to(RE_ROOT)} -> {module}")
    assert not violations, "Forbidden domain imports:\n" + "\n".join(violations)


def test_core_layers_do_not_import_adapters() -> None:
    violations: list[str] = []
    for root in CORE_ROOTS:
        for path in _python_files(root):
            for module in _imports(path):
                if _starts_with_any(module, CORE_FORBIDDEN_PREFIXES):
                    violations.append(f"{path.relative_to(RE_ROOT)} -> {module}")
    assert not violations, "Core-to-adapter imports:\n" + "\n".join(violations)


def test_adapter_import_spellings_are_canonicalized_and_blocked() -> None:
    cases = (
        ("import re.adapters", "re.domain.cases"),
        ("import src.re.adapters.persistence", "re.domain.cases"),
        ("from src.re.adapters import persistence", "re.domain.cases"),
        ("from src.re import adapters", "re.domain.cases"),
        ("from ...adapters import persistence", "re.domain.cases"),
        ("from ... import adapters", "re.domain.cases"),
    )
    for source, current_package in cases:
        modules = _imports_from_tree(ast.parse(source), current_package)
        assert any(
            _starts_with_any(module, CORE_FORBIDDEN_PREFIXES) for module in modules
        ), f"Adapter import escaped guard: {source!r} -> {modules!r}"


def test_non_adapter_core_import_is_not_false_positive() -> None:
    modules = _imports_from_tree(ast.parse("from src.re import domain"), "re.application")
    assert not any(_starts_with_any(module, CORE_FORBIDDEN_PREFIXES) for module in modules)


def test_expected_bounded_context_packages_exist() -> None:
    required = (
        "domain/cases",
        "domain/property",
        "domain/construction",
        "domain/adjustment",
        "domain/valuation",
        "domain/approval",
        "domain/common",
        "application/commands",
        "application/queries",
        "application/services",
        "ports",
        "adapters/persistence",
        "adapters/excel",
        "adapters/providers",
    )
    missing = [name for name in required if not (RE_ROOT / name).is_dir()]
    assert not missing, f"Missing RE packages: {missing}"

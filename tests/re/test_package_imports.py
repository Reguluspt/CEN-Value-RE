"""Smoke tests for the additive RE package skeleton."""

from src import re as re_context
from src.re import application, domain, ports


def test_re_core_packages_import_without_infrastructure() -> None:
    assert re_context is not None
    assert domain is not None
    assert application is not None
    assert ports is not None

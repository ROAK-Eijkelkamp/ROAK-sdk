from __future__ import annotations

import os
from unittest.mock import MagicMock

import pytest

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dev dependency
    load_dotenv = None


class StubRegistry:
    """Minimal registry test double compatible with semantic constructors."""

    def __init__(self, mapping: dict[type, object] | None = None) -> None:
        self._mapping = mapping or {}
        self.headers = {"Authorization": "Bearer test"}
        self.base_url = "https://example.test"

    def get(self, client_class: type):
        if client_class not in self._mapping:
            self._mapping[client_class] = MagicMock(name=f"{client_class.__name__}Mock")
        return self._mapping[client_class]


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="Run integration tests that require live ROAK credentials.",
    )


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "integration: marks tests that require a live ROAK environment",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if config.getoption("--run-integration"):
        return

    skip_integration = pytest.mark.skip(
        reason="integration tests are disabled by default; pass --run-integration to enable",
    )
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)


@pytest.fixture(scope="session")
def integration_env() -> dict[str, str]:
    if load_dotenv is not None:
        load_dotenv()

    username = os.getenv("ROAK_USERNAME")
    password = os.getenv("ROAK_PASSWORD")

    if not username or not password:
        pytest.skip("ROAK_USERNAME and ROAK_PASSWORD must be set for integration tests")

    return {
        "username": username,
        "password": password,
        "base_url": os.getenv("ROAK_BASE_URL", "https://dev.roak.com"),
        "multi_base_url": os.getenv("ROAK_MULTI_BASE_URL", "https://dev.roak.com"),
    }

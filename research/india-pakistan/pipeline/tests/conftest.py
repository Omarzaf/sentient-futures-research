"""The public suite is offline; unexpected socket creation is a test failure."""

import socket

import pytest


@pytest.fixture(autouse=True)
def prevent_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep historical acquisition imports from silently making external calls."""

    def reject(*args: object, **kwargs: object) -> None:
        """Fail any actual networking during the public suite."""
        raise AssertionError("Public tests must remain offline")

    monkeypatch.setattr(socket, "socket", reject)

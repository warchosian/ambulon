"""Unit tests for ``app.cli.registry`` and ``app.cli.dispatch``.

These protect the new registry-based CLI dispatcher introduced in 4.1.0 so
regressions (e.g. renaming a module or removing a ``main``) are caught at
build time, not at user runtime.
"""

from __future__ import annotations

import importlib
import sys
from typing import Dict, Tuple

import pytest

from app.cli.dispatch import dispatch_standard
from app.cli.registry import STANDARD_COMMANDS


class TestRegistryShape:
    def test_registry_is_non_empty(self):
        assert len(STANDARD_COMMANDS) > 0

    def test_every_entry_is_a_pair_of_strings(self):
        for cmd, entry in STANDARD_COMMANDS.items():
            assert isinstance(cmd, str) and cmd, f"bad cmd key: {cmd!r}"
            assert isinstance(entry, tuple) and len(entry) == 2, (
                f"{cmd} entry should be (module_path, attr), got {entry!r}"
            )
            mod_path, attr = entry
            assert isinstance(mod_path, str) and mod_path.startswith("app."), (
                f"{cmd} -> {mod_path!r}: module path must start with 'app.'"
            )
            assert isinstance(attr, str) and attr, (
                f"{cmd} -> {attr!r}: handler name must be a non-empty string"
            )

    def test_no_duplicate_targets(self):
        """Two registry keys pointing at the same handler likely means alias/typo."""
        seen: Dict[Tuple[str, str], str] = {}
        duplicates = []
        for cmd, entry in STANDARD_COMMANDS.items():
            if entry in seen:
                duplicates.append(f"{cmd} and {seen[entry]} both target {entry}")
            else:
                seen[entry] = cmd
        assert not duplicates, "\n".join(duplicates)


@pytest.mark.parametrize("cmd", sorted(STANDARD_COMMANDS.keys()))
def test_every_registered_handler_is_importable(cmd):
    """Each (module_path, attr) must resolve to a callable."""
    mod_path, attr = STANDARD_COMMANDS[cmd]
    module = importlib.import_module(mod_path)
    handler = getattr(module, attr, None)
    assert handler is not None, f"{mod_path}.{attr} does not exist"
    assert callable(handler), f"{mod_path}.{attr} is not callable"


class TestDispatchStandard:
    def test_unknown_command_returns_none(self):
        assert dispatch_standard("definitely-not-a-command-xyz") is None

    def test_dispatch_rewrites_argv_and_calls_handler(self, monkeypatch):
        """dispatch_standard should hide the command token from the handler."""
        captured: Dict[str, object] = {}

        def fake_main():
            captured["argv"] = list(sys.argv)
            return 42

        fake_module = type(sys)("fake_mod")
        fake_module.main = fake_main  # type: ignore[attr-defined]
        monkeypatch.setitem(sys.modules, "app.cli._test_fake_module", fake_module)

        monkeypatch.setitem(
            STANDARD_COMMANDS, "fake-test-cmd", ("app.cli._test_fake_module", "main")
        )

        monkeypatch.setattr(sys, "argv", ["ambulon", "fake-test-cmd", "--flag", "x"])
        try:
            result = dispatch_standard("fake-test-cmd")
        finally:
            STANDARD_COMMANDS.pop("fake-test-cmd", None)

        assert result == 42
        # The handler must see argv without the 'fake-test-cmd' token.
        assert captured["argv"] == ["ambulon", "--flag", "x"]

    def test_dispatch_restores_argv_after_call(self, monkeypatch):
        fake_module = type(sys)("fake_mod2")
        fake_module.main = lambda: 0  # type: ignore[attr-defined]
        monkeypatch.setitem(sys.modules, "app.cli._test_fake_module2", fake_module)
        monkeypatch.setitem(
            STANDARD_COMMANDS, "fake-restore", ("app.cli._test_fake_module2", "main")
        )

        monkeypatch.setattr(sys, "argv", ["ambulon", "fake-restore", "a", "b"])
        original = list(sys.argv)
        try:
            dispatch_standard("fake-restore")
        finally:
            STANDARD_COMMANDS.pop("fake-restore", None)
        assert sys.argv == original

    def test_dispatch_restores_argv_even_if_handler_raises(self, monkeypatch):
        fake_module = type(sys)("fake_mod3")

        def boom():
            raise RuntimeError("kaboom")

        fake_module.main = boom  # type: ignore[attr-defined]
        monkeypatch.setitem(sys.modules, "app.cli._test_fake_module3", fake_module)
        monkeypatch.setitem(
            STANDARD_COMMANDS, "fake-raise", ("app.cli._test_fake_module3", "main")
        )

        monkeypatch.setattr(sys, "argv", ["ambulon", "fake-raise"])
        original = list(sys.argv)
        try:
            with pytest.raises(RuntimeError, match="kaboom"):
                dispatch_standard("fake-raise")
        finally:
            STANDARD_COMMANDS.pop("fake-raise", None)
        assert sys.argv == original

    def test_dispatch_normalises_non_int_return_to_zero(self, monkeypatch):
        """Handlers that forget to return int should be coerced to 0."""
        fake_module = type(sys)("fake_mod4")
        fake_module.main = lambda: None  # type: ignore[attr-defined]
        monkeypatch.setitem(sys.modules, "app.cli._test_fake_module4", fake_module)
        monkeypatch.setitem(
            STANDARD_COMMANDS, "fake-none", ("app.cli._test_fake_module4", "main")
        )

        monkeypatch.setattr(sys, "argv", ["ambulon", "fake-none"])
        try:
            assert dispatch_standard("fake-none") == 0
        finally:
            STANDARD_COMMANDS.pop("fake-none", None)

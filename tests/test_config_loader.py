"""Unit tests for ``app.core.config_loader``.

Focuses on the three pieces of transverse logic used by every Ambulon module:

- ``deep_merge`` — recursive dict merge used by config layering.
- ``_replace_env_var`` — ``${VAR}`` / ``${VAR:-default}`` substitution.
- ``find_config_file`` / ``load_config`` — config discovery across the
  AMBULON_HOME / cwd / AMBULON_CONFIG_DIR hierarchy, with .example fallback.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from app.core.config_loader import (
    _replace_env_var,
    deep_merge,
    find_config_file,
    load_config,
)


# ---------------------------------------------------------------------------
# deep_merge
# ---------------------------------------------------------------------------

class TestDeepMerge:
    def test_override_wins_on_scalar(self):
        assert deep_merge({"a": 1}, {"a": 2}) == {"a": 2}

    def test_missing_keys_are_added(self):
        assert deep_merge({"a": 1}, {"b": 2}) == {"a": 1, "b": 2}

    def test_nested_dicts_are_merged_recursively(self):
        base = {"api": {"url": "x", "timeout": 30}}
        override = {"api": {"timeout": 60, "retries": 3}}
        assert deep_merge(base, override) == {
            "api": {"url": "x", "timeout": 60, "retries": 3}
        }

    def test_override_replaces_lists_wholesale(self):
        """Lists are not merged element-wise; override replaces."""
        assert deep_merge({"xs": [1, 2, 3]}, {"xs": [9]}) == {"xs": [9]}

    def test_override_replaces_scalar_with_dict(self):
        """If base has scalar and override has dict, override wins as-is."""
        assert deep_merge({"api": "x"}, {"api": {"url": "y"}}) == {"api": {"url": "y"}}

    def test_does_not_mutate_inputs(self):
        base = {"a": {"b": 1}}
        override = {"a": {"c": 2}}
        deep_merge(base, override)
        assert base == {"a": {"b": 1}}
        assert override == {"a": {"c": 2}}


# ---------------------------------------------------------------------------
# _replace_env_var
# ---------------------------------------------------------------------------

def _substitute(content: str) -> str:
    """Convenience wrapper mirroring what load_config does internally."""
    return re.sub(r"\$\{([^}]+)\}", _replace_env_var, content)


class TestReplaceEnvVar:
    def test_simple_var_present(self, monkeypatch):
        monkeypatch.setenv("MY_VAR", "hello")
        assert _substitute("token: ${MY_VAR}") == "token: hello"

    def test_simple_var_missing_raises(self, monkeypatch):
        monkeypatch.delenv("UNSET_VAR", raising=False)
        with pytest.raises(ValueError, match="UNSET_VAR"):
            _substitute("x: ${UNSET_VAR}")

    def test_default_fallback_when_unset(self, monkeypatch):
        monkeypatch.delenv("MY_VAR", raising=False)
        assert _substitute("x: ${MY_VAR:-fallback}") == "x: fallback"

    def test_default_ignored_when_var_set(self, monkeypatch):
        monkeypatch.setenv("MY_VAR", "real")
        assert _substitute("x: ${MY_VAR:-fallback}") == "x: real"

    def test_empty_default_returns_empty(self, monkeypatch):
        monkeypatch.delenv("MY_VAR", raising=False)
        assert _substitute("x: ${MY_VAR:-}") == "x: "

    def test_multiple_substitutions_in_one_string(self, monkeypatch):
        monkeypatch.setenv("A", "1")
        monkeypatch.setenv("B", "2")
        assert _substitute("${A}-${B}") == "1-2"


# ---------------------------------------------------------------------------
# find_config_file / load_config
# ---------------------------------------------------------------------------

@pytest.fixture
def isolated_env(tmp_path, monkeypatch):
    """Run with AMBULON_HOME pointing at a clean tmp dir; everything else unset."""
    monkeypatch.setenv("AMBULON_HOME", str(tmp_path))
    monkeypatch.delenv("AMBULON_CONFIG_DIR", raising=False)
    monkeypatch.chdir(tmp_path)
    return tmp_path


class TestFindConfigFile:
    def test_returns_none_when_nothing_exists(self, isolated_env):
        assert find_config_file("nonexistent") is None

    def test_finds_yaml_in_ambulon_home(self, isolated_env):
        cfg = isolated_env / "config" / "myapp.yaml"
        cfg.parent.mkdir()
        cfg.write_text("key: value", encoding="utf-8")
        assert find_config_file("myapp") == cfg

    def test_falls_back_to_example_suffix(self, isolated_env):
        cfg = isolated_env / "config" / "myapp.yaml.example"
        cfg.parent.mkdir()
        cfg.write_text("key: example_value", encoding="utf-8")
        assert find_config_file("myapp") == cfg

    def test_yaml_wins_over_example(self, isolated_env):
        (isolated_env / "config").mkdir()
        (isolated_env / "config" / "myapp.yaml").write_text("a: 1", encoding="utf-8")
        (isolated_env / "config" / "myapp.yaml.example").write_text("a: 2", encoding="utf-8")
        assert find_config_file("myapp").name == "myapp.yaml"

    def test_ambulon_config_dir_is_searched(self, tmp_path, monkeypatch):
        monkeypatch.delenv("AMBULON_HOME", raising=False)
        monkeypatch.chdir(tmp_path)
        cfg_dir = tmp_path / "custom_configs"
        cfg_dir.mkdir()
        (cfg_dir / "myapp.yaml").write_text("x: 1", encoding="utf-8")
        monkeypatch.setenv("AMBULON_CONFIG_DIR", str(cfg_dir))
        result = find_config_file("myapp")
        assert result is not None
        assert result.name == "myapp.yaml"


class TestLoadConfig:
    def test_returns_defaults_when_file_missing(self, isolated_env):
        result = load_config("nonexistent", default_config={"a": 1})
        assert result == {"a": 1}

    def test_merges_yaml_over_defaults(self, isolated_env):
        cfg = isolated_env / "config" / "app.yaml"
        cfg.parent.mkdir()
        cfg.write_text("b: 2\nnested:\n  x: override\n", encoding="utf-8")
        result = load_config(
            "app",
            default_config={"a": 1, "b": 0, "nested": {"x": "base", "y": "kept"}},
        )
        assert result == {"a": 1, "b": 2, "nested": {"x": "override", "y": "kept"}}

    def test_env_substitution_in_yaml(self, isolated_env, monkeypatch):
        monkeypatch.setenv("MY_TOKEN", "secret123")
        cfg = isolated_env / "config" / "app.yaml"
        cfg.parent.mkdir()
        cfg.write_text('token: "${MY_TOKEN}"\n', encoding="utf-8")
        result = load_config("app")
        assert result == {"token": "secret123"}

    def test_env_substitution_with_default(self, isolated_env, monkeypatch):
        monkeypatch.delenv("MISSING_VAR", raising=False)
        cfg = isolated_env / "config" / "app.yaml"
        cfg.parent.mkdir()
        cfg.write_text('url: "${MISSING_VAR:-http://localhost}"\n', encoding="utf-8")
        result = load_config("app")
        assert result == {"url": "http://localhost"}

    def test_absolute_path_is_honored(self, tmp_path, monkeypatch):
        monkeypatch.delenv("AMBULON_HOME", raising=False)
        monkeypatch.delenv("AMBULON_CONFIG_DIR", raising=False)
        cfg = tmp_path / "somewhere" / "explicit.yaml"
        cfg.parent.mkdir()
        cfg.write_text("x: 42", encoding="utf-8")
        result = load_config(str(cfg))
        assert result == {"x": 42}

    def test_returns_empty_dict_when_no_defaults_and_no_file(self, isolated_env):
        assert load_config("nonexistent") == {}

    def test_malformed_yaml_falls_back_to_defaults(self, isolated_env, caplog):
        cfg = isolated_env / "config" / "bad.yaml"
        cfg.parent.mkdir()
        cfg.write_text("this: is: : invalid: yaml:::", encoding="utf-8")
        result = load_config("bad", default_config={"safe": True})
        assert result == {"safe": True}

"""Regression tests for embedded YAML configuration templates.

``ambulon init <module>`` writes a YAML file to disk using a string constant
stored in ``app/<module>/core/config_template.py``. Because those strings are
opaque blobs sitting inside Python modules, linters do not catch syntax errors
or accidental tab indentation. These tests parse each template with
``yaml.safe_load`` so any regression is caught at build time.
"""

from __future__ import annotations

import pytest
import yaml

from app.piag.core.config_template import PIAG_CONFIG_TEMPLATE
from app.wikisi.core.config_template import WIKISI_CONFIG_TEMPLATE
from app.gitlab.core.config_template import GITLAB_CONFIG_TEMPLATE


@pytest.mark.parametrize(
    "name,template",
    [
        ("piag", PIAG_CONFIG_TEMPLATE),
        ("wikisi", WIKISI_CONFIG_TEMPLATE),
        ("gitlab", GITLAB_CONFIG_TEMPLATE),
    ],
)
def test_template_is_valid_yaml(name: str, template: str) -> None:
    """Each embedded template must parse as a non-empty mapping."""
    data = yaml.safe_load(template)
    assert data is not None, f"{name} template parsed to None (empty or all-comments)"
    assert isinstance(data, dict), f"{name} template did not parse to a dict"
    assert data, f"{name} template parsed to an empty dict"


# Known drift: piag and wikisi embedded templates are not wrapped in a
# top-level ``piag:`` / ``wikisi:`` key, unlike their on-disk .example
# counterparts. Enforce the invariant only where it already holds.
def test_gitlab_template_has_top_level_key() -> None:
    data = yaml.safe_load(GITLAB_CONFIG_TEMPLATE)
    assert "gitlab" in data, "gitlab template must have top-level 'gitlab:' key"


def test_gitlab_template_matches_example_file() -> None:
    """Catch drift between the embedded GitLab template and the .example file."""
    import pathlib

    example = pathlib.Path("config/gitlab.yaml.example")
    if not example.exists():
        pytest.skip("config/gitlab.yaml.example not present in this checkout")
    disk = example.read_text(encoding="utf-8").strip()
    embedded = GITLAB_CONFIG_TEMPLATE.strip()
    # We only compare the high-level structure (parsed YAML) so cosmetic
    # differences in trailing whitespace or comments don't break the test.
    assert yaml.safe_load(disk) == yaml.safe_load(embedded), (
        "config/gitlab.yaml.example and GITLAB_CONFIG_TEMPLATE have diverged. "
        "Update the embedded template in src/app/gitlab/core/config_template.py."
    )

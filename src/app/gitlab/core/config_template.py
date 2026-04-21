"""Embedded GitLab configuration template for ``ambulon init gitlab``.

Kept in sync with ``config/gitlab.yaml.example`` at the project root. The
``tests/test_config_templates.py`` regression test ensures this string is
valid YAML, so typos are caught at build time rather than at runtime.
"""

GITLAB_CONFIG_TEMPLATE = """gitlab:
  token: "${GITLAB_PRIVATE_TOKEN:-YOUR_GITLAB_PRIVATE_ACCESS_TOKEN}" # GitLab Personal Access Token
  username: "${GITLAB_USERNAME:-oauth2}" # GitLab username (often 'oauth2' for PAT authentication)
  base_clone_dir: "${GITLAB_CLONE_DIR:-./gitlab_clones}" # Base directory where projects will be cloned
  automation:
    enabled: true
    output_mode: "shared" # separate|shared
    code_monofile:
      enabled: true
      output_dir: null # default: <repo>.rag next to the repo
      templates:
        - "{project}.code.md"
        - "{project}.code.html"
      pipeline: ["project2md"]
    wiki_monofile:
      enabled: true
      output_dir: null # default: <repo>.rag next to the repo
      templates:
        - "{project}.md"
        - "{project}.html"
      pipeline: ["flatten-md", "merge-md"]
  repositories:
    - "gitlab.example.com/group/project.git" # Git repository URL (with or without https://)
    # Add more repositories as needed:
"""

__all__ = ["GITLAB_CONFIG_TEMPLATE"]

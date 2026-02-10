"""Template de configuration GitLab embarqué dans le code."""

GITLAB_CONFIG_TEMPLATE = """# Configuration GitLab - Template
# Copiez ce fichier vers config/gitlab.yaml et ajustez les valeurs

gitlab:
  # Personal Access Token GitLab avec les permissions appropriées (read_repository, etc.)
  token: "YOUR_GITLAB_PRIVATE_ACCESS_TOKEN"

  # Nom d'utilisateur associé au token (souvent 'oauth2' ou votre username GitLab)
  username: "your-gitlab-username-for-pat"

  # Répertoire de base où les projets seront clonés
  base_clone_dir: "C:/Users/your_user/dev/gitlab_projects"

  # Liste des dépôts à cloner (chemins relatifs depuis le serveur GitLab)
  repositories:
    - "gitlab-forge.din.developpement-durable.gouv.fr/snum/pnm3/produits/support/admin-ep/admin_ep.git"
    - "another/group/another_project.git"  # Ajoutez d'autres projets au besoin

# Hiérarchie de configuration:
# 1. Arguments CLI (--token, --username, etc.)
# 2. Ce fichier YAML
# 3. Variables d'environnement (GITLAB_PRIVATE_TOKEN, GITLAB_USERNAME, etc.)
# 4. Valeurs par défaut
"""

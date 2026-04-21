# app.gitlab

Clonage de dépôts GitLab et génération de **monofiles** (`code.md`, `wiki.md`)
pour alimentation RAG, plus gestion des releases GitLab.

## Architecture

- **`core/cloning.py`** : clonage/mise à jour d'un dépôt Git avec authentification
  par PAT (`GITLAB_PRIVATE_TOKEN`).
- **`core/monofile.py`** : génération des monofiles (`project2md` pour le code,
  `flatten-md` + `merge-md` pour le wiki).
- **`core/monofile_load.py`** : pipeline complet (clone + monofile + post-traitement
  TOC/iTOC/augment).
- **`core/config_template.py`** : template embarqué pour `ambulon init gitlab`.
- **`commands/gitlab_clone.py`** : `ambulon gitlab-clone` — pipeline complet pour
  tous les dépôts configurés dans `config/gitlab.yaml`. Flags
  `--add-toc`, `--add-itoc`, `--augment`, `--generate-filtered`,
  `--generate-summarized`, `-E/--all-enhancements`.
- **`commands/gitlab_monofile.py`** : `ambulon gitlab-monofile` — régénère un
  monofile depuis un répertoire déjà cloné.
- **`releases/core/`** : gestion des releases GitLab (upload d'assets au
  Package Registry).
- **`releases/commands/gitlab_release.py`** : `ambulon gitlab-release`.

## Configuration

Voir `config/gitlab.yaml.example`. Variables d'environnement :

| Variable | Rôle |
| --- | --- |
| `GITLAB_PRIVATE_TOKEN` | Personal Access Token (obligatoire) |
| `GITLAB_USERNAME`      | Nom d'utilisateur (défaut : `oauth2` pour PAT) |
| `GITLAB_CLONE_DIR`     | Racine des clones (défaut : `./gitlab_clones`) |

## Exemples

```bash
# Clone + génération monofiles pour tous les dépôts config/gitlab.yaml
export GITLAB_PRIVATE_TOKEN="..."
ambulon gitlab-clone

# Avec post-traitement complet (TOC + iTOC + augment + filtered + summarized)
ambulon gitlab-clone -E

# Régénérer uniquement le monofile d'un dépôt déjà cloné
ambulon gitlab-monofile G:/repos/my-project

# Créer une release + uploader un asset
ambulon gitlab-release --project-id 123 --tag v1.0.0 --asset dist/pkg.zip
```

oui # GEMINI Project Guidelines

Ce projet utilise les outils suivants pour la gestion des modules Python et les commits conventionnels.

## Gestion des dépendances Python avec Poetry

[Poetry](https://python-poetry.org/) est utilisé pour la gestion des dépendances et le packaging. Pour commencer :

1.  **Installer Poetry**: Si vous n'avez pas Poetry, suivez le guide d'installation officiel.
2.  **Installer les dépendances**: Naviguez à la racine du projet et exécutez :
    ```bash
    poetry install
    ```
3.  **Vérification avant Build**: Avant de procéder à un `poetry build`, assurez-vous toujours que le fichier `pyproject.toml` contient toutes les dépendances nécessaires et qu'elles sont cohérentes.
4.  **Activer l'environnement virtuel**: Pour activer l'environnement virtuel du projet, exécutez :
    ```bash
    poetry shell
    ```

## Workflow de Versioning et de Release

Ce projet suit le **Semantic Versioning (SemVer)** et utilise [Commitizen](https://commitizen-tool.github.io/commitizen/) pour automatiser la gestion des versions et la génération du changelog.

### Semantic Versioning (SemVer)

Le numéro de version est structuré en `MAJEUR.MINEUR.PATCH` :
- **MAJEUR** : Incrémenté pour des changements d'API non rétrocompatibles (tout ce qui est marqué comme `BREAKING CHANGE`).
- **MINEUR** : Incrémenté pour de nouvelles fonctionnalités rétrocompatibles (un commit de type `feat`).
- **PATCH** : Incrémenté pour des corrections de bugs rétrocompatibles (un commit de type `fix`).

### Commits Conventionnels (Conventional Commits)

Les messages de commit doivent suivre la spécification [Conventional Commits](https://www.conventionalcommits.org/). C'est Commitizen qui s'en assure. Le type de commit détermine directement l'incrémentation de la version :

- `feat:` : Une nouvelle fonctionnalité pour l'utilisateur. **Résulte en une version MINEURE.**
- `fix:` : Une correction de bug pour l'utilisateur. **Résulte en une version PATCH.**
- `docs:` : Changements affectant uniquement la documentation.
- `style:` : Changements qui n'affectent pas le sens du code (espaces, formatage, etc.).
- `refactor:` : Une modification du code qui ne corrige ni un bug ni n'ajoute de fonctionnalité.
- `perf:` : Une modification du code qui améliore les performances.
- `test:` : Ajout de tests manquants ou correction de tests existants.
- `chore:` : Modifications du processus de build ou des outils auxiliaires.

Un `BREAKING CHANGE:` dans le pied de page du message de commit, ou un `!` après le type/scope (ex: `feat!: Mettre à jour l'API`), **résultera en une version MAJEURE**.

### Processus de Release

Le processus de création d'une nouvelle release est strict et doit suivre ces étapes dans l'ordre :

1.  **Effectuer les modifications** : Modifiez le code comme nécessaire.

2.  **Indexer et Commiter**: Indexez vos changements (`git add .`) et utilisez la commande `cz commit` pour créer un message de commit guidé et conventionnel.
    ```bash
    cz commit
    ```

3.  **Créer la nouvelle version**: Exécutez `cz bump`. Cette commande va automatiquement :
    - Déterminer le nouveau numéro de version (PATCH, MINOR, ou MAJOR) en se basant sur vos commits.
    - Mettre à jour la version dans `pyproject.toml` et `src/ambulon/__init__.py`.
    - Générer ou mettre à jour le `CHANGELOG.md`.
    - Créer un commit et un tag Git pour la nouvelle version.
    ```bash
    cz bump --changelog
    ```

4.  **Générer le build**: Une fois la version taguée, générez les fichiers de distribution.
    ```bash
    poetry build
    ```

5.  **Vérification Systématique du Build**: **Cette étape est obligatoire avant de pousser les changements.** Inspectez le contenu du fichier `.whl` pour garantir qu'il contient tous les fichiers attendus (modules Python, fichiers de configuration, etc.).
    ```bash
    # Remplacez x.y.z par la version que vous venez de créer
    python -m zipfile -l dist/ambulon-x.y.z-py3-none-any.whl
    ```
    Si des fichiers manquent, retournez à la section "Vérification de l'Intégrité du Build" pour ajuster la configuration `pyproject.toml`, puis recommencez le build.

6.  **Pousser les changements**: Si la vérification du build est réussie, poussez vos commits et tags vers le dépôt distant.
    ```bash
    git push --follow-tags
    ```

## Vérification de l'Intégrité du Build (`.whl`)

Pour éviter de distribuer des packages incomplets, il est crucial de s'assurer que tous les fichiers nécessaires (y compris les fichiers de configuration, les données, etc.) sont inclus dans le fichier Wheel (`.whl`) généré par `poetry build`.

### Inclusion des fichiers dans le build

La configuration de ce qui est inclus se trouve dans `pyproject.toml`, sous la section `[tool.poetry]`.

1.  **Packages Python**: La directive `packages` indique à Poetry où trouver les packages Python. La configuration actuelle `packages = [{include = "ambulon", from = "src"}]` inclut correctement tout le code source du répertoire `src/ambulon`.

2.  **Autres fichiers**: Pour inclure des fichiers non-Python (comme des `.json`, `.md`, etc.), utilisez la directive `include`. Elle accepte une liste de chemins ou de motifs (globs).

    Votre `pyproject.toml` contient déjà :
    ```toml
    include = ["config/mcp-config.json"]
    ```

    Si vous avez besoin d'inclure d'autres fichiers ou des répertoires entiers, vous pouvez l'étendre. Par exemple, pour inclure tous les fichiers `.json` du répertoire `config` :
    ```toml
    include = ["config/**/*.json"]
    ```

### Vérifier le contenu du fichier Wheel

Après avoir généré le build avec `poetry build`, vous pouvez inspecter son contenu pour vérifier que tout y est. Un fichier `.whl` est une archive zip.

Utilisez la commande suivante pour lister le contenu du fichier Wheel sans l'extraire :

```bash
# Assurez-vous d'activer l'environnement virtuel (poetry shell)
python -m zipfile -l dist/*.whl
```

Cette commande affichera la liste de tous les fichiers embarqués dans la distribution. Vérifiez méticuleusement cette liste pour confirmer la présence de tous vos fichiers de configuration, données, et assets nécessaires au bon fonctionnement de l'application.

Si un fichier manque, ajustez la directive `include` dans votre `pyproject.toml`, reconstruisez avec `poetry build`, et vérifiez à nouveau.

### Stratégie de Vérification des Dépendances de Modules

Pour garantir qu'aucun module ne manque de ses composants nécessaires (fichiers de configuration, données, assets), il est recommandé d'adopter une stratégie de vérification en plusieurs étapes :

1.  **Analyse Statique Manuelle**: Pour chaque module, le développeur doit identifier et lister tous les fichiers externes qu'il utilise. Par exemple, si `ambulon/ocr.py` charge un fichier de configuration ou des données d'entraînement, ces fichiers doivent être notés.

2.  **Configuration de l'Inclusion**: Assurez-vous que chaque fichier identifié à l'étape 1 est bien couvert par la directive `include` dans votre `pyproject.toml`. Utilisez des motifs glob (ex: `config/**/*.json`) pour inclure des groupes de fichiers de manière fiable.

3.  **Tests d'Intégration**: Créez des tests qui exercent spécifiquement les fonctionnalités qui dépendent de ces fichiers externes. L'exécution réussie de ces tests après une installation propre (`poetry install`) est la meilleure validation que les dépendances (code et fichiers) sont correctement gérées.

4.  **Vérification Post-Build**: Après chaque `poetry build`, utilisez la commande `python -m zipfile -l dist/*.whl` pour confirmer que les fichiers identifiés à l'étape 1 sont bien présents dans l'archive finale. C'est votre filet de sécurité final avant la distribution.

En combinant l'analyse du code, une configuration `pyproject.toml` explicite, des tests robustes et une inspection finale du livrable, vous réduirez considérablement le risque de distribuer un package incomplet.

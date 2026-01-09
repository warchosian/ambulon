# Configuration RAG PIAG

Ce dossier contient les fichiers de configuration pour l'intégration avec l'API RAG PIAG.

## Fichiers

### `piag_rag.yaml` ⚠️ (Non versionné)
Fichier de configuration principal avec les vraies valeurs (tokens, project IDs, etc.).
**Ce fichier est dans `.gitignore` et ne doit jamais être commité dans le dépôt.**

### `piag_rag.yaml.example`
Fichier template/exemple sans valeurs sensibles. Versionné dans Git.

## Installation

### Première utilisation

1. **Copiez le fichier d'exemple:**
   ```bash
   cp config/piag_rag.yaml.example config/piag_rag.yaml
   ```

2. **Éditez `config/piag_rag.yaml`** et remplissez les valeurs nécessaires:
   - `project.project_id`: Votre identifiant de projet PIAG
   - `security.token`: Votre token d'authentification (optionnel, voir ci-dessous)

3. **Alternative recommandée: Utiliser les variables d'environnement**
   Au lieu de stocker le token dans le fichier YAML, exportez-le comme variable d'environnement:
   ```bash
   export PIAG_RAG_API_TOKEN="votre-token-ici"
   ```

## Hiérarchie de priorité

La configuration suit cette hiérarchie (du plus prioritaire au moins prioritaire):

1. **Arguments CLI** - Passés directement en ligne de commande
2. **Fichier YAML** - Définis dans `config/piag_rag.yaml`
3. **Variables d'environnement** - Exportées dans votre shell
4. **Valeurs par défaut** - Définies dans le code

### Exemple:
```bash
# Le token passé en CLI écrase le YAML et les variables d'environnement
ambulon piag-collection-list --token "mon-token" --project-id "mon-projet"
```

## Configuration du Projet PNM3-GTI

Le fichier `piag_rag.yaml` est préconfiguré pour le projet **PNM3-GTI** avec:

- **Project ID**: `PnuQzUEmwRDkxZPX`
- **URL de base**: `https://preprod.api.piag.e2.rie.gouv.fr/rag/`
- **Environnement**: Préprod (indisponibilité possible)

## Sécurité

⚠️ **Bonnes pratiques de sécurité:**

1. **Ne jamais commiter de tokens** dans le dépôt Git
2. **Utiliser les variables d'environnement** plutôt que le fichier YAML pour les tokens
3. **Vérifier que `config/piag_rag.yaml` est bien dans `.gitignore`**
4. **Ne pas partager votre fichier `piag_rag.yaml`** avec d'autres personnes

## Commandes disponibles

### Collections
```bash
# Lister les collections
ambulon piag-collection-list --token $PIAG_RAG_API_TOKEN

# Créer une collection
ambulon piag-collection-add --name "Ma Collection" --description "Test" --token $PIAG_RAG_API_TOKEN

# Obtenir une collection
ambulon piag-collection-get --collection-id <id> --token $PIAG_RAG_API_TOKEN

# Mettre à jour une collection
ambulon piag-collection-update --collection-id <id> --name "Nouveau nom" --token $PIAG_RAG_API_TOKEN

# Supprimer une collection
ambulon piag-collection-rm --collection-id <id> --token $PIAG_RAG_API_TOKEN
```

### Documents
```bash
# Upload un document
ambulon piag-doc-upload --collection-id <id> --file document.pdf --token $PIAG_RAG_API_TOKEN

# Lister les documents
ambulon piag-doc-list --collection-id <id> --token $PIAG_RAG_API_TOKEN

# Obtenir un document
ambulon piag-doc-get --document-id <id> --token $PIAG_RAG_API_TOKEN

# Supprimer un document
ambulon piag-doc-rm --document-id <id> --token $PIAG_RAG_API_TOKEN

# Obtenir les chunks d'un document
ambulon piag-doc-chunks --document-id <id> --token $PIAG_RAG_API_TOKEN
```

### Recherche
```bash
# Recherche RAG sémantique
ambulon piag-search --collection-id <id> --query "Quelle est la procédure?" --token $PIAG_RAG_API_TOKEN
```

## Options communes

Toutes les commandes acceptent les options suivantes:

- `--token`: Token d'authentification (Bearer)
- `--base-url`: URL de base de l'API (par défaut: valeur du YAML)
- `--config`: Chemin vers un fichier de configuration personnalisé
- `--debug`: Active le mode debug avec logs détaillés

## Aide

Pour obtenir l'aide d'une commande spécifique:
```bash
ambulon piag-collection-list --help
```

## Support

Pour les questions ou problèmes:
- Consultez la documentation PIAG
- Vérifiez les exemples cURL fournis
- Contactez l'administrateur du projet PNM3-GTI

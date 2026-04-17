# ZIP Archive Module

Module de gestion d'archives ZIP avec chiffrement AES-256.

## 📦 Architecture

```
src/app/zip/
├── core/
│   └── zip_manager.py      # Gestion des archives (création, extraction, AES)
└── commands/
    ├── zip_create.py       # CLI: ambulon zip-create
    └── zip_extract.py      # CLI: ambulon zip-extract
```

## 🚀 Commandes CLI

### **`ambulon zip-create`** - Créer une archive ZIP

Crée une archive ZIP à partir de fichiers et répertoires avec support du chiffrement AES-256.

```bash
# Archive simple
ambulon zip-create docs/

# Avec nom personnalisé
ambulon zip-create docs/ -o documentation.zip

# Archive chiffrée (AES-256)
ambulon zip-create docs/ -p "secret123"

# Mot de passe depuis un fichier (plus sécurisé)
ambulon zip-create docs/ --password-file .password

# Archiver plusieurs sources
ambulon zip-create src/ tests/ README.md -o project.zip

# Exclure des fichiers
ambulon zip-create src/ --exclude "*.pyc" --exclude "__pycache__"

# Compression maximale
ambulon zip-create docs/ --compression 9

# Non récursif (uniquement fichiers directs)
ambulon zip-create docs/ --no-recursive

# Verbeux
ambulon zip-create docs/ -v
```

**Options :**
- `sources` : Fichier(s) ou répertoire(s) à archiver (obligatoire, répétable)
- `-o, --output FILE` : Fichier ZIP de sortie (défaut: `<premier_source>.zip`)
- `-p, --password PASS` : Mot de passe pour chiffrement AES-256
- `--password-file FILE` : Lire le mot de passe depuis un fichier
- `--exclude PATTERN` : Pattern glob à exclure (répétable, ex: `*.pyc`)
- `--compression LEVEL` : Niveau de compression 0-9 (défaut: 6)
  - `0` : Aucune compression (stockage)
  - `6` : Compression standard (défaut)
  - `9` : Compression maximale (plus lent)
- `--no-recursive` : Ne pas inclure les sous-répertoires récursivement
- `-v, --verbose` : Mode verbeux

---

### **`ambulon zip-extract`** - Extraire une archive ZIP

Extrait une archive ZIP avec support du déchiffrement AES-256.

```bash
# Extraction simple (répertoire courant)
ambulon zip-extract archive.zip

# Extraction vers un répertoire spécifique
ambulon zip-extract archive.zip -o extracted/

# Archive chiffrée
ambulon zip-extract secure.zip -p "secret123"

# Mot de passe depuis un fichier
ambulon zip-extract secure.zip --password-file .password

# Lister le contenu sans extraire
ambulon zip-extract archive.zip --list

# Liste détaillée
ambulon zip-extract archive.zip --list --verbose
```

**Options :**
- `archive` : Fichier ZIP à extraire (obligatoire)
- `-o, --output DIR` : Répertoire de destination (défaut: répertoire courant)
- `-p, --password PASS` : Mot de passe si archive chiffrée
- `--password-file FILE` : Lire le mot de passe depuis un fichier
- `--list` : Lister le contenu sans extraire
- `-v, --verbose` : Mode verbeux

---

## 🔒 Sécurité

### Chiffrement AES-256

Le module utilise **pyzipper** pour le chiffrement AES-256 :

- **Standard industriel** : AES-256 est le standard de chiffrement militaire
- **Compatible** : Les archives sont compatibles avec 7-Zip, WinZip, etc.
- **Sécurisé** : Beaucoup plus sécurisé que le chiffrement ZIP standard

### Bonnes Pratiques

✅ **À FAIRE** :
- Utiliser `--password-file` pour éviter les mots de passe dans l'historique shell
- Utiliser des mots de passe forts (minimum 16 caractères)
- Stocker les mots de passe de manière sécurisée (gestionnaire de mots de passe)
- Tester l'extraction après création d'une archive chiffrée

❌ **À NE PAS FAIRE** :
- Ne jamais commiter un fichier `.password` dans Git
- Ne jamais utiliser de mots de passe faibles
- Ne jamais partager le mot de passe avec l'archive sur le même canal

### Protection du Mot de Passe

Le mot de passe n'est jamais affiché ni enregistré dans les logs :

```bash
# Créer un fichier de mot de passe
echo "my_secret_password_123" > .password

# Utiliser le fichier
ambulon zip-create docs/ --password-file .password

# Ajouter au .gitignore
echo ".password" >> .gitignore
```

---

## 📚 API Python

### Utilisation Programmatique

```python
from pathlib import Path
from app.zip.core.zip_manager import ZipManager

# Initialiser le manager
manager = ZipManager()

# Créer une archive simple
manager.create_archive(
    sources=[Path("docs/")],
    output=Path("docs.zip")
)

# Créer une archive chiffrée
manager.create_archive(
    sources=[Path("docs/"), Path("README.md")],
    output=Path("secure.zip"),
    password="secret123",
    compression_level=9
)

# Avec exclusions
manager.create_archive(
    sources=[Path("src/")],
    output=Path("src.zip"),
    exclude_patterns=["*.pyc", "__pycache__", "*.egg-info"]
)

# Extraire une archive
manager.extract_archive(
    archive=Path("secure.zip"),
    output_dir=Path("extracted/"),
    password="secret123"
)

# Lister le contenu
contents = manager.list_contents(
    archive=Path("archive.zip")
)

for item in contents:
    print(f"{item['filename']} ({item['file_size']} bytes)")
```

### Classe ZipManager

```python
class ZipManager:
    """Gestionnaire d'archives ZIP avec support AES-256."""

    def create_archive(
        self,
        sources: List[Path],
        output: Path,
        password: Optional[str] = None,
        compression_level: int = 6,
        exclude_patterns: Optional[List[str]] = None,
        recursive: bool = True
    ) -> Path:
        """Crée une archive ZIP."""

    def extract_archive(
        self,
        archive: Path,
        output_dir: Path,
        password: Optional[str] = None
    ) -> List[Path]:
        """Extrait une archive ZIP."""

    def list_contents(
        self,
        archive: Path,
        password: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Liste le contenu d'une archive."""
```

---

## 🎯 Exemples Complets

### Exemple 1 : Archive Simple

```bash
# Créer
ambulon zip-create documents/

# Extraire
ambulon zip-extract documents.zip -o restored/
```

### Exemple 2 : Archive Chiffrée

```bash
# Créer fichier mot de passe
echo "MyS3cur3P@ssw0rd!" > .password

# Créer archive chiffrée
ambulon zip-create confidential/ --password-file .password

# Extraire
ambulon zip-extract confidential.zip --password-file .password
```

### Exemple 3 : Projet Python

```bash
# Archiver un projet Python (exclure cache)
ambulon zip-create src/ \
  --exclude "*.pyc" \
  --exclude "__pycache__" \
  --exclude "*.egg-info" \
  --exclude ".pytest_cache" \
  -o myproject.zip
```

### Exemple 4 : Sauvegarde Complète

```bash
# Sauvegarde chiffrée avec compression max
ambulon zip-create \
  ~/Documents/ \
  ~/Pictures/ \
  --password-file ~/.backup_password \
  --compression 9 \
  -o backup_$(date +%Y%m%d).zip \
  --verbose
```

### Exemple 5 : Inspection d'Archive

```bash
# Lister le contenu
ambulon zip-extract archive.zip --list

# Détails complets
ambulon zip-extract archive.zip --list --verbose
```

---

## 🐛 Dépannage

### Mot de passe incorrect

**Erreur** : `Incorrect password or password required for this archive`

**Solution** :
```bash
# Vérifier le fichier de mot de passe
cat .password

# Essayer avec mot de passe direct (pour test uniquement)
ambulon zip-extract archive.zip -p "test123"
```

### Archive corrompue

**Erreur** : `Failed to extract archive: Bad CRC-32`

**Solution** :
- L'archive est corrompue ou incomplète
- Vérifier l'intégrité du téléchargement
- Réessayer la création de l'archive

### pyzipper non installé

**Erreur** : `ModuleNotFoundError: No module named 'pyzipper'`

**Solution** :
```bash
# Installer pyzipper
pip install pyzipper

# Ou avec poetry
poetry add pyzipper
```

### Fichiers exclus par erreur

**Solution** :
```bash
# Mode verbeux pour voir quels fichiers sont ajoutés
ambulon zip-create src/ --exclude "*.pyc" --verbose
```

---

## 💡 Astuces

### 1. Archivage Sélectif

```bash
# N'archiver que les fichiers .md
ambulon zip-create docs/ --exclude "*" --exclude "!*.md"
```

### 2. Tester une Archive

```bash
# Créer avec test
ambulon zip-create docs/ -o test.zip && ambulon zip-extract test.zip --list
```

### 3. Compression vs Vitesse

```bash
# Rapide (moins de compression)
ambulon zip-create large_project/ --compression 1

# Petit (plus de compression)
ambulon zip-create large_project/ --compression 9
```

### 4. Archiver Plusieurs Projets

```bash
# Archiver plusieurs répertoires
ambulon zip-create project1/ project2/ project3/ -o all_projects.zip
```

---

## 📄 Compatibilité

### Logiciels Compatibles

Les archives créées par Ambulon sont compatibles avec :

✅ **7-Zip** (Windows/Linux/Mac)
✅ **WinZip** (Windows/Mac)
✅ **Windows Explorer** (Windows 10+)
✅ **macOS Archive Utility** (macOS)
✅ **p7zip** (Linux)
✅ **Toute outil supportant AES-256 ZIP**

### Standards

- **Format** : ZIP 2.0
- **Chiffrement** : WinZip AES-256
- **Compression** : Deflate

---

## 🔗 Voir Aussi

- [pyzipper Documentation](https://github.com/danifus/pyzipper)
- [ZIP Format Specification](https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT)
- [AES Encryption](https://fr.wikipedia.org/wiki/Advanced_Encryption_Standard)

---

## 📄 Licence

Ce module fait partie du projet Ambulon.

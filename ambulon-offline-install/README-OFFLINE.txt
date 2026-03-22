================================================================================
  AMBULON v3.0.1 - Package d'Installation Offline
================================================================================

Ce package contient Ambulon et TOUTES ses dependances pour une installation
sans connexion Internet.


================================================================================
  PREREQUIS (sur la machine cible)
================================================================================

1. Python 3.10 ou superieur doit etre installe

   Pour verifier:
   > python --version

   Si Python n'est pas installe, telechargez-le depuis:
   https://www.python.org/downloads/

   IMPORTANT: Cochez "Add Python to PATH" lors de l'installation !

2. pip doit etre installe (inclus avec Python par defaut)

   Pour verifier:
   > pip --version


================================================================================
  CONTENU DU PACKAGE
================================================================================

ambulon-offline-install/
├── wheels/                         (50 fichiers .whl, 82 MB)
│   ├── ambulon-3.0.1-py3-none-any.whl
│   ├── requests-2.32.5-py3-none-any.whl
│   ├── pyyaml-6.0.3-cp310-cp310-win_amd64.whl
│   └── ... (47 autres dependances)
├── install-offline.bat             Script d'installation Windows
└── README-OFFLINE.txt              Ce fichier


================================================================================
  METHODE 1: INSTALLATION AUTOMATIQUE (WINDOWS)
================================================================================

1. Decompressez l'archive ambulon-3.0.1-offline-install.zip

2. Ouvrez le dossier ambulon-offline-install/

3. Double-cliquez sur:
   > install-offline.bat

4. Suivez les instructions a l'ecran

5. Verifiez l'installation:
   > ambulon --version

   Doit afficher: ambulon 3.0.1


================================================================================
  METHODE 2: INSTALLATION MANUELLE
================================================================================

1. Ouvrez un terminal (cmd, PowerShell, ou bash)

2. Naviguez vers le dossier ambulon-offline-install:
   > cd chemin\vers\ambulon-offline-install

3. Installez avec pip:
   > pip install --no-index --find-links=.\wheels ambulon

   IMPORTANT: Les options --no-index et --find-links sont essentielles
   pour forcer pip a utiliser les wheels locales sans connexion Internet.

4. Verifiez l'installation:
   > ambulon --version


================================================================================
  VERIFICATION DE L'INSTALLATION
================================================================================

Pour verifier qu'Ambulon est correctement installe:

> ambulon --version
  ambulon 3.0.1

> ambulon --help
  Usage: ambulon [OPTIONS] COMMAND [ARGS]...
  ...

Si la commande 'ambulon' n'est pas reconnue:
- Redemarrez votre terminal
- Verifiez que Python Scripts/ est dans votre PATH
- Ou utilisez: python -m app.cli.cli --version


================================================================================
  EXEMPLES D'UTILISATION
================================================================================

# Initialiser la configuration
ambulon init

# Convertir PDF vers HTML
ambulon pdf2html document.pdf

# Convertir Markdown vers HTML
ambulon md2html readme.md

# Encapsuler du code dans un bloc Markdown
ambulon code2md script.py

# Scanner un document (OCR)
ambulon scan-image document.jpg

# Cloner des projets GitLab
ambulon gitlab-clone --help

# Recherche RAG avec PIAG
ambulon piag-search "ma recherche" --collection-name MaCollection

# Synchroniser WikiSI
ambulon wikisi-sync-api --verbose

# Voir toutes les commandes disponibles
ambulon --help


================================================================================
  DESINSTALLATION
================================================================================

Pour desinstaller Ambulon:

> pip uninstall ambulon

Cela NE supprimera PAS les dependances partagees (requests, pyyaml, etc.)
car elles peuvent etre utilisees par d'autres packages Python.


================================================================================
  ARCHITECTURE COMPATIBLE
================================================================================

Ce package contient des wheels pour:
- Python: 3.10+
- Plateforme: Windows (win_amd64)
- Architecture: x86_64 (64-bit)

Pour d'autres plateformes (Linux, macOS), vous devrez regenerer le package
sur une machine avec connexion Internet en utilisant:
> pip download ambulon==3.0.1 -d ./wheels/


================================================================================
  TAILLE ET DEPENDANCES
================================================================================

Taille totale: 82 MB (50 packages)

Dependances principales:
- requests       : Requetes HTTP
- pyyaml         : Lecture de fichiers YAML
- pillow         : Traitement d'images
- pymupdf        : Manipulation de PDF
- beautifulsoup4 : Parsing HTML
- lxml           : Parsing XML
- mcp            : Serveur MCP pour assistants IA
- playwright     : Automatisation navigateur
- markdown       : Conversion Markdown
- python-slugify : Generation de slugs

Et 40+ dependances transitives (urllib3, certifi, pydantic, etc.)


================================================================================
  SUPPORT ET DOCUMENTATION
================================================================================

Documentation complete:
https://github.com/warchosian/ambulon

Signaler un bug:
https://github.com/warchosian/ambulon/issues

Version: 3.0.1
Date: 2026-01-30
Licence: MIT


================================================================================
  NOTES TECHNIQUES
================================================================================

Ce package d'installation offline utilise la methode standard Python
"pip download" pour telecharger toutes les wheels necessaires.

Les wheels sont des archives .whl qui contiennent du code Python pre-compile
et des metadonnees. Elles sont plus rapides a installer que les sources.

L'option --no-index empeche pip de chercher sur PyPI (Python Package Index).
L'option --find-links=./wheels indique a pip ou trouver les packages locaux.

Cette methode est la solution officielle recommandee par pip pour les
installations offline:
https://pip.pypa.io/en/stable/topics/local-project-installs/


================================================================================
  FIN
================================================================================

# Ambulon 3.0.4 - Installation Offline (Wheels Exposées)

## Installation

1. Assurez-vous que le dossier `wheels/` contient toutes les wheels (dont `kroki`)
2. Exécutez la commande suivante :
   ```bash
   python -m pip install --no-index --find-links=wheels ambulon
   ```

Cette commande installe Ambulon et toutes les dépendances depuis les wheels locales.

## Désinstallation

```bash
python uninstall_offline.py
```

## Versions Python supportées

- Python 3.10
- Python 3.11
- Python 3.12

## Structure

```
dist-offline/
├── wheels/              # Wheels pour toutes les versions Python
│   ├── ambulon-3.0.4-py3-none-any.whl
│   ├── pillow-*-cp310-*.whl
│   ├── pillow-*-cp311-*.whl
│   ├── pillow-*-cp312-*.whl
│   └── ...
├── install_offline.py   # Script d'installation intelligent
├── uninstall_offline.py # Script de désinstallation
└── README.md           # Ce fichier
```

## Utilisation

Après installation :
```bash
ambulon --version
ambulon --help
```

---
**Version**: 3.0.4
**Licence**: MIT

# Ambulon 3.0.3 - Installation Offline (Wheels Exposées)

## Installation

1. Téléchargez `install_offline.py`
2. Exécutez :
   ```bash
   python install_offline.py
   ```

Le script téléchargera automatiquement les wheels compatibles avec votre version Python depuis ce dossier et les installera.

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
│   ├── ambulon-3.0.3-py3-none-any.whl
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
**Version**: 3.0.3
**Licence**: MIT

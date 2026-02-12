# Installation Offline Ambulon

## Installation en 2 PHASES SÉPARÉES

### PHASE 1 : Téléchargement (ONLINE - sur un poste avec internet)

```bash
python download_wheels.py
```

**Ce que fait ce script** :
- Télécharge ~150 wheels depuis GitHub (~143 MB)
- Crée le dossier `wheels/`
- **N'installe RIEN** - juste téléchargement

**Résultat** : dossier `wheels/` prêt à être copié

---

### PHASE 2 : Installation (OFFLINE - sur le poste cible SANS internet)

Copiez le dossier `dist-offline/` complet (avec `wheels/`) sur le poste cible, puis :

```bash
python install_offline.py
```

**Ce que fait ce script** :
- Installe ambulon + toutes dépendances depuis `wheels/`
- Mode OFFLINE : aucun accès internet
- Affiche la commande pip exécutée
- Affiche un résumé de l'installation

**C'est tout !**

---

## 📦 Ce qui est installé

```bash
ambulon --version
ambulon --help
```

Si `ambulon` n'est pas reconnu, redémarrez votre terminal.

---

## 📋 Prérequis

- Python 3.10, 3.11 ou 3.12
- pip inclus avec Python

---

## Structure du package

```
dist-offline/
  - download_wheels.py       (Phase 1 - ONLINE)
  - install_offline.py       (Phase 2 - OFFLINE)
  - uninstall_offline.py     (Désinstallation)
  - README_OFFLINE.md        (Ce fichier)
  - wheels/                  (Généré - 150 fichiers, 143 MB)
```

---

## ⚡ Pourquoi c'est simple ?

- **Pas de configuration** : pip résout les dépendances automatiquement
- **Pas de parsing** : pas besoin de lire poetry.lock ou pyproject.toml
- **Juste 2 commandes** : download puis install

---

## 🔧 Dépannage

| Problème | Solution |
|----------|----------|
| `wheels/` introuvable | Exécutez d'abord `python download_wheels.py` |
| Python version incorrecte | Installez Python 3.10, 3.11 ou 3.12 |
| `ambulon` non reconnu | Redémarrez le terminal |


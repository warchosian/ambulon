# Guide Rapide - Option A : Installation Automatique

## Installation en 2 commandes

### Etape 1 : Telecharger le script

**Windows (PowerShell)** :
```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/warchosian/ambulon/preprod/v3.0.2-stable/dist-offline/install_from_github.py" -OutFile "install_from_github.py"
```

**Windows (curl)** :
```bash
curl -O https://raw.githubusercontent.com/warchosian/ambulon/preprod/v3.0.2-stable/dist-offline/install_from_github.py
```

**Linux/Mac** :
```bash
wget https://raw.githubusercontent.com/warchosian/ambulon/preprod/v3.0.2-stable/dist-offline/install_from_github.py
```

### Etape 2 : Executer le script

```bash
python install_from_github.py
```

**C'est tout !** Le script fait automatiquement :
- Creation du repertoire `wheels/`
- Telechargement des 70 wheels depuis GitHub (~130 MB)
- Installation d'Ambulon en mode offline

---

## Modes d'installation

### Mode Automatique (par defaut)

```bash
python install_from_github.py
```

**Phases** :
1. **CREATION DU REPERTOIRE** (toujours)
2. **TELECHARGEMENT** (online - internet requis)
3. **INSTALLATION** (offline - sans internet)

### Mode Offline

Si vous avez deja les wheels :

```bash
python install_from_github.py --offline
```

**Phases** :
1. **CREATION DU REPERTOIRE** (toujours)
2. **TELECHARGEMENT** (ignore - wheels deja presentes)
3. **INSTALLATION** (offline - sans internet)

---

## Ce que fait le script

### Phase 1 : Creation du repertoire
```
[OK] Repertoire wheels/ cree
```

### Phase 2 : Telechargement (si necessaire)
```
[INFO] ! Cette phase necessite une CONNEXION INTERNET
       Les wheels seront telechargees depuis GitHub

[INFO] Telechargement de 70 wheels depuis GitHub...
       URL: https://raw.githubusercontent.com/warchosian/ambulon/preprod/v3.0.2-stable/dist-offline/wheels

  Telechargement: ambulon-3.0.3-py3-none-any.whl... OK
  Telechargement: beautifulsoup4-4.14.3-py3-none-any.whl... OK
  ...

[OK] 70/70 wheels telechargees
     Taille totale: 129.8 MB
```

### Phase 3 : Installation (offline)
```
[INFO] OK Cette phase fonctionne HORS LIGNE
       Installation depuis les wheels locales uniquement

[CMD] python -m pip install --no-index --find-links=wheels ambulon

[INFO] Equivalent simplifie:
       pip install --no-index --find-links=wheels ambulon

[OK] Installation terminee avec succes ! OK
```

---

## Verification

Apres installation :

```bash
ambulon --version
# Ambulon version 3.0.3
```

Si la commande n'est pas trouvee :
```bash
# Redemarrez votre terminal
# Ou utilisez :
python -m app.cli.cli --version
```

---

## Commandes affichees par le script

Le script affiche toutes les commandes pip executees :

**Commande complete** :
```
[CMD] python -m pip install --no-index --find-links=wheels ambulon
```

**Version simplifiee** :
```
[INFO] Equivalent simplifie:
       pip install --no-index --find-links=wheels ambulon
```

Vous pouvez utiliser la version simplifiee directement si vous avez deja le dossier `wheels/`.

---

## Desinstallation

### Desinstaller uniquement Ambulon
```bash
pip uninstall ambulon
```

### Desinstaller Ambulon + dependances
```bash
pip uninstall ambulon mcp playwright greenlet markdown beautifulsoup4 python-slugify lxml chardet pyyaml requests pymupdf pillow importlib-resources
```

---

## Avantages de l'Option A

✓ **Rapide** : 2 commandes seulement
✓ **Automatique** : Le script gere tout
✓ **Intelligent** : Detecte si wheels deja presentes
✓ **Transparent** : Affiche toutes les commandes
✓ **Modes multiples** : Automatique ou offline
✓ **Compatible** : Python 3.10, 3.11, 3.12

---

## Troubleshooting

### Erreur : "No module named 'urllib'"

Solution : Verifiez votre installation Python
```bash
python --version
# Python 3.10+ requis
```

### Erreur : "HTTP 404" lors du telechargement

Cause : URL GitHub incorrecte ou branche inexistante

Solution : Verifiez que la branche `preprod/v3.0.2-stable` existe sur GitHub

### Les wheels ne se telechargent pas

Solution : Verifiez votre connexion internet
```bash
# Testez la connexion
curl -I https://raw.githubusercontent.com/warchosian/ambulon/preprod/v3.0.2-stable/dist-offline/wheels/ambulon-3.0.3-py3-none-any.whl
```

### Installation echoue meme avec wheels presentes

Solution : Verifiez que les wheels sont compatibles
```bash
# Lister les wheels
ls wheels/

# Verifier la version ambulon
ls wheels/ambulon-*.whl
# Devrait afficher: ambulon-3.0.3-py3-none-any.whl
```

---

## Comparaison Option A vs Option B

| Critere | Option A (Script auto) | Option B (Manuel) |
|---------|------------------------|-------------------|
| Commandes | 2 | 3-4 |
| Telechargement | Automatique | Manuel (git/zip) |
| Taille telechargee | ~130 MB (wheels) | ~130 MB + depot git |
| Temps | ~2-5 min | ~5-10 min |
| Complexite | Faible | Moyenne |
| Mode offline | Oui (--offline) | Oui (par defaut) |

**Recommandation** : Utilisez Option A sauf si vous voulez le depot git complet.

---

**Version** : 3.0.3
**Derniere mise a jour** : 2026-02-05
**Support** : https://github.com/warchosian/ambulon/issues

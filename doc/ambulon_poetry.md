Voici un **guide Markdown complet** (`setup-ambulon-guide.md`) détaillant pas à pas la résolution des problèmes rencontrés, **spécifiquement adapté à votre configuration portable Windows 10** (Anaconda sur `G:\`, sans PATH global, sans droits admin).

---

# 🛠️ Guide d’installation de Poetry + Commitizen pour Ambulon  
> *Hervé Marchal — Environnement portable Windows 10 / Anaconda*  
> ✅ Fonctionne **sans `conda` ni `poetry` dans le PATH**  
> ✅ Utilise uniquement des **chemins absolus**  
> ✅ Compatible PowerShell natif

---

## 🧩 Problème initial

```powershell
PS C:\Users\herve.marchal> poetry
poetry : Le terme «poetry» n'est pas reconnu...
PS C:\Users\herve.marchal> conda activate conda_ai10
conda : Le terme «conda» n'est pas reconnu...
PS C:\Users\herve.marchal> python
python : Le terme «python» n'est pas reconnu...
```

→ Ni `conda`, ni `python`, ni `poetry` ne sont dans le `PATH` système.  
→ Mais vous avez Anaconda **portable** ici :  
`G:\WarchoLife\WarchoPortable\PortableWork\Anaconda\anaconda-3\`

---

## ✅ Solution : utiliser les chemins absolus

### 1. Vérifier que Python fonctionne (base Anaconda)

```powershell
& "G:\WarchoLife\WarchoPortable\PortableWork\Anaconda\anaconda-3\python.exe" -c "import sys; print(sys.version)"
# → Python 3.12.4 | packaged by Anaconda, Inc. | ...
```

✅ OK — Python est accessible via son chemin absolu.

---

### 2. Vérifier que l’environnement `conda_ai10` existe

Chemin typique :  
`G:\WarchoLife\WarchoPortable\PortableWork\Anaconda\anaconda-3\envs\conda_ai10\python.exe`

```powershell
Test-Path "G:\WarchoLife\WarchoPortable\PortableWork\Anaconda\anaconda-3\envs\conda_ai10"
# → True
```

✅ OK — l’environnement existe.

---

### 3. Installer Poetry (déjà fait ✅)

```powershell
& "G:\WarchoLife\WarchoPortable\PortableWork\Anaconda\anaconda-3\envs\conda_ai10\python.exe" -m pip install poetry
# → Requirement already satisfied: poetry in ... (2.2.1)
```

✅ Poetry est installé **dans `conda_ai10`**.

---

### 4. Se placer dans le dossier projet

```powershell
cd G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon
```

⚠️ **Important** : `poetry` ne fonctionne que si un `pyproject.toml` est présent (ou dans un parent).

---

### 5. Initialiser le projet Poetry (si absent)

```powershell
& "G:\WarchoLife\WarchoPortable\PortableWork\Anaconda\anaconda-3\envs\conda_ai10\python.exe" -m poetry init --name ambulon --no-interaction
```

→ Crée `pyproject.toml`.

---

### 6. Ajouter Commitizen

```powershell
& "G:\WarchoLife\WarchoPortable\PortableWork\Anaconda\anaconda-3\envs\conda_ai10\python.exe" -m poetry add --group dev commitizen
```

→ Met à jour `pyproject.toml` + `poetry.lock`.

---

### 7. Installer les dépendances (⚠️ erreur `README.md`)

```powershell
& "G:\WarchoLife\WarchoPortable\PortableWork\Anaconda\anaconda-3\envs\conda_ai10\python.exe" -m poetry install --no-root
```

> 🔍 Pourquoi `--no-root` ?  
> L’erreur `Readme path ...README.md does not exist` survient car Poetry tente d’installer le *projet courant* comme paquet (mode *package*).  
> `--no-root` → installe seulement les dépendances, pas le projet.

✅ Après cela, `commitizen` est bien dans le venv Poetry (`ambulon-ccBhI1VF-py3.10`).

---

### 8. ✅ Finaliser : `cz init`

```powershell
& "G:\WarchoLife\WarchoPortable\PortableWork\Anaconda\anaconda-3\envs\conda_ai10\python.exe" -m poetry run cz init
```

→ Répondre aux questions (ex. Conventional Commits), puis :

```powershell
Creating configuration file pyproject.toml
```

✅ **Succès !** Le fichier `pyproject.toml` contient désormais :

```toml
[tool.commitizen]
name = "cz_conventional_commits"
version = "0.1.0"
tag_format = "v$version"
```

---

### 9. Tester

```powershell
& "G:\WarchoLife\WarchoPortable\PortableWork\Anaconda\anaconda-3\envs\conda_ai10\python.exe" -m poetry run cz check --commit-msg "feat: add Docurba parser"
# → Commit message follows commitizen pattern ✅
```

---

## 🧪 Bonus : alias temporaires (session PowerShell)

Pour gagner du temps :

```powershell
Set-Alias py "G:\WarchoLife\WarchoPortable\PortableWork\Anaconda\anaconda-3\envs\conda_ai10\python.exe"
Set-Alias poetry "py -m poetry"
```

Puis :
```powershell
poetry run cz commit
```

---

## 📦 Résumé des commandes clés (copier-coller)

```powershell
# 1. Aller dans le projet
cd G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon

# 2. Initialiser (si pas de pyproject.toml)
& "G:\WarchoLife\WarchoPortable\PortableWork\Anaconda\anaconda-3\envs\conda_ai10\python.exe" -m poetry init --name ambulon --no-interaction

# 3. Ajouter commitizen
& "G:\WarchoLife\WarchoPortable\PortableWork\Anaconda\anaconda-3\envs\conda_ai10\python.exe" -m poetry add --group dev commitizen

# 4. Installer (sans erreur README)
& "G:\WarchoLife\WarchoPortable\PortableWork\Anaconda\anaconda-3\envs\conda_ai10\python.exe" -m poetry install --no-root

# 5. Configurer commitizen
& "G:\WarchoLife\WarchoPortable\PortableWork\Anaconda\anaconda-3\envs\conda_ai10\python.exe" -m poetry run cz init
```

---

## 🚀 Prochaines étapes

- [ ] Créer un `README.md` pour éviter `--no-root` à l’avenir  
- [ ] Générer un `.cz.yaml` adapté au contexte ministériel (ex. mots-clés `docurba`, `urbanisme`)  
- [ ] Intégrer à GitLab CI/CD (`poetry run cz check --commit-msg "$CI_COMMIT_TITLE"`)

Souhaitez-vous que je vous génère :
- Un **template `README.md` minimaliste pour Ambulon** ?
- Un **`.cz.yaml` préconfiguré pour les commits Docurba** (ex. types `urbanisme`, `pac`, `ddtm`) ?

Dites-moi 👇
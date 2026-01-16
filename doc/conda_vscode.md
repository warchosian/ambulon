# 🧠 Guide de configuration propre de Conda dans VS Code (Windows)

> **Objectif** : Activer automatiquement un environnement Conda **nommé comme le dossier du projet** dans VS Code, **sans double activation**, **sans conflits**, et **sans dépendance à l’initialisation globale de Conda**.

---

## 📌 Contexte

- Vous utilisez **Anaconda/Miniconda sur Windows** (chemins `G:\...`).
- Chaque projet est dans un dossier dont le **nom = nom de l’environnement Conda** (ex. `atarax` → env `atarax`).
- Vous souhaitez que VS Code active cet environnement **automatiquement** dans les terminaux (`cmd` et PowerShell).
- Vous **ne voulez pas** que `base` soit activé au démarrage, ni voir de doubles appels (`activate` suivi de `conda activate`).

---

## 🔧 Étape 1 : Désactiver l’activation automatique de `base`

Exécutez **une seule fois** dans un terminal (CMD ou PowerShell) :

```cmd
conda config --set auto_activate_base false
```

✅ Vérifiez avec :
```cmd
conda config --show auto_activate_base
# → doit afficher : auto_activate_base: false
```

> Cela modifie le fichier `C:\Users\herve.marchal\.condarc`.

---

## 🔧 Étape 2 : Nettoyer l’initialisation automatique de **CMD**

### Problème
`conda init cmd.exe` ajoute un hook dans le registre Windows (`AutoRun`), ce qui force une initialisation à chaque lancement de `cmd.exe`.

### Solution
1. Ouvrez `regedit`.
2. Allez dans :
   ```
   HKEY_CURRENT_USER\Software\Microsoft\Command Processor
   ```
3. Modifiez la valeur **`AutoRun`**.
4. **Commentez la ligne Conda** avec `REM` :

```bat
REM if exist "G:\WarchoLife\WarchoPortable\PortableWork\Anaconda\anaconda-3\condabin\conda_hook.bat" "G:\WarchoLife\WarchoPortable\PortableWork\Anaconda\anaconda-3\condabin\conda_hook.bat"
```

> ✅ Cela désactive le hook tout en gardant la trace pour plus tard.

---

## 🔧 Étape 3 : Nettoyer l’initialisation automatique de **PowerShell**

### Problème
`conda init powershell` modifie le profil utilisateur (`$PROFILE`) pour charger Conda à chaque session.

### Solution
1. Dans PowerShell, exécutez :
   ```powershell
   echo $PROFILE
   ```
   → Exemple de sortie :  
     `C:\Users\herve.marchal\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1`

2. Ouvrez ce fichier avec un éditeur :
   ```powershell
   notepad $PROFILE
   ```

3. **Commentez le bloc Conda** avec `#` :

```powershell
# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
# (& "G:\WarchoLife\WarchoPortable\PortableWork\Anaconda\anaconda-3\Scripts\conda.exe" "shell.powershell" "hook") | Out-String | Invoke-Expression
# <<< conda initialize <<<
```

> ✅ Le hook est désactivé, mais récupérable si besoin.

---

## 🔧 Étape 4 : Configurer `.vscode/settings.json` par projet

Placez ce fichier à la racine de **chaque projet**, dans `.vscode/settings.json` :

```json
{
    "liveServer.settings.port": 5501,
    "makefile.configureOnOpen": false,

    "python.defaultInterpreterPath": "G:\\WarchoLife\\WarchoPortable\\PortableWork\\Anaconda\\anaconda-3\\envs\\${workspaceFolderBasename}\\python.exe",
    "python.terminal.activateEnvironment": true,
    "python.terminal.activateEnvInCurrentTerminal": true,
    "python.condaPath": "G:\\WarchoLife\\WarchoPortable\\PortableWork\\Anaconda\\anaconda-3\\condabin\\conda.bat",

    "terminal.integrated.defaultProfile.windows": "PowerShell",

    "terminal.integrated.profiles.windows": {
        "PowerShell": {
            "source": "PowerShell",
            "args": [
                "-NoExit",
                "-Command",
                "conda activate ${workspaceFolderBasename}"
            ]
        },
        "Command Prompt": {
            "path": "C:\\WINDOWS\\system32\\cmd.exe",
            "args": [
                "/k",
                "G:\\WarchoLife\\WarchoPortable\\PortableWork\\Anaconda\\anaconda-3\\Scripts\\activate.bat",
                "${workspaceFolderBasename}"
            ]
        }
    },

    "python.envFile": "${workspaceFolder}/.env"
}
```

### ⚠️ Conditions requises
- Le **nom du dossier du projet** doit correspondre **exactement** au nom de l’environnement Conda.
- Le chemin `G:\...\anaconda-3\Scripts` doit être dans votre **`PATH` Windows** (pour que `conda` soit trouvable dans PowerShell).

Vérifiez avec :
```powershell
where.exe conda
# → Doit retourner le chemin vers conda.exe
```

---

## ✅ Résultat attendu

Dans VS Code, lors de l’ouverture d’un terminal :

- **PowerShell** → `(mon_projet) G:\...>`
- **Command Prompt** → `(mon_projet) G:\...>`

→ **Une seule activation**, **pas de `(base)`**, **pas de lignes parasites**.

---

## 🛑 À éviter à l’avenir

- Ne **relancez pas** `conda init cmd.exe` ou `conda init powershell` → cela réinjecterait les hooks.
- N’utilisez **pas** `activate.bat` dans PowerShell → cela invoque `cmd.exe` et casse l’environnement.
- Ne mélangez **pas** `activate.bat` **et** `conda activate` dans les mêmes arguments.

---

## 💡 Bonus : Vérifier le shell courant

| Shell | Commande | Indice |
|------|--------|--------|
| **CMD** | `echo %COMSPEC%` | Retourne `cmd.exe` |
| **PowerShell** | `$Host.Name` | Retourne `ConsoleHost` |
| **WSL/Linux** | `echo $0` ou `ps -p $$` | Retourne `-bash`, `-zsh`, etc. |

---

> ✨ Avec cette configuration, vous avez un **contrôle total, propre et reproductible** de vos environnements Python par projet — sans magie noire, sans doublons, et sans dépendance à l’initialisation globale de Conda.

*Document rédigé pour Hervé Marchal – Janvier 2026*
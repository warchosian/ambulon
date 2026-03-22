# Instructions pour Lancer les Tests E2E PIAG

## ⚠️ IMPORTANT : N'utilisez PAS Git Bash !

L'erreur `No pyvenv.cfg file` que vous rencontrez est causée par un **conflit entre Git Bash et l'environnement conda Python sous Windows**.

---

## ✅ Solution : Utiliser un Terminal Windows Natif

### Option 1 : CMD (Invite de Commandes Windows)

1. **Ouvrir CMD** :
   - Appuyez sur `Win + R`
   - Tapez `cmd`
   - Appuyez sur Entrée

2. **Activer conda** :
   ```batch
   conda activate ambulon
   ```

3. **Aller dans le répertoire du projet** :
   ```batch
   cd G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon
   ```

4. **Lancer les tests** :
   ```batch
   python test_piag_all.py --config config\piag.yaml
   ```

---

### Option 2 : PowerShell Windows

1. **Ouvrir PowerShell** :
   - Appuyez sur `Win + X`
   - Sélectionnez "Windows PowerShell"

2. **Activer conda** :
   ```powershell
   conda activate ambulon
   ```

3. **Aller dans le répertoire du projet** :
   ```powershell
   cd G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon
   ```

4. **Lancer les tests** :
   ```powershell
   python test_piag_all.py --config config\piag.yaml
   ```

---

### Option 3 : Utiliser le Script Batch

**Double-cliquez simplement sur** :
```
RUN_TESTS_DIRECT.bat
```

Ce script détectera automatiquement votre environnement Python et lancera les tests.

---

### Option 4 : Utiliser le Chemin Complet de Python

Si vous voulez absolument utiliser Git Bash ou un autre terminal :

```bash
# Remplacez par le chemin réel de votre environnement conda
/g/WarchoLife/WarchoPortable/PortableWork/Anaconda/anaconda-3/envs/ambulon/python.exe test_piag_all.py --config config/piag.yaml
```

---

## 🔍 Diagnostic

Si vous rencontrez toujours des problèmes, lancez le diagnostic :

```batch
DIAGNOSE_PYTHON.bat
```

Cela vous indiquera exactement quel est le problème avec votre environnement Python.

---

## 📊 Résultats Attendus

Une fois les tests lancés avec succès, vous verrez :

```
================================================================================
TESTS END-TO-END - API PIAG (RAG + CHAT)
================================================================================

📝 Logs détaillés: test_output/rag/20260319_XXXXXX/logs/...
📂 Répertoire de sortie: test_output/

================================================================================
TEST RAG
================================================================================
✓ Client PIAG créé
...

================================================================================
TEST CHAT
================================================================================
✓ Test 1/4: API Key Info
...

================================================================================
RÉSULTATS FINAUX
================================================================================
✓ Tests RAG: RÉUSSI
✓ Tests CHAT: RÉUSSI
```

Tous les logs et réponses JSON seront sauvegardés dans `test_output/`.

---

## 🎯 Commandes Rapides

| Test | Commande |
|------|----------|
| **Tous les tests** | `python test_piag_all.py --config config\piag.yaml` |
| **RAG uniquement** | `python test_piag_rag_e2e.py --config config\piag.yaml` |
| **CHAT uniquement** | `python test_piag_chat_e2e.py --config config\piag.yaml` |
| **Vérifier config** | `python check_piag_config.py --config config\piag.yaml` |

---

## 💡 Pourquoi Git Bash ne Fonctionne Pas ?

Git Bash utilise un environnement POSIX simulé sous Windows qui :
- Ne détecte pas correctement les environnements virtuels Python
- A des problèmes avec les chemins Windows (backslashes vs slashes)
- Ne gère pas bien les variables d'environnement conda

**➡️ Solution : Utilisez toujours CMD ou PowerShell pour Python/conda sous Windows**

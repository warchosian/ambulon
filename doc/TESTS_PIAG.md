# Guide de Tests PIAG

Ce document décrit comment exécuter les différents types de tests pour le module PIAG.

## 📋 Types de Tests

### 1. Tests Unitaires Mockés (Sans Réseau) ✅

**Ces tests ne nécessitent AUCUNE connexion réseau et doivent TOUJOURS passer à 100%.**

Tous les appels HTTP et fichiers sont simulés (mockés) en mémoire.

#### Commandes

```bash
# Tests de la commande piag-collection-list (8 tests)
poetry run pytest tests/unit/piag/commands/test_piag_collection_list.py -v

# Tests du client PIAG (17 tests)
poetry run pytest tests/unit/piag/core/test_piag_client.py -v

# Tests du workflow E2E complet mocké (12 tests) - NOUVEAU !
poetry run pytest tests/unit/piag/test_piag_workflow_mocked.py -v -m unit

# Tous les tests mockés ensemble (37 tests)
poetry run pytest -m unit tests/unit/piag/ -v
```

#### Résultat Attendu

```
# Tests workflow E2E mocké
======================== 12 passed in 2.32s ========================

# Tous les tests unitaires mockés
======================== 37 passed in 8.50s ========================
```

**✅ 100% de réussite obligatoire (37/37 tests)**

#### Ce que le Workflow Mocké Teste

Le fichier `tests/unit/piag/test_piag_workflow_mocked.py` teste **11 étapes complètes** d'un workflow RAG PIAG :

1. ✅ Créer une collection
2. ✅ Mettre à jour la collection
3. ✅ Récupérer la collection
4. ✅ Uploader un document
5. ✅ Lister les documents
6. ✅ Récupérer les chunks du document
7. ✅ Rechercher dans la collection (RAG)
8. ✅ Récupérer le document par ID
9. ✅ Supprimer le document
10. ✅ Vérifier la suppression
11. ✅ Supprimer la collection (cleanup)

**Avantages du workflow mocké :**
- 🚀 Rapide (< 3 secondes)
- 🔒 Pas de réseau requis
- 🎯 Teste tous les appels API sans dépendance externe
- ✅ 100% reproductible

---

### 2. Test End-to-End Réel (Avec Réseau) 🌐

**Ce test nécessite une connexion au réseau PIAG et des credentials valides.**

#### Prérequis

Vous devez avoir accès à l'API PIAG avec l'une de ces méthodes :

##### Option A : Variables d'Environnement (Recommandé)

```bash
# Windows (CMD)
set PIAG_RAG_API_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
set PIAG_RAG_PROJECT_ID=your_project_id_here
set PIAG_RAG_BASE_URL=https://preprod.api.piag.e2.rie.gouv.fr/rag/

# Windows (PowerShell)
$env:PIAG_RAG_API_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
$env:PIAG_RAG_PROJECT_ID="your_project_id_here"
$env:PIAG_RAG_BASE_URL="https://preprod.api.piag.e2.rie.gouv.fr/rag/"

# Linux/Mac
export PIAG_RAG_API_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
export PIAG_RAG_PROJECT_ID="your_project_id_here"
export PIAG_RAG_BASE_URL="https://preprod.api.piag.e2.rie.gouv.fr/rag/"
```

##### Option B : Fichier de Configuration

Le test charge automatiquement depuis `config/piag.yaml` si les variables d'environnement ne sont pas définies.

```yaml
# config/piag.yaml
api:
  base_url: "https://preprod.api.piag.e2.rie.gouv.fr/rag/"

project:
  project_id: "your_project_id_here"

security:
  token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

#### Commandes

```bash
# Test E2E complet avec sortie détaillée
poetry run pytest tests/integration/test_piag_e2e_workflow.py -v -s

# Test E2E avec capture des logs dans un fichier
poetry run pytest tests/integration/test_piag_e2e_workflow.py -v -s > logs_e2e_piag.txt 2>&1
```

#### Ce que le Test E2E Vérifie

Le test exécute un workflow complet en 11 étapes :

1. ✅ **Créer une collection** test
2. ✅ **Mettre à jour** la collection
3. ✅ **Vérifier** la mise à jour
4. ✅ **Uploader** un document
5. ✅ **Lister** les documents
6. ✅ **Récupérer les chunks** du document
7. ✅ **Rechercher** dans la collection (RAG)
8. ✅ **Récupérer le document** par ID
9. ✅ **Supprimer** le document
10. ✅ **Vérifier** la suppression
11. ✅ **Supprimer** la collection (cleanup)

#### Durée Estimée

**15-30 secondes** (dépend de la latence réseau)

#### Résultat Attendu

```
tests/integration/test_piag_e2e_workflow.py::test_piag_e2e_workflow PASSED [100%]

======================== 1 passed in 23.45s ========================
```

---

## 🔍 Vérification de la Couverture de Code

### Tests Mockés avec Couverture

```bash
# Couverture uniquement pour les tests mockés
poetry run pytest \
  tests/unit/piag/commands/test_piag_collection_list.py \
  tests/unit/piag/core/test_piag_client.py \
  --cov=app.piag \
  --cov-report=term \
  --cov-report=html

# Voir le rapport HTML
start htmlcov/index.html   # Windows
open htmlcov/index.html    # Mac
xdg-open htmlcov/index.html  # Linux
```

### Objectif de Couverture

- **Minimum requis** : ≥ 80%
- **Cible recommandée** : ≥ 90%

---

## 🚨 Troubleshooting

### Erreur : "project_id requis"

**Cause** : Configuration manquante

**Solution** :
1. Vérifiez que `config/piag.yaml` existe (pas `piag.yml`)
2. Vérifiez que la section `project.project_id` est présente
3. Ou définissez `PIAG_RAG_PROJECT_ID` en variable d'env

### Erreur : "Token API requis"

**Cause** : Token manquant

**Solution** :
1. Définissez `PIAG_RAG_API_TOKEN` en variable d'env
2. Ou décommentez `security.token` dans `config/piag.yaml`

### Erreur : "SyntaxError: invalid syntax" (test E2E)

**Cause** : Erreur de syntaxe dans le fichier de test

**Solution** : Le fichier a été corrigé. Si l'erreur persiste :
```bash
# Vérifiez la première ligne du fichier
head -1 tests/integration/test_piag_e2e_workflow.py
# Devrait afficher: import pytest
```

### Test E2E Skip

**Message** : `SKIPPED [1] test_piag_e2e_workflow.py:39: PIAG_RAG_API_TOKEN and PIAG_RAG_PROJECT_ID environment variables or a valid config file must be set.`

**Cause** : Credentials non configurés

**Solution** : Configurez les variables d'environnement ou le fichier de config (voir section Prérequis ci-dessus)

---

## 📊 Résumé des Commandes

### 🚀 Commandes avec Markers Pytest (Standard)

**Utilisez les markers pytest pour choisir quel type de tests exécuter.**

#### Markers Disponibles

| Marker | Description | Réseau requis ? |
|--------|-------------|-----------------|
| `unit` | Tests unitaires mockés | ❌ Non |
| `integration` | Tests d'intégration réels | ✅ Oui (API PIAG) |

#### Commandes Standard

```bash
# 1. Tests mockés UNIQUEMENT (rapide, pas de réseau)
poetry run pytest -m "unit" tests/unit/piag/ -v

# 2. Tests d'intégration UNIQUEMENT (réel, réseau requis)
poetry run pytest -m "integration" tests/integration/ -v -s

# 3. TOUS les tests sauf intégration (mock uniquement)
poetry run pytest -m "not integration" -v

# 4. TOUS les tests (mock + intégration si config dispo)
poetry run pytest tests/unit/piag/commands/test_piag_collection_list.py tests/unit/piag/core/test_piag_client.py tests/integration/test_piag_e2e_workflow.py -v -s
```

#### Comportement Intelligent

**La commande s'adapte automatiquement selon votre configuration :**

| Fichier `config/piag.yaml` | Test E2E | Résultat |
|----------------------------|----------|----------|
| ✅ **Existe avec token + project_id** | **EXÉCUTÉ** (appels API réels) | `26 passed` |
| ❌ **N'existe pas OU incomplet** | **SKIPPÉ** (pas d'erreur) | `25 passed, 1 skipped` |

**Pas besoin de changer la commande !** Le test E2E détecte automatiquement s'il peut tourner.

#### Exemples de Résultats

**Cas 1 : Sur le réseau PIAG avec `config/piag.yaml` configuré**
```
tests/unit/piag/commands/test_piag_collection_list.py::... 8 passed
tests/unit/piag/core/test_piag_client.py::... 17 passed
tests/integration/test_piag_e2e_workflow.py::test_piag_e2e_workflow PASSED

======================== 26 passed in 25.32s ========================
✅ Mode RÉEL : API PIAG contactée
```

**Cas 2 : Sans connexion ou config incomplète**
```
tests/unit/piag/commands/test_piag_collection_list.py::... 8 passed
tests/unit/piag/core/test_piag_client.py::... 17 passed
tests/integration/test_piag_e2e_workflow.py::test_piag_e2e_workflow SKIPPED

==================== 25 passed, 1 skipped in 3.45s ====================
✅ Mode MOCK uniquement : Aucun réseau requis
```

#### Pourquoi c'est Intelligent ?

1. **Tests mockés** : Tournent TOUJOURS (pas de config requise)
2. **Test E2E** : Lit `config/piag.yaml` et décide automatiquement :
   - Config valide → Tourne en mode RÉEL
   - Pas de config → Se skip sans erreur

**Vous n'avez qu'UNE SEULE commande à retenir !**

---

### Tests Rapides (Sans Réseau)

```bash
# Lancer UNIQUEMENT les tests mockés
poetry run pytest tests/unit/piag/commands/test_piag_collection_list.py tests/unit/piag/core/test_piag_client.py -v
```

**✅ Résultat attendu : 25/25 passed**

### Tests Complets (Avec Réseau)

```bash
# 1. Configurer l'environnement
set PIAG_RAG_API_TOKEN=votre_token
set PIAG_RAG_PROJECT_ID=votre_project_id

# 2. Lancer le test E2E
poetry run pytest tests/integration/test_piag_e2e_workflow.py -v -s
```

**✅ Résultat attendu : 1/1 passed**

---

## 📝 Notes Importantes

1. **Tests mockés** :
   - ✅ Peuvent être exécutés PARTOUT
   - ✅ Ne nécessitent AUCUNE configuration
   - ✅ Doivent TOUJOURS passer à 100%
   - ✅ Exécution rapide (< 3 secondes)

2. **Test E2E** :
   - ⚠️ Nécessite l'accès au réseau PIAG
   - ⚠️ Nécessite des credentials valides
   - ⚠️ Crée et supprime des données réelles
   - ⏱️ Plus lent (15-30 secondes)

3. **Avant chaque commit** :
   - Exécutez les tests mockés (100% requis)
   - Si possible, exécutez le test E2E
   - Vérifiez la couverture ≥ 80%

---

## 🎯 Commande Recommandée pour CI/CD

```bash
# Commande unique : Mock + E2E (skip si pas de config)
poetry run pytest \
  tests/unit/piag/commands/test_piag_collection_list.py \
  tests/unit/piag/core/test_piag_client.py \
  tests/integration/test_piag_e2e_workflow.py \
  --cov=app.piag \
  --cov-report=term \
  --cov-report=html \
  --cov-fail-under=80 \
  -v

# Vérifie :
# ✅ Tests mockés passent à 100%
# ✅ Test E2E (si config disponible)
# ✅ Couverture ≥ 80%
```

**Code de sortie** :
- `0` : Tout est OK
- `!= 0` : Tests échoués OU couverture < 80%

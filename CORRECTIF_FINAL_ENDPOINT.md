# Correctif Final - Endpoint Chunks

**Date** : 2026-03-19 après premier test
**Problème** : L'endpoint chunks contient toujours `{collection_id}`

---

## 🔴 Problème Identifié

L'URL générée était :
```
/rag/api/v1/collections/%7Bcollection_id%7D/documents/9b94065c-d395-4832-bac9-d4032ccbcdf5/chunks
```

`%7Bcollection_id%7D` = `{collection_id}` non remplacé

---

## 🔍 Cause Racine

### Problème 1 : Mauvais chemin de lecture (CRITIQUE)

**Fichier** : `src/app/piag/core/config.py` ligne 163

**Avant** :
```python
endpoints = cfg.get('endpoints', {})  # ❌ Cherche à la racine
```

La configuration est structurée comme :
```yaml
piag:
  rag:
    endpoints:
      document_chunks: "/api/v1/documents/{document_id}/chunks"
```

Mais le code cherchait à `endpoints` au niveau racine, donc **il utilisait toujours les valeurs par défaut hardcodées**.

**Après** :
```python
# Chercher dans la nouvelle structure piag.rag.endpoints
endpoints = cfg.get('piag', {}).get('rag', {}).get('endpoints', {})
```

---

### Problème 2 : Valeur par défaut incorrecte

**Fichier** : `src/app/piag/core/config.py` ligne 172

**Avant** :
```python
'document_chunks': '/api/v1/collections/{collection_id}/documents/{document_id}/chunks',
```

**Après** :
```python
'document_chunks': '/api/v1/documents/{document_id}/chunks',  # Pas de collection_id selon la doc API
```

---

## ✅ Corrections Appliquées

1. ✅ Lecture des endpoints depuis `piag.rag.endpoints`
2. ✅ Correction de la valeur par défaut hardcodée

---

## 🚀 Test

**Relancer** :
```bash
python test_piag_rag_e2e.py --config config\piag.yaml
```

**URL attendue maintenant** :
```
/rag/api/v1/documents/9b94065c-d395-4832-bac9-d4032ccbcdf5/chunks
```

✅ Sans `{collection_id}` !

---

## 📊 Impact

Cette correction affecte **tous les appels à `get_endpoint()`** :
- ✅ Utilise maintenant la config YAML correctement
- ✅ Les fallbacks sont corrigés
- ✅ Plus de problème avec `{collection_id}` non remplacé

---

**Les correctifs sont appliqués. Relancez les tests !** 🎯

# Correctif - Timeout Configurable pour Traitement Documents

**Date** : 2026-03-19
**Objectif** : Rendre le délai d'attente configurable dans YAML

---

## ✅ Modifications Appliquées

### 1. Ajout du Paramètre dans config/piag.yaml

**Fichier** : `config/piag.yaml` (ligne ~118)

```yaml
upload:
  # Délai d'attente après upload (en secondes) pour le traitement asynchrone
  # Le serveur doit générer les chunks et indexer le document
  processing_delay: 20

  # Types MIME autorisés
  allowed_mime_types:
    - "application/pdf"
    - "text/plain"
    # ...
```

**Avantages** :
- ✅ Paramètre centralisé
- ✅ Modifiable sans toucher au code
- ✅ Valeur par défaut : 20 secondes
- ✅ Ajustable selon l'environnement (dev/preprod/prod)

---

### 2. Lecture du Paramètre dans le Test

**Fichier** : `test_piag_rag_e2e.py` (ligne 252-256)

**Avant** :
```python
print("  ⏳ Attente du traitement du document (10 secondes)...")
time.sleep(10)  # Hardcodé
```

**Après** :
```python
# Lecture du délai depuis la configuration
processing_delay = config.get('piag', {}).get('rag', {}).get('upload', {}).get('processing_delay', 20)
print(f"  ⏳ Attente du traitement du document ({processing_delay} secondes)...")
logging.info(f"Attente du traitement du document ({processing_delay}s)...")
time.sleep(processing_delay)
```

**Comportement** :
- Lit `piag.rag.upload.processing_delay` depuis la config
- Utilise 20 secondes par défaut si non défini
- Affiche le délai dans les logs

---

### 3. Correction Format Réponse Chunks

**Fichier** : `test_piag_rag_e2e.py` (ligne 286-299)

**Problème** : L'API retourne une liste `[]` directement, pas `{"chunks": []}`

**Solution** :
```python
# L'API peut retourner soit une liste directe, soit un dict avec clé 'chunks'
if isinstance(chunks, list):
    chunks_list = chunks
elif isinstance(chunks, dict):
    chunks_list = chunks.get('chunks', [])
else:
    chunks_list = []

num_chunks = len(chunks_list)
```

**Avantages** :
- ✅ Compatible avec les deux formats
- ✅ Robuste face aux changements d'API
- ✅ Pas de crash sur format inattendu

---

## 📋 Configuration Recommandée Selon Environnement

### Développement Local
```yaml
processing_delay: 5  # Rapide pour les tests
```

### Préprod (actuel)
```yaml
processing_delay: 20  # Recommandé
```

### Production
```yaml
processing_delay: 30  # Plus prudent
```

### Réseau Lent
```yaml
processing_delay: 60  # Très conservateur
```

---

## 🚀 Test

**Relancer** :
```bash
python test_piag_rag_e2e.py --config config\piag.yaml
```

**Résultat attendu** :
```
✓ Document uploadé: xxx-xxx-xxx
  Fichier: test_document.txt
  ⏳ Attente du traitement du document (20 secondes)...
✓ X chunk(s) récupéré(s)
  Chunk 1: Ceci est un document de test...
```

---

## 🎯 Avantages de Cette Approche

1. **Flexibilité** : Ajustable sans recompilation
2. **Documentation** : Valeur visible dans la config
3. **Environnements** : Différentes valeurs dev/prod
4. **Debugging** : Logs affichent la valeur utilisée
5. **Maintenance** : Paramètre centralisé

---

## 📝 Notes

- Le délai de 20s est un bon compromis pour la préprod
- Peut être augmenté si les chunks sont encore vides
- Peut être réduit en environnement local plus rapide
- Les logs indiquent toujours le délai utilisé

---

**Les correctifs sont appliqués. Relancez les tests !** 🎯

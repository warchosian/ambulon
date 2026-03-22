# Tests End-to-End PIAG

Ce dossier contient les tests de bout en bout pour les API RAG et CHAT de PIAG.

## 📋 Fichiers de test

- **`test_piag_rag_e2e.py`** - Test complet de l'API RAG
- **`test_piag_chat_e2e.py`** - Test complet de l'API CHAT
- **`test_piag_all.py`** - Lance tous les tests et génère un rapport

## 🚀 Lancement des tests

### Prérequis

1. **Installation des dépendances** :
   ```bash
   pip install -r requirements_tests_e2e.txt
   ```
   Ou individuellement :
   ```bash
   pip install pyyaml requests
   ```

2. **Configuration** : Assurez-vous que `config/piag.yaml` est correctement configuré avec vos tokens

3. **Variables d'environnement** (alternative à la config) :
   ```bash
   export PIAG_RAG_API_TOKEN="votre-token-rag"
   export PIAG_CHAT_API_TOKEN="votre-token-chat"
   export PIAG_RAG_PROJECT_ID="votre-project-id"
   ```

### Lancer tous les tests

```bash
# Tous les tests
python test_piag_all.py

# Avec un fichier de config spécifique
python test_piag_all.py --config config/piag.yaml

# Uniquement RAG
python test_piag_all.py --skip-chat

# Uniquement CHAT
python test_piag_all.py --skip-rag
```

### Lancer un test individuel

```bash
# Test RAG uniquement
python test_piag_rag_e2e.py

# Test CHAT uniquement
python test_piag_chat_e2e.py
```

## 📊 Résultats des tests

Tous les résultats sont sauvegardés dans le répertoire `test_output/` :

```
test_output/
├── rag/
│   └── 20260319_143025/          # Timestamp du test
│       ├── logs/
│       │   └── test_rag_e2e_20260319_143025.log
│       └── responses/
│           ├── 00_config_*.json
│           ├── 01_list_collections_*.json
│           ├── 02_create_collection_*.json
│           ├── 03_upload_document_*.json
│           ├── 04_list_documents_*.json
│           ├── 05_get_chunks_*.json
│           └── 06_search_*.json
└── chat/
    └── 20260319_143128/          # Timestamp du test
        ├── logs/
        │   └── test_chat_e2e_20260319_143128.log
        └── responses/
            ├── 00_config_*.json
            ├── 01_apikey_info_*.json
            ├── 02_basic_query_*.json
            ├── 03_completion_*.json
            └── 04_chat_with_context_*.json
```

### Fichiers générés

- **`logs/*.log`** : Logs détaillés avec toutes les requêtes HTTP, réponses, erreurs
- **`responses/*.json`** : Réponses JSON brutes de chaque appel API pour analyse

## 🔍 Débuggage

### Analyser les logs

```bash
# Voir le dernier test RAG
cat test_output/rag/*/logs/*.log

# Chercher les erreurs
grep -i error test_output/rag/*/logs/*.log
grep -i error test_output/chat/*/logs/*.log
```

### Analyser les réponses JSON

```bash
# Voir la config utilisée
cat test_output/rag/*/responses/00_config_*.json

# Voir les résultats de recherche
cat test_output/rag/*/responses/06_search_*.json

# Voir les réponses du chat
cat test_output/chat/*/responses/02_basic_query_*.json
```

## 📝 Ce que teste chaque script

### Test RAG (`test_piag_rag_e2e.py`)

1. **List Collections** - Liste les collections existantes
2. **Create Collection** - Crée une collection de test
3. **Upload Document** - Upload un document texte de test
4. **List Documents** - Liste les documents de la collection
5. **Get Chunks** - Récupère les chunks du document
6. **Search** - Effectue 3 recherches sémantiques
7. **Cleanup** - Supprime le document et la collection

### Test CHAT (`test_piag_chat_e2e.py`)

1. **API Key Info** - Récupère les infos de l'API key (budget, dépenses)
2. **Basic Query** - Pose 3 questions simples au modèle
3. **Completion** - Test l'endpoint legacy `/completions`
4. **Chat with Context** - Test le chat avec des chunks de contexte simulés

## ⚙️ Configuration pour réseau externe

Si vous testez hors du réseau habituel :

1. **Vérifiez les URLs** dans `config/piag.yaml` :
   ```yaml
   piag:
     rag:
       api:
         base_url: "https://preprod.api.piag.e2.rie.gouv.fr/rag/"
     chat:
       api:
         base_url: "https://preprod.api.piag.e2.rie.gouv.fr/v1/chat/completions"
   ```

2. **Augmentez les timeouts** si le réseau est lent :
   ```yaml
   piag:
     rag:
       api:
         timeout: 120  # 2 minutes au lieu de 30s
     chat:
       api:
         timeout: 120
   ```

3. **Activez le debug maximal** dans `config/piag.yaml` :
   ```yaml
   piag:
     rag:
       logging:
         enable_debug: true
         log_requests: true
         log_responses: true
   ```

## 🐛 Problèmes courants

### Token invalide ou expiré

```
❌ ERREUR: Token API RAG non trouvé
```

**Solution** : Vérifiez que le token est bien défini :
- Dans `config/piag.yaml` sous `piag.rag.security.token`
- Ou via variable d'env `PIAG_RAG_API_TOKEN`

### Timeout de connexion

```
Erreur API: ReadTimeout
```

**Solution** : Augmentez le timeout dans `config/piag.yaml` ou avec `--timeout`

### URL incorrecte

```
Erreur API: 404 Not Found
```

**Solution** : Vérifiez les URLs dans `config/piag.yaml`

### Project ID manquant (RAG seulement)

```
❌ ERREUR: Project ID non trouvé
```

**Solution** : Définissez `PIAG_RAG_PROJECT_ID` ou ajoutez-le dans `config/piag.yaml`

## 📧 Partage des résultats

Pour partager les résultats avec l'équipe :

```bash
# Créer une archive des résultats
cd test_output
tar -czf piag_tests_$(date +%Y%m%d_%H%M%S).tar.gz rag/ chat/

# Ou sur Windows
tar -czf piag_tests_%date:~-4,4%%date:~-7,2%%date:~-10,2%.tar.gz rag chat
```

L'archive contiendra tous les logs et réponses JSON pour analyse.

## ✅ Codes de retour

- **0** : Tous les tests ont réussi
- **1** : Au moins un test a échoué

Utilisez le code de retour dans vos scripts CI/CD :

```bash
python test_piag_all.py
if [ $? -eq 0 ]; then
    echo "Tests OK"
else
    echo "Tests KO"
    exit 1
fi
```

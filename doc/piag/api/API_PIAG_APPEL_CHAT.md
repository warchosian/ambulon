Voici le contenu complet dans un fichier Markdown :

```markdown
# API PIAG - Appels CHAT

> **Phase d'expérimentations**
> L'offre API PIAG est en cours de développement

## Appels API supportés

> **Note**
> Remplacer dans les requêtes `"sk-xxxxx"` par une apiKey valide

---

### Récupérer des informations sur une "apikey" (max_budget, spend)

**Endpoint :** `apikey/info`

```bash
curl -X GET \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-xxxxx"
```

---

### Conversation avec réponses directes

**Endpoint :** `chat/completions`

```bash
curl -X POST https://preprod.api.piag.e2.rie.gouv.fr/v1/chat/completions \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer sk-xxxxx" \
     -d '{
          "model": "mte-api-piag-mistral-medium-latest",
          "messages": [
            {
              "role": "user",
              "content": "bonjour"
            }
          ]
     }'
```

---

### Conversation avec réponses en streaming

**Endpoint :** `chat/completions` avec paramètre `"stream"`

```bash
curl -X POST https://preprod.api.piag.e2.rie.gouv.fr/v1/chat/completions \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer sk-xxxxx" \
     -d '{
          "model": "mte-api-piag-mistral-medium-latest",
          "messages": [
            {
              "role": "user",
              "content": "bonjour"
            }
          ],
          "stream": true
     }'
```

---

### Complétion de texte

**Endpoint :** `completions`

```bash
curl -X POST https://preprod.api.piag.e2.rie.gouv.fr/v1/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-xxxxx" \
  -d '{
    "model": "mte-api-piag-mistral-medium-latest",
    "prompt": "Bonjour",
    "max_tokens": 50,
    "temperature": 0.7
  }'
```

---

## Informations générales

| Élément | Valeur |
|---------|--------|
| **URL de base** | `https://preprod.api.piag.e2.rie.gouv.fr/v1/` |
| **Modèle utilisé** | `mte-api-piag-mistral-medium-latest` |
| **Environnement** | Préproduction |
```

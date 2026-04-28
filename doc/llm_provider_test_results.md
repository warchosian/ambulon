# LLM Provider Test Results

**Date:** 2026-04-27  
**Test:** Single document generation (sireines app, ccf prompt)

## Résumé

| Provider | Status | Details |
|----------|--------|---------|
| `cloud_gemini` | ✅ **SUCCÈS** | Génération réussie en 47.4s (504 caractères) |
| `cloud_claude` | ❌ Erreur | Solde API insuffisant |
| `cloud_kimi` | ❌ Erreur | Authentification invalide (clé expirée) |
| `cloud_deepseek_v4` | ❌ Erreur | URL mal formée (double endpoint) |
| `cloud_glm` | ❌ Erreur | Clé API manquante |
| `cloud_qwen` | ⏳ Non testé | |

## Détails

### ✅ cloud_gemini - SUCCÈS

**Résultat:** Génération réussie  
**Temps:** 47.4 secondes  
**Taille du document:** 504 caractères  
**Modèle:** `gemini-2.5-flash`

**Notes:**
- Le serveur Gemini a d'abord retourné une erreur 503 (haute demande)
- Le retry automatique après 2 secondes a fonctionné
- Clé API valide et fonctionnelle

### ❌ cloud_claude - Erreur

**Statut:** 400 Bad Request  
**Raison:** Solde API insuffisant  
**Modèle:** `claude-3-haiku-20240307`

```
Your credit balance is too low to access the Anthropic API. 
Please go to Plans & Billing to upgrade or purchase credits.
```

**Action requise:** Ajouter des crédits au compte Anthropic

### ❌ cloud_kimi - Erreur

**Statut:** 401 Unauthorized  
**Raison:** Authentification invalide  
**Modèle:** `moonshot-v1-128k`

```
Invalid Authentication
```

**Action requise:** Vérifier/renouveler la clé API Kimi

### ❌ cloud_deepseek_v4 - Erreur

**Statut:** 404 Not Found  
**Raison:** Double endpoint dans l'URL  
**Modèle:** `deepseek-v4-flash`

```
https://api.deepseek.com/chat/completions/chat/completions
```

**Problème identifié:** L'URL contient un endpoint dupliqué. Le provider openai_compatible ajoute "/chat/completions" mais la base_url en a déjà une.

**Action requise:** Corriger la base_url dans la config

### ❌ cloud_glm - Erreur

**Statut:** API key non trouvée  
**Raison:** La clé GLM_API_KEY n'est pas fournie  
**Modèle:** `glm-5.1-cloud`

**Action requise:** Définir la clé API GLM ou fournir une clé valide

## Recommandations

1. **Immédiat:** Utiliser `cloud_gemini` (✅ Fonctionne actuellement)
2. **À corriger:** 
   - Fix base_url pour cloud_deepseek_v4 (retirer le double endpoint)
   - Ajouter clés API valides pour GLM
   - Renouveler clé Kimi
   - Ajouter crédits à Anthropic si cloud_claude est préféré
3. **À tester:**
   - cloud_qwen (possible alternative)
   - cloud_chatgpt (si clé OpenAI disponible)

## Conclusion

**Provider recommandé:** `cloud_gemini` (✅ SUCCÈS, 47.4s)

C'est le seul provider cloud_ qui fonctionne actuellement et offre une génération de qualité.

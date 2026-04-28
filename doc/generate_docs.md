 # Avec un prompt spécifique
  ambulon llm-generate-docs --app sireines --prompt dex --provider local

  ---
  📝 Providers Testés

  | Provider       | Status        | Raison                          |
  |----------------|---------------|---------------------------------|
  | local (Ollama) | ✅ FONCTIONNE | Modèle llama3.1:8b disponible   |
  | alibaba        | ❌ Échec      | Clé API invalide (401)          |
  | kimi           | ❌ Échec      | Authentification invalide (401) |
  | claude         | ❌ Échec      | Solde insuffisant (400)         |
  | gemini         | ❌ Échec      | Modèle non trouvé (404)         |

  ---
  💡 Recommandation

  Utilisez le provider local pour vos tests :

  ambulon llm-generate-docs --app sireines --provider local
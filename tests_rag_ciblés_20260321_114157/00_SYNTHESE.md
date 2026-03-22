# Synthèse des Tests RAG - Questions Ciblées

**Date**: 2026-03-21 11:46:26

**Collection**: PNM3_SIREINES

**Objectif**: Tester le RAG avec des questions sur des détails spécifiques impossibles à deviner

## 📊 Statistiques Globales

- **Total de questions**: 8
- **Tests réussis**: 8/8
- **Taux de réussite**: 100.0%

## 📈 Métriques RAG (Moyennes)

- **Chunks trouvés par question**: 5.8
- **Sources documentaires par question**: 3.9
- **Différence de longueur (avec RAG - sans RAG)**: -4101 caractères
- **Amélioration des détails techniques**: 37.5% des cas
- **🎯 Utilisation effective des chunks**: 0.0%

### 💡 Métrique Clé : Utilisation Effective des Chunks

Cette métrique mesure **si les informations des chunks sont réellement utilisées** dans la réponse générée. Elle vérifie combien de termes techniques et concepts présents dans les chunks se retrouvent dans la réponse avec RAG.

**Score actuel**: 0.0%

❌ Les chunks sont **peu utilisés**. Le contexte n'est pas bien intégré dans les réponses.

## 🎯 Verdict

❌ **Le RAG semble peu efficace** : Seulement 38% des réponses montrent une amélioration. Vérifier la qualité des documents indexés.


## 📋 Détail des Tests

| ID | Catégorie | Chunks | Sources | Termes sans/avec | Utilisation | Amélioration | Rapport |
|---|---|---|---|---|---|---|---|
| Q1 | Composants Java | 5 | 3 | 6/2 | 0% | ⚠️ | [Voir](./q1_rapport.md) |
| Q2 | Vulnérabilités CVE | 7 | 5 | 2/3 | 0% | ✅ | [Voir](./q2_rapport.md) |
| Q3 | Configuration technique | 5 | 4 | 6/3 | 0% | ⚠️ | [Voir](./q3_rapport.md) |
| Q4 | Décisions architecturales | 5 | 5 | 3/9 | 0% | ✅ | [Voir](./q4_rapport.md) |
| Q5 | Sécurité STRIDE | 7 | 4 | 3/2 | 0% | ⚠️ | [Voir](./q5_rapport.md) |
| Q6 | ISO 25010 | 7 | 5 | 4/4 | 0% | ⚠️ | [Voir](./q6_rapport.md) |
| Q7 | Modèle C4 Level 3 | 5 | 2 | 4/2 | 0% | ⚠️ | [Voir](./q7_rapport.md) |
| Q8 | Dépendances Maven | 5 | 3 | 4/7 | 0% | ✅ | [Voir](./q8_rapport.md) |

**Légende** :
- **Termes** : nombre de termes techniques trouvés (sans RAG / avec RAG)
- **Utilisation** : % de termes des chunks effectivement utilisés dans la réponse


## Questions Testées

### Q1: Composants Java

**Question**: Quel est le rôle exact de la classe DossierRechercheMotsClefsAction dans SIREINES ?

**Top-K**: 5

**Status**: ✅ Réussi

**Rapport détaillé**: [q1_rapport.md](./q1_rapport.md)

---

### Q2: Vulnérabilités CVE

**Question**: Quelles sont les vulnérabilités CVE identifiées pour le composant ExtractionsServicesImpl de SIREINES ?

**Top-K**: 7

**Status**: ✅ Réussi

**Rapport détaillé**: [q2_rapport.md](./q2_rapport.md)

---

### Q3: Configuration technique

**Question**: Quelle version exacte d'Elasticsearch est utilisée dans SIREINES et comment est-elle configurée en mode embarqué ?

**Top-K**: 5

**Status**: ✅ Réussi

**Rapport détaillé**: [q3_rapport.md](./q3_rapport.md)

---

### Q4: Décisions architecturales

**Question**: Pourquoi SIREINES utilise-t-il le Vertigo Framework et quelles sont ses responsabilités exactes ?

**Top-K**: 5

**Status**: ✅ Réussi

**Rapport détaillé**: [q4_rapport.md](./q4_rapport.md)

---

### Q5: Sécurité STRIDE

**Question**: Quelles vulnérabilités STRIDE ont été identifiées pour le module CerbereUtil + SireinesSessionFilter ?

**Top-K**: 7

**Status**: ✅ Réussi

**Rapport détaillé**: [q5_rapport.md](./q5_rapport.md)

---

### Q6: ISO 25010

**Question**: Quels sont les critères ISO 25010 spécifiques définis pour SIREINES avec leurs valeurs cibles mesurables ?

**Top-K**: 7

**Status**: ✅ Réussi

**Rapport détaillé**: [q6_rapport.md](./q6_rapport.md)

---

### Q7: Modèle C4 Level 3

**Question**: Quels sont les composants internes détaillés du service SvcExtr dans le diagramme C4 Component de SIREINES ?

**Top-K**: 5

**Status**: ✅ Réussi

**Rapport détaillé**: [q7_rapport.md](./q7_rapport.md)

---

### Q8: Dépendances Maven

**Question**: Quelles sont les dépendances Maven listées dans le pom.xml de sireines-web avec leurs versions exactes ?

**Top-K**: 5

**Status**: ✅ Réussi

**Rapport détaillé**: [q8_rapport.md](./q8_rapport.md)

---

## Recommandations

Pour chaque rapport détaillé, comparez:

1. **Précision**: La réponse avec RAG contient-elle des détails spécifiques ?
2. **Sources**: Les chunks proviennent-ils des bons documents ?
3. **Termes techniques**: Retrouve-t-on les noms de classes, CVE, versions exactes ?
4. **Différence**: Y a-t-il une vraie différence entre réponse avec/sans RAG ?

**Verdict attendu**: Si le RAG fonctionne bien, la réponse AVEC RAG devrait contenir
des détails spécifiques impossibles à deviner par le modèle seul.


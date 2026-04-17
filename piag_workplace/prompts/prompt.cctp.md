# Prompt pour la génération d'un CCTP — Cahier des Clauses Techniques Particulières

Tu es un expert en marchés publics informatiques et rédacteur de clauses techniques. À partir du cadre réglementaire du **Code de la commande publique** et des référentiels de l'État français (**RGS, SSI, RGPD, RGI**), tu dois produire un **Cahier des Clauses Techniques Particulières (CCTP)** complet, contractuel et conforme aux exigences des marchés publics.

Le document doit être autoporté, prêt à être intégré dans un dossier de consultation des entreprises (DCE), sans dépendances externes, et sans aucune hypothèse ni donnée externe.

## Consignes générales

- Utilise exclusivement le format **Markdown**.
- Rédige des clauses **claires, mesurables, vérifiables** et **sans ambiguïté**.
- Respecte le vocabulaire réglementaire des marchés publics.
- Distingue les obligations de moyen et les obligations de résultat.
- Intègre les référentiels de sécurité de l'État (RGS, ANSSI) si applicable.
- Le document a une **valeur contractuelle** : sois précis et exhaustif.

## Structure obligatoire du CCTP

1. **Objet du marché**
   - Définition précise de l'objet (fourniture, prestation de services, etc.).
   - Références au CCF associé (séparer le fonctionnel du technique).
   - Périmètre exact des prestations attendues.

2. **Description technique détaillée**
   - Spécifications fonctionnelles minimales (références au CCF).
   - Spécifications techniques obligatoires (impératif).
   - Spécifications techniques souhaitées (souhaitable, noté).
   - Spécifications techniques optionnelles (facultatif).

3. **Architecture et conception**
   - Contraintes architecturales imposées.
   - Standards et normes obligatoires (ISO, IEEE, W3C, etc.).
   - Exigences d'interopérabilité et de portabilité.
   - Patterns et frameworks autorisés ou imposés.

4. **Exigences de sécurité** (RGS, ANSSI)
   - Niveau de sécurité requis (RGS basique, RGS renforcé).
   - Authentification et contrôle d'accès.
   - Chiffrement des données (en transit et au repos).
   - Traçabilité et journalisation des événements de sécurité.
   - Conformité RGPD pour les données personnelles.

5. **Interfaces et intégrations**
   - Liste des systèmes existants à interfacer.
   - Spécifications techniques des interfaces (protocoles, formats).
   - Modalités de recette des interfaces.

6. **Environnements et infrastructure**
   - Contraintes d'hébergement (on-premise, cloud, souveraineté).
   - Exigences de haute disponibilité et PRA/PCA.
   - Contraintes réseau et sécurité périmètrique.
   - Spécifications des environnements (développement, recette, production).

7. **Qualité et conformité**
   - Référentiels de qualité applicables (ISO 9001, ISO 25010).
   - Exigences de maintenabilité (documentation, code source).
   - Exigences de performance (temps de réponse, disponibilité).
   - Compatibilité et accessibilité (RGAA si applicable).

8. **Documentation et formation**
   - Liste des documents à fournir (DAT, documentation utilisateur, admin).
   - Formats et standards de documentation.
   - Programme de formation des utilisateurs et administrateurs.

9. **Tests et recette**
   - Stratégie de recette et critères d'acceptation.
   - Types de tests obligatoires (unitaires, intégration, charge, sécurité).
   - Modalités de la recette fonctionnelle et technique.
   - Gestion des anomalies et recette avec réserves.

10. **Maintenance et support**
    - Niveaux de support (hotline, support technique).
    - Délais d'intervention et de correction (GTR/GTD).
    - Engagements de disponibilité (SLA).
    - Conditions de la garantie et maintenance évolutive.

11. **Livrables et planning**
    - Liste détaillée des livrables attendus.
    - Format et modalités de livraison.
    - Jalons du projet et échéances.
    - Pénalités de retard (si applicable).

12. **Contraintes légales et réglementaires**
    - Propriété intellectuelle et droits d'auteur.
    - Licences des composants et logiciels tiers.
    - Protection des données personnelles (RGPD).
    - Archivage et conservation des données.

13. **Critères de sélection des offres**
    - Pondération des critères techniques (souvent sur 100 ou 60-40).
    - Modalités de notation et grille d'évaluation.
    - Attendus pour chaque critère (excellent, satisfaisant, insuffisant).

14. **Annexes contractuelles**
    - Glossaire.
    - Références normatives.
    - Modèles de documents à remplir par le candidat.

## Règles de rédaction des clauses

- Utiliser impérativement le conditionnel pour les obligations : *"Le prestataire devra..."*, *"La solution devra permettre..."*
- Quantifier chaque exigence quand c'est possible : temps de réponse, taux de disponibilité, délais.
- Éviter les formulations floues : remplacer *"rapide"* par *"inférieur à X secondes"*, *"suffisant"* par des chiffres.
- Distinguer clairement :
  - **Obligations de résultat** : *"Le système doit garantir une disponibilité de 99,9%"*
  - **Obligations de moyen** : *"Le prestataire doit mettre en œuvre une surveillance 24/7"*
- Préciser les modalités de vérification et de preuve pour chaque exigence critique.

## Règles de forme

- Numérotation hiérarchique claire (1., 1.1, 1.1.1).
- Tableaux pour les listes structurées (exigences, critères, livrables).
- Liens internes pour la navigation entre sections.
- Pas de références externes non fournies.
- Style formel, juridique, contractuel.

## Sortie attendue

- Un seul fichier `.md`.
- Aucune mention de fichiers sources ou de prompts.
- Prêt à être intégré dans un DCE et à faire l'objet d'une consultation.

---

**Références réglementaires appliquées :**
- **Code de la commande publique** : Articles relatifs aux CCTP et DCE.
- **RGS** (Référentiel Général de Sécurité) : Niveaux basique et renforcé.
- **RGPD** : Règlement Général sur la Protection des Données.
- **Référentiel SSI de l'ANSSI** : Bonnes pratiques de sécurité.
- **RGI** (Référentiel Général d'Interopérabilité) : SI de l'État.
- **RGAA** : Référentiel Général d'Amélioration de l'Accessibilité.

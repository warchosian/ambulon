# 📄 Cahier des Spécifications Techniques (CST) – **Projet : ambulon**  
**Chemin du dépôt** : `G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon\workplace-ambulon\gitlab\ambulon`  

> **NOTE** – Le présent CST a été généré à partir des seules métadonnées du dépôt (arborescence, nom du projet et absence de code source fourni).  
> Pour le finaliser, il sera indispensable de compléter les sections marquées **« 🚧 À compléter »** avec les informations fonctionnelles (CCF), l’architecture réelle, le stack technique, les contraintes métier et les objectifs chiffrés propres au projet *ambulon*.

---

## 1️⃣ Introduction et contexte qualité

| Élément | Description |
|---|---|
| **Objectif général** | Définir les exigences de qualité logicielle du produit *ambulon* conformément à la norme **ISO/IEC 25010 : 2023** et garantir la traçabilité entre exigences fonctionnelles (CCF) et critères de qualité. |
| **Contexte métier** | 🚧 À compléter : description du domaine d’activité (ex. : service d’urgence médicale, plateforme de suivi de patients, etc.). |
| **Contexte technique** | 🚧 À compléter : architecture cible (monolithique, micro‑services, serverless…), environnements d’exécution, contraintes d’infrastructure (cloud, on‑prem, edge…). |
| **Références aux exigences fonctionnelles (CCF)** | Voir **Annexe A – Matrice CCF ↔ Qualité** (à alimenter). |
| **Méthodologie d’évaluation de la qualité** | - **Revues de conception** (architecturales & détaillées) <br> - **Analyse statique** (SonarQube, ESLint, PMD…) <br> - **Tests automatisés** (unitaires, intégration, performance, sécurité) <br> - **Mesure en production** (APM, logs, métriques d’incidents) <br> - **Audits de conformité** (RGAA, OWASP ASVS, RGS…) |

---

## 2️⃣ Modèle de qualité ISO / IEC 25010 : 2023  

```
                    ┌─────────────────────────────────────┐
                    │     QUALITÉ DU PRODUIT LOGICIEL     │
                    └─────────────────────────────────────┘
                                        │
    ┌───────────┬───────────┬───────────┼───────────┬───────────┬───────────┬───────────┐
    ▼           ▼           ▼           ▼           ▼           ▼           ▼           ▼
┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐
│Aptitude│ │Performance│ │Compatibilité│ │Utilisabilité│ │Fiabilité│ │Sécurité│ │Maintenabilité│ │Portabilité│
│fonction│ │efficacité│ │            │ │            │ │          │ │        │ │            │ │           │
│-nelle  │ │           │ │            │ │            │ │          │ │        │ │            │ │           │
└───────┘  └───────┘  └───────┘  └───────┘  └───────┘  └───────┘  └───────┘  └───────┘
```

Chaque caractéristique est détaillée ci‑après avec ses sous‑caractéristiques, les **métriques proposées**, les **objectifs chiffrés** (à ajuster) et les **méthodes de vérification**.

---

## 3️⃣ Spécification détaillée par caractéristique

### 3.1 Aptitude fonctionnelle (Functional Suitability)

| Sous‑caractéristique | Métrique | Objectif | Méthode de mesure | Commentaire |
|---|---|---|---|---|
| **Complétude fonctionnelle** | % d’exigences fonctionnelles couvertes | **≥ [TODO %]** | Matrice de traçabilité CCF ↔ Fonctions implémentées | Nécessite la liste complète des CCF. |
| **Exactitude fonctionnelle** | Taux d’erreurs de calcul / traitement (défauts/transactions) | **≤ [TODO %]** | Tests d’acceptation automatisés, revues de code | Définir les scénarios critiques (ex. : dosage médicaments). |
| **Adéquation fonctionnelle** | Score d’évaluation utilisateur (échelle 1‑5) | **≥ [TODO /5]** | Enquêtes utilisateurs, tests d’utilisabilité | À réaliser lors de la phase de validation. |

---

### 3.2 Performance et efficacité (Performance Efficiency)

| Sous‑caractéristique | Métrique | Objectif | Méthode de mesure | Commentaire |
|---|---|---|---|---|
| **Comportement temporel** | Temps de réponse 95ᵉ percentile (s) | **≤ [TODO s]** | Tests de charge (JMeter, k6) | Scénario principal : création d’un dossier patient. |
| **Utilisation des ressources** | % CPU / RAM en charge nominale | **CPU ≤ [TODO %]**, **RAM ≤ [TODO %]** | Monitoring APM (Prometheus, Grafana) | Vérifier sur les environnements de staging. |
| **Capacité** | Nombre d’utilisateurs simultanés supportés | **≥ [TODO ]** | Tests de stress (scalabilité horizontale) | Définir le pic attendu (ex. : 2000 UCC). |

---

### 3.3 Compatibilité (Compatibility)

| Sous‑caractéristique | Métrique | Objectif | Méthode de mesure | Commentaire |
|---|---|---|---|---|
| **Cohérence** | Conformité aux standards (ex. : HL7, FHIR, ISO 20022) – Oui/Non | **100 %** | Analyse de spécifications, tests d’interopérabilité | Liste des standards à valider. |
| **Interopérabilité** | Nombre de formats / API supportés | **≥ [TODO]** | Tests d’échange de messages, contrats OpenAPI | Ex. : JSON, XML, CSV, DICOM. |

---

### 3.4 Utilisabilité (Usability)

| Sous‑caractéristique | Métrique | Objectif | Méthode de mesure | Commentaire |
|---|---|---|---|---|
| **Appréhensibilité** | Temps de formation (h) pour tâches basiques | **≤ [TODO h]** | Sessions de formation, questionnaires | Cible : 1 h pour infirmier·e. |
| **Apprenabilité** | Taux de réussite sans formation (%) | **≥ [TODO %]** | Tests utilisateurs (scenario‑based) | |
| **Opérabilité** | Nombre d’actions (clics) pour tâche standard | **≤ [TODO]** clics pour *Créer un patient* | Observation, enregistrement vidéo | |
| **Esthétique de l’interface** | Score SUS (System Usability Scale) | **≥ 68/100** | Questionnaire SUS | |
| **Accessibilité** | Niveau de conformité WCAG 2.1 (A/AA/AAA) | **AA minimum** | Audits automatisés (axe‑core) + revue manuelle | |

---

### 3.5 Fiabilité (Reliability)

| Sous‑caractéristique | Métrique | Objectif | Méthode de mesure | Commentaire |
|---|---|---|---|---|
| **Maturité** | Densité de défauts (défauts/KLOC) | **≤ [TODO]** | Analyse des tickets, SonarQube | |
| **Disponibilité** | % de temps de disponibilité (Uptime) | **≥ 99,9 %** | Monitoring (SLM) | Objectif SLA. |
| **Tolérance aux fautes** | Temps de récupération (RTO) | **≤ [TODO min]** | Tests de basculement, chaos engineering | |
| **Récupérabilité** | Point de récupération (RPO) | **≤ [TODO min]** | Tests de restauration de bases de données | |

---

### 3.6 Sécurité (Security)

| Sous‑caractéristique | Métrique | Objectif | Métrode de mesure | Commentaire |
|---|---|---|---|---|
| **Confidentialité** | Score d’audit (ex. : OWASP ASVS) | **≥ [TODO]** | Audits externes, scans de vulnérabilités (OWASP ZAP, Snyk) | |
| **Intégrité** | Présence de contrôles d’intégrité (Oui/Non) | **Oui** | Revue de code, signatures numériques | |
| **Non‑répudiation** | Journalisation des actions sensibles (Oui/Non) | **Oui** | Log centralisé, audit trails immutable | |
| **Responsabilité** | Couverture du traçage d’audit (%) | **≥ [TODO %]** | Analyse des logs, corrélation SIEM | |
| **Authenticité** | Méthodes d’authentification implémentées (ex. : MFA, OIDC) | **≥ 2 méthodes** | Tests d’authentification, revue de configuration | |

---

### 3.7 Maintenabilité (Maintainability)

| Sous‑caractéristique | Métrique | Objectif | Méthode de mesure | Commentaire |
|---|---|---|---|---|
| **Modularité** | Couplage / Cohésion (Métriques SonarQube) | **Couplage faible, Cohésion forte** | Analyse statique | |
| **Réutilisabilité** | % de composants réutilisables identifiés | **≥ [TODO %]** | Inventaire du code, catalogue de services | |
| **Analysabilité** | Complexité cyclomatique moyenne | **≤ [TODO]** | SonarQube, linter | |
| **Modifiabilité** | Temps moyen de modification (jours/homme) | **≤ [TODO]** | Historique des tickets, métriques de cycle‑time | |
| **Testabilité** | Couverture de tests automatisés (%) | **≥ 80 %** | Tests unitaires + d’intégration (JaCoCo, Istanbul) | |

---

### 3.8 Portabilité (Portability)

| Sous‑caractéristique | Métrique | Objectif | Méthode de mesure | Commentaire |
|---|---|---|---|---|
| **Adaptabilité** | Nombre d’environnements supportés (OS, cloud) | **≥ [TODO]** | Tests de déploiement (Docker, Kubernetes) | |
| **Installabilité** | Temps d’installation standard (min) | **≤ [TODO]** | Scripts d’installation automatisés, CI / CD | |
| **Remplaçabilité** | Compatibilité avec formats standards (ex. : HL7 v2/v3, FHIR) | **Oui** | Tests de migration, validation de schémas | |

---

## 4️⃣ Architecture technique (esquisse)

> **⚠️ À compléter** – Le diagramme ci‑dessous doit refléter la vraie architecture du projet (micro‑services, base de données, bus d’événements, etc.).  

```mermaid
graph TD;
    A[Client (Web / Mobile)] --> B[API Gateway]
    B --> C[Service Auth]
    B --> D[Service Patient]
    B --> E[Service Scheduling]
    D --> F[(DB PostgreSQL)]
    E --> G[(DB MongoDB)]
    style A fill:#f9f,stroke:#333,stroke-width_2px;
    style B fill:#bbf,stroke:#333,stroke-width_2px
```

**Justification des choix** (exemple) :

| Décision | Impact Qualité | Raison |
|---|---|---|
| **API Gateway** | Améliore **Compatibilité** & **Sécurité** (centralisation des contrôles) | Simplifie la gouvernance des API et la traçabilité. |
| **Micro‑services** | Favorise **Modularité**, **Scalabilité**, **Portabilité** | Permet de déployer indépendamment chaque domaine fonctionnel. |
| **Base de données PostgreSQL** (transactionnelle) | Renforce **Fiabilité** & **Intégrité** | Supporte les contraintes ACID nécessaires aux dossiers patients. |
| **Base MongoDB** (documents) | Optimise **Performance** pour les logs / historiques | Lecture rapide, schéma flexible. |
| **CI/CD avec GitLab CI** | Accélère **Testabilité** & **Maintenabilité** | Pipelines automatisés, validation à chaque merge. |
| **Conteneurisation (Docker + Kubernetes)** | Améliore **Portabilité**, **Installabilité**, **Adaptabilité** | Environnements reproductibles, scaling automatisé. |

---

## 5️⃣ Stack technologique qualifié

| Couche | Technologie | Version | Raison qualité | Licence |
|---|---|---|---|---|
| **Front‑end** | React / Vue (choisir) | 18.x / 3.x | Rich UI, bonnes pratiques d’accessibilité, large communauté | MIT |
| **UI Framework** | Ant Design / Vuetify | 5.x / 3.x | Composants accessibles, thèmes personnalisables | MIT |
| **API Gateway** | Kong / Traefik | 3.x / 2.x | Gestion du routage, authentification, observabilité | Apache‑2.0 |
| **Service Auth** | Keycloak | 24.x | OpenID Connect, MFA, gestion fine des rôles | Apache‑2.0 |
| **Service Domain** | Spring Boot (Java) **ou** NestJS (Node) | 3.2.x / 10.x | Framework mature, support de tests, monitoring intégré | Apache‑2.0 |
| **Base de données** | PostgreSQL | 15.x | ACID, support JSON, réplication native | PostgreSQL Licence |
| **NoSQL** | MongoDB | 7.x | Stockage de documents semi‑structurés, haute performance | SSPL |
| **Message Broker** | Apache Kafka | 3.5.x | Découplage, résilience, haute disponibilité | Apache‑2.0 |
| **Conteneurisation** | Docker | 24.x | Portabilité, isolation, reproductibilité | Apache‑2.0 |
| **Orchestration** | Kubernetes (k8s) | 1.28.x | Autoscaling, self‑healing, multi‑cloud | Apache‑2.0 |
| **CI/CD** | GitLab CI | 16.x | Pipelines intégrées, artefacts, review‑apps | MIT |
| **Monitoring / APM** | Prometheus + Grafana | 2.50 / 10.x | Métriques temps réel, alerting, tableau de bord | Apache‑2.0 |
| **Static Analysis** | SonarQube | 10.x | Qualité du code, métriques de maintenabilité | LGPL‑3.0 |
| **Security Scanning** | OWASP ZAP, Snyk | 2.12 / 1.1200 | Détection de vulnérabilités, conformité | Apache‑2.0 / Proprietary (Free tier) |

> **⚠️ À valider** – Les versions exactes seront fixées en fonction des politiques de support LTS de l’organisation.

---

## 6️⃣ Stratégie de test et validation

| Niveau | Objectif | Outils | Métriques de succès | Commentaire |
|---|---|---|---|---|
| **Tests unitaires** | Vérifier la logique métier individuelle | JUnit / Jest | Coverage ≥ 80 % | Exécution à chaque commit. |
| **Tests d’intégration** | Valider les interactions service‑service & DB | Testcontainers, Spring Test, SuperTest | Pass ≥ 95 % | Environnements éphémères. |
| **Tests fonctionnels (E2E)** | Simuler les scénarios utilisateurs | Cypress / Playwright | SUS ≥ 68, taux de réussite ≥ 90 % | Sessions de validation avec utilisateurs finaux. |
| **Tests de performance** | Mesurer temps de réponse, charge maximale | k6, JMeter | RT ≤ [TODO] s, RPS ≥ [TODO] | Tests en pré‑production. |
| **Tests de sécurité** | Identifier vulnérabilités & conformité | OWASP ZAP, Snyk, Trivy | Aucun HIGH/CRITICAL non résolu | Scan CI + audit périodique. |
| **Tests de compatibilité** | Vérifier interopérabilité avec systèmes tiers | Postman, SOAP UI | Tous les contrats API validés | Basé sur spécifications HL7/FHIR. |
| **Tests de résilience** | Chaos engineering, basculement | Gremlin, LitmusChaos | RTO ≤ [TODO] min | Scénarios de perte de nœud. |
| **Tests d’accessibilité** | Conformité WCAG AA | axe‑core, pa11y | Score ≥ AA | Intégré dans le pipeline UI. |

**Critères d’acceptation technique** (exemple) :

- Toutes les métriques de couverture (code, tests, sécurité) dépassent les seuils définis.  
- Aucun test critique (niveau HIGH) n’est bloquant en production.  
- Les SLA de disponibilité et de performance sont satisfaits pendant la période de validation.

---

## 7️⃣ Supervision et métriques en production

| Métrique | Source | Seuil d’alerte | Action corrective |
|---|---|---|---|
| **Uptime** | Prometheus / Grafana | < 99,9 % (sur 30 j) | Escalade N2, vérification du load‑balancer |
| **Temps de réponse 95ᵉ %** | APM (Jaeger, Zipkin) | > [TODO] s | Scaling horizontal, optimisation query |
| **CPU %** | Node Exporter | > 80 % (sur 5 min) | Autoscaling, revue de code |
| **Erreur HTTP 5xx** | NGINX logs | > 0,5 % du trafic | Redémarrage service, investigation |
| **Taux de défauts (post‑release)** | Sentry / Bug tracking | > 2 défauts/semestre | Hot‑fix, rollback |
| **Score de sécurité (OWASP ZAP)** | Scan quotidien | HIGH > 0 | Patch, mise à jour dépendances |
| **Conformité WCAG** | axe‑core (CI) | < AA | Refactor UI, revue design |
| **RTO / RPO** | DR plan | RTO > [TODO] min ou RPO > [TODO] min | Basculement, restauration DB |

Les **tableaux de bord** seront publiés sur Grafana avec des panels dédiés par caractéristique (ex. : *Performance*, *Fiabilité*, *Sécurité*).

---

## 8️⃣ Documentation technique

| Livrable | Format | Responsable | Fréquence de mise à jour |
|---|---|---|---|
| **Architecture & Design** | Markdown + diagrammes (PlantUML) | Architecte | à chaque itération majeure |
| **API Specification** | OpenAPI 3.0 (YAML) + Swagger UI | Équipe API | CI‑generated, versionnée |
| **Guide de déploiement** | Markdown + scripts (Helm) | DevOps | chaque release |
| **Guide d’exploitation** | Confluence / Markdown | Ops | chaque changement d’infra |
| **Code documentation** | Javadoc / TypeDoc / ESLint comments | Développeurs | CI‑check |
| **Run‑books d’incident** | Markdown | Support | mise à jour post‑incident |
| **Matrice CCF ↔ Qualité** | Excel / Markdown table | Analyste fonctionnel | chaque sprint |

---

## 9️⃣ Gestion des dettes techniques

| Risque / Dette | Impact sur la qualité | Priorité | Plan de remboursement |
|---|---|---|---|
| **Couplage élevé entre services** | Réduit **Modularité** & **Maintenabilité** | Haute | Refactoring en version 2.0, introduction de contrats d’interface |
| **Absence de tests de charge** | Risque de **Performance** insuffisante | Moyenne | Implémenter tests k6 dès le prochain sprint |
| **Documentation API incomplet** | Freine **Compatibilité** & **Portabilité** | Haute | Générer automatiquement via SpringDoc / NestJS, revue mensuelle |
| **Vulnérabilités connues dans dépendances** | Compromet **Sécurité** | Haute | Snyk CI, mise à jour mensuelle des dépendances |
| **Manque de logs structurés** | Difficile **Responsabilité** & **Analyse d’incident** | Moyenne | Centraliser logs avec Loki, ajouter corrélation d’ID de trace |
| **Déploiement manuel de certains composants** | Limite **Installabilité** & **Adaptabilité** | Faible | Automatiser via Helm + GitOps |

> **Hypothèses** :  
> - L’équipe dispose d’au moins 2 développeurs full‑stack, 1 architecte, 1 DevOps.  
> - Le projet doit être livrable en **6 mois** (MVP) avec une **phase de stabilisation** de 2 mois.  

---

## 🔟 Annexes

### A. Matrice de traçabilité CCF ↔ Qualité (exemple)

| CCF (exigence fonctionnelle) | Caractéristique ISO 25010 | Sous‑caractéristique | Métrique associée | Objectif |
|---|---|---|---|---|
| **CF‑001** – Enregistrement d’un patient | Aptitude fonctionnelle | Complétude fonctionnelle | % exigences couvertes | ≥ 100 % |
| **CF‑002** – Authentification MFA | Sécurité | Authentivité | Méthodes d’authent. implémentées | ≥ 2 |
| **CF‑003** – Recherche patients en < 2 s | Performance | Comportement temporel | Temps de réponse 95ᵉ % | ≤ 2 s |
| **CF‑004** – Export HL7 v2 | Compatibilité | Interopérabilité | Formats supportés | HL7 v2, FHIR R4 |
| **CF‑005** – Interface accessible WCAG AA | Utilisabilité | Accessibilité | Niveau WCAG | AA |
| **CF‑006** – Sauvegarde quotidienne | Fiabilité | Récupérabilité | RPO | ≤ 24 h |
| **CF‑007** – Déploiement en 5 min | Portabilité | Installabilité | Temps d’installation | ≤ 5 min |
| **CF‑008** – Refactorisation du module de facturation | Maintenabilité | Modifiabilité | Temps moyen de changement | ≤ 2 jours |

> **⚠️ À enrichir** – La matrice doit être alimentée avec **toutes** les exigences fonctionnelles du projet *ambulon*.

---

## 📌 Conclusion

Ce CST fournit le **cadre complet** requis par la norme **ISO/IEC 25010 : 2023** afin d’assurer que le produit *ambulon* réponde aux exigences de **qualité**, de **sécurité**, de **performance** et de **maintenabilité** attendues par les parties prenantes.  

Les sections marquées **🚧 À compléter** devront être renseignées dès que les informations fonctionnelles, l’architecture détaillée et les contraintes métier seront disponibles. Une fois ces éléments fournis, le CST pourra être finalisé, validé et intégré au processus de développement (planification des sprints, CI/CD, gouvernance qualité).

---

*Document généré le 27 avril 2026 – Version 1.0*  
*Auteur : ChatGPT (modèle gpt‑4‑turbo), expert ISO 25010*
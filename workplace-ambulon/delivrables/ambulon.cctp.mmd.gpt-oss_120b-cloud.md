# Cahier des Clauses Techniques Particulières (CCTP)  
## Projet **« Ambulon »** – Marché public informatique  

> **Document** : CCTP – à intégrer dans le Dossier de Consultation des Entreprises (DCE)  
> **Version** : 1.0 – 27‑04‑2026  
> **Références réglementaires** : Code de la commande publique, RGS, ANSSI, RGPD, RGI, RGAA, ISO/IEC 27001, ISO/IEC 25010, ISO 9001, ISO 20000‑1  

---  

## 1. Objet du marché  

| N° | Description |
|---|-------------|
| 1.1 | Le présent marché a pour objet **la conception, le développement, la mise en œuvre, la recette, la mise en production, la maintenance évolutive et le support technique** de la solution logicielle **« Ambulon »** (ci‑après la « Solution »). |
| 1.2 | La Solution devra répondre aux besoins fonctionnels détaillés dans le **Cahier des Clauses Fonctionnelles (CCF)** annexé au présent CCTP. |
| 1.3 | Le périmètre du marché comprend : <br>• Analyse et spécifications détaillées ; <br>• Conception et développement ; <br>• Intégration et tests ; <br>• Déploiement en environnement de production ; <br>• Documentation complète ; <br>• Formation des utilisateurs et administrateurs ; <br>• Support technique (1ᵉʳ‑niveau et 2ᵉ‑niveau) et maintenance pendant la période contractuelle. |
| 1.4 | Le prestataire devra garantir le respect des exigences légales, réglementaires et normatives applicables à tout système d’information de l’État. |

---

## 2. Description technique détaillée  

| Niveau | Exigence | Référence |
|--------|----------|-----------|
| **2.1 Obligations minimales (obligations de résultat)** | La Solution devra implémenter **toutes les fonctions** décrites dans le CCF, avec un taux de conformité fonctionnelle de **≥ 99,5 %** lors de la recette finale. | CCF – Chap. 3 |
| **2.2 Obligations techniques obligatoires** | • Architecture micro‑services ou monolithique selon le modèle indiqué dans le CCF.<br>• Utilisation de **Java 17** (ou version supérieure) et **Spring Boot 3.x** pour le back‑end.<br>• Utilisation de **React 18** (ou version supérieure) pour le front‑end.<br>• Base de données **PostgreSQL 15** (ou version supérieure).<br>• Conteneurisation avec **Docker 24** et orchestration **Kubernetes 1.28** (ou version supérieure). | CCF – Annexes techniques |
| **2.3 Obligations techniques souhaitées (optionnelles)** | • Mise en place d’une API GraphQL en complément de l’API REST.<br>• Utilisation de **Redis** comme cache distribué.<br>• Implémentation d’un système de monitoring **Prometheus + Grafana**. | CCF – Annexes optionnelles |
| **2.4 Obligations techniques optionnelles (facultatives)** | • Intégration d’un moteur d’intelligence artificielle (ex. : LLM) pour l’aide à la décision.<br>• Support de l’authentification biométrique. | CCF – Annexes optionnelles |

---

## 3. Architecture et conception  

| Point | Exigence |
|-------|----------|
| **3.1 Contraintes architecturales** | La Solution devra être **déployable** sur une infrastructure **cloud souverain** (ex. : OVHcloud, Scaleway) ou en **on‑premise** selon la décision du maître d’ouvrage, tout en respectant le **Référentiel Général d’Interopérabilité (RGI)**. |
| **3.2 Normes et standards obligatoires** | • **ISO/IEC 27001** – Système de management de la sécurité de l’information.<br>• **ISO/IEC 25010** – Qualité du produit logiciel.<br>• **ISO 9001** – Management de la qualité.<br>• **W3C** – HTML 5, CSS 3, ARIA 1.2.<br>• **IEEE 1471/42010** – Architecture des systèmes logiciels. |
| **3.3 Interopérabilité & portabilité** | La Solution devra exposer des API **RESTful** conformes à la **norme OpenAPI 3.0** et être compatible avec les **services d’échange de données** du SI de l’État (ex. : API Gateway, ESB). |
| **3.4 Patterns & frameworks** | • Architecture **Clean Architecture** ou **Hexagonal**.<br>• Utilisation du **Framework Spring Security** pour la gestion des accès.<br>• Utilisation du **Design System** de l’État (ex. : DSFR) pour l’interface utilisateur. |

---

## 4. Exigences de sécurité (RGS, ANSSI)

| N° | Exigence | Niveau (RGS) |
|---|----------|--------------|
| **4.1 Niveau de sécurité** | La Solution devra être certifiée **RGS Renforcé** (niveau 2). | RGS 2 |
| **4.2 Authentification & contrôle d’accès** | • Authentification forte (MFA) via **SAML 2.0** ou **OpenID Connect**.<br>• Gestion des rôles et des habilitations conforme au **modèle RBAC** du SI de l’État. |
| **4.3 Chiffrement** | • Chiffrement TLS 1.3 pour toutes les communications réseau.<br>• Chiffrement AES‑256 GCM des données au repos (bases de données, backups). |
| **4.4 Traçabilité & journalisation** | • Enregistrement de **tous les événements de sécurité** (authentifications, modifications de données, appels d’API) selon la **norme ISO 27002**.<br>• Conservation des logs pendant **≥ 12 mois** avec intégrité vérifiable (hashes). |
| **4.5 Conformité RGPD** | • Mise en œuvre du **Principe de minimisation** des données.<br>• Droit d’accès, de rectification, d’effacement et de portabilité garantis via des API dédiées.<br>• Notification des violations de données dans les **72 heures** suivant la découverte. |
| **4.6 Tests de sécurité** | • **Tests d’intrusion** (pentest) selon la méthode **OWASP Testing Guide** avant mise en production.<br>• Analyse de code statique (SAST) et dynamique (DAST) à chaque itération majeure. |

---

## 5. Interfaces et intégrations  

| Interface | Système cible | Protocole / Format | Modalité de recette |
|-----------|---------------|--------------------|----------------------|
| **5.1 API REST** | Portail citoyen de l’État | HTTPS / JSON (OpenAPI 3.0) | Tests d’intégration automatisés + validation fonctionnelle par le maître d’ouvrage |
| **5.2 ESB** | Bus d’Échange de Services (ex. : MuleSoft) | SOAP / XML ou REST / JSON | Validation du schéma XSD ou du contrat OpenAPI |
| **5.3 Authentification SSO** | IAM de l’État (ex. : CAS, Keycloak) | SAML 2.0 ou OpenID Connect | Tests de flux d’authentification et de propagation des attributs |
| **5.4 Gestion des logs** | SIEM (ex. : Splunk, Elastic) | Syslog / CEF | Vérification de la conformité des champs et de la rétention |
| **5.5 Base de données** | PostgreSQL existante | JDBC / SQL | Tests de migration de schéma et de performances de requêtes |

---

## 6. Environnements et infrastructure  

| Environnement | Description | Exigences |
|---------------|--------------|-----------|
| **6.1 Développement** | Accès limité aux développeurs, réseau interne, isolation totale. | • Docker‑Compose pour le déploiement local.<br>• Accès VPN avec MFA. |
| **6.2 Recette** | Environnement de pré‑production répliquant la production (hardware, réseau, sécurité). | • Niveau de sécurité **RGS Basique**.<br>• Disponibilité **≥ 99 %** pendant les phases de tests. |
| **6.3 Production** | Hébergement sur cloud souverain ou datacenter dédié de l’État. | • **Haute disponibilité** : architecture en **cluster** avec **load‑balancing**.<br>• **PRA/PCA** : temps de récupération **≤ 2 heures**, perte de données **≤ 5 minutes**. |
| **6.4 Réseau** | Segmentation réseau selon la classification des flux (DMZ, zone interne, zone de données). | • Pare‑feu de périmètre conforme à **l’ANSSI**.<br>• VPN IPSec pour les accès distants. |
| **6.5 Infrastructure as Code (IaC)** | Déploiement automatisé via **Terraform 1.6** et **Ansible 2.15**. | • Scripts versionnés dans le dépôt Git du projet. |

---

## 7. Qualité et conformité  

| Domaine | Référentiel | Exigence |
|---------|-------------|----------|
| **7.1 Qualité logicielle** | ISO 25010 | • **Fiabilité** : taux d’erreur < 0,1 % en production.<br>• **Performance** : temps de réponse < 2 s pour 95 % des requêtes.<br>• **Sécurité** : conformité RGS 2. |
| **7.2 Maintenabilité** | ISO 9001 | • Documentation du code (Javadoc, commentaires) ≥ 80 % des classes.<br>• Livrables source remis sous forme de **repository Git** avec **branches** claires (feature, release, hotfix). |
| **7.3 Accessibilité** | RGAA 4.1 | • Conformité **≥ 90 %** aux critères de succès du RGAA.<br>• Tests d’accessibilité automatisés (axe‑core) + audit manuel. |
| **7.4 Gestion de configuration** | ITIL 4 / ISO 20000‑1 | • Utilisation d’un **CMDB** pour le suivi des actifs.<br>• Gestion des changements via processus formalisé (RFC). |

---

## 8. Documentation et formation  

| Livrable | Format | Contenu minimum |
|----------|--------|------------------|
| **8.1 Dossier d’Architecture Technique (DAT)** | PDF + diagrammes UML (PlantUML) | Architecture globale, diagrammes de composants, flux de données, diagrammes de séquence, contraintes de sécurité. |
| **8.2 Guide d’Installation & d’Exploitation** | PDF + scripts (Shell, PowerShell) | Procédures d’installation, configuration, mise à jour, sauvegarde/restauration, procédure de bascule PRA. |
| **8.3 Manuel Utilisateur** | PDF + HTML (online) | Fonctionnalités, scénarios d’usage, FAQ. |
| **8.4 Manuel Administrateur** | PDF + HTML | Gestion des comptes, paramétrage de la sécurité, monitoring, gestion des logs. |
| **8.5 Rapport de Tests** | PDF + JUnit/pytest reports | Résultats détaillés des tests unitaires, d’intégration, de charge, de sécurité. |
| **8.6 Formation** | Sessions présentielles ou distancielles (max 5 jours) + supports PPT | • Formation des **utilisateurs finaux** (2 jours).<br>• Formation des **administrateurs** (2 jours).<br>• Atelier **développeurs** (1 jour) pour la prise en main du code source. |

---

## 9. Tests et recette  

| Type de test | Objectif | Méthode | Critère d’acceptation |
|--------------|----------|---------|-----------------------|
| **9.1 Tests unitaires** | Vérifier le bon fonctionnement de chaque unité de code. | Couverture ≥ 80 % (JaCoCo, Istanbul). | Aucun test critique échoué. |
| **9.2 Tests d’intégration** | Valider les interactions entre modules et interfaces externes. | Scénarios automatisés (Postman, Karate). | Taux de succès ≥ 95 %. |
| **9.3 Tests de charge** | Garantir les performances sous charge maximale prévue (10 000 utilisateurs simultanés). | JMeter / Gatling – durée 30 min, 95 % des réponses < 2 s. | Aucun dépassement de seuils de latence. |
| **9.4 Tests de sécurité** | Détecter vulnérabilités et non‑conformités RGS. | Pentest externe (OWASP Top 10) + SAST/DAST. | Aucun risque **critical** ou **high** non‑corrigé. |
| **9.5 Tests d’acceptation fonctionnelle (UAT)** | Vérifier la conformité aux exigences fonctionnelles du CCF. | Scénarios rédigés par le maître d’ouvrage, exécutés par les utilisateurs clés. | Taux de conformité ≥ 99,5 %. |
| **9.6 Gestion des anomalies** | Traiter les défauts détectés pendant la recette. | Outil de suivi (Jira, Redmine) – priorité selon sévérité. | Toutes les anomalies **bloquantes** corrigées avant validation finale. |

---

## 10. Maintenance et support  

| Niveau | Service | Délai d’intervention | Délai de correction | SLA |
|--------|---------|----------------------|----------------------|-----|
| **10.1 Support niveau 1 (Hotline)** | Assistance téléphonique / ticketing pour incidents d’usage. | Accusé de réception ≤ 30 min. | Résolution **≤ 4 h** (critère = P1). |
| **10.2 Support niveau 2 (Technique)** | Analyse approfondie, correction de bugs, assistance aux administrateurs. | Accusé de réception ≤ 1 h. | Résolution **≤ 8 h** (P1) ou **≤ 24 h** (P2). |
| **10.3 Maintenance corrective** | Corrections de défauts (bugs) identifiés. | Conforme aux délais ci‑dessus. | Taux de disponibilité **≥ 99,9 %** du service de support. |
| **10.4 Maintenance évolutive** | Ajout de nouvelles fonctionnalités ou amélioration de performances. | Définie dans le **plan de version** (road‑map) signé par les deux parties. |
| **10.5 Garantie** | Garantie de conformité pendant **24 mois** à compter de la mise en production. | – | Couverture totale des défauts de conception et de réalisation. |
| **10.6 Reporting** | Rapport mensuel d’activités (incidents, changements, performances). | – | Livraison au plus tard le 5 du mois suivant. |

---

## 11. Livrables et planning  

| Jalons | Livrable | Date cible (JJ/MM/AAAA) | Pénalité de retard* |
|--------|----------|--------------------------|----------------------|
| **11.1** | Cadrage fonctionnel & technique (CCF + DAT) | 30/06/2026 | 0,5 % du montant du lot par jour de retard. |
| **11.2** | Prototype fonctionnel (version 0.1) | 31/08/2026 | 0,5 % du montant du lot par jour de retard. |
| **11.3** | Version bêta (tests d’intégration) | 30/11/2026 | 0,5 % du montant du lot par jour de retard. |
| **11.4** | Version finale (pré‑production) | 31/01/2027 | 0,5 % du montant du lot par jour de retard. |
| **11.5** | Mise en production & recette finale | 28/02/2027 | 0,5 % du montant du lot par jour de retard. |
| **11.6** | Livraison de la documentation complète | 15/03/2027 | 0,5 % du montant du lot par jour de retard. |
| **11.7** | Formation des utilisateurs & administrateurs | 31/03/2027 | 0,5 % du montant du lot par jour de retard. |
| **11.8** | Démarrage du support & maintenance (M1) | 01/04/2027 | – |
| *Les pénalités sont plafonnées à **10 %** du montant du lot. |

---

## 12. Contraintes légales et réglementaires  

| Domaine | Exigence | Référence |
|--------|----------|-----------|
| **12.1 Propriété intellectuelle** | Le prestataire cèdera à l’État **l’ensemble des droits patrimoniaux** sur le code source, la documentation et les livrables, conformément à l’article **L. 2122‑2** du Code de la commande publique. | CACP – Art. L2122‑2 |
| **12.2 Licences tierces** | Toutes les bibliothèques tierces devront être compatibles avec une **licence open source** autorisant une utilisation dans le secteur public (ex. : MIT, Apache 2.0, LGPL 3). Aucun composant sous licence **GPL v3** ou **propriétaire** ne pourra être intégré. | Politique DINSIC |
| **12.3 Protection des données** | Le prestataire devra mettre en œuvre les mesures techniques et organisationnelles requises par le **RGPD** (article 32) et le **Décret sur la sécurité des systèmes d’information** (2022‑101). | RGPD – Art. 32 |
| **12.4 Archivage** | Les livrables (code source, documentation, rapports de tests) devront être archivés pendant **10 ans** sur le serveur d’archivage de l’État, conformément à l’article **L. 112‑1‑1** du Code des relations entre le public et l’administration. | CRCN |
| **12.5 Conformité RGS** | La solution devra être conforme au **Référentiel Général de Sécurité** (RGS) niveau **Renforcé** et aux recommandations de l’**ANSSI** (Guide d’hardening, référentiel SSI). | RGS 2, ANSSI SSI‑2024 |
| **12.6 Accessibilité** | L’interface doit être conforme au **RGAA 4.1** et aux exigences d’accessibilité du **Décret n° 2022‑105**. | RGAA 4.1 |
| **12.7 Responsabilité civile** | Le prestataire devra souscrire une assurance responsabilité civile professionnelle couvrant les dommages liés à la réalisation du marché, avec une garantie minimale de **2 M€**. | Code des assurances |

---

## 13. Critères de sélection des offres  

| Critère | Pondération | Modalité d’évaluation | Barème (0‑5) |
|---------|-------------|-----------------------|--------------|
| **13.1 Qualité technique de la solution** (conformité aux exigences du CCTP) | 40 % | Analyse du **DAT**, démonstrations fonctionnelles, preuves de conformité RGS/ANSSI. | 5 = Conformité totale + innovations pertinentes ; 0 = Non‑conformité majeure. |
| **13.2 Méthodologie & plan projet** (planning, gouvernance, management des risques) | 20 % | Grille d’évaluation basée sur la clarté du planning, la pertinence des livrables, la gestion des risques. | 5 = Plan détaillé, risques identifiés & atténués ; 0 = Absence de plan ou risques non maîtrisés. |
| **13.3 Expérience & références** (projets similaires dans le secteur public) | 15 % | Analyse des références (3 projets de même envergure) et des certifications (ISO 27001, ISO 9001). | 5 = 3 références probantes + certifications ; 0 = Aucune référence pertinente. |
| **13.4 Capacité financière** | 10 % | Analyse du bilan, capacité à assurer la garantie de bonne exécution. | 5 = Capacité financière solide (CA > 5 M€) ; 0 = Capacité insuffisante. |
| **13.5 Prix** | 15 % | Prix global du marché (hors TVA) – analyse de la compétitivité. | 5 = Prix le plus bas dans la fourchette acceptable ; 0 = Prix > 30 % du prix moyen. |
| **Total** | **100 %** | | |

> **Notation** : chaque critère est noté sur 5 points, multiplé par sa pondération. La somme des points obtenus détermine le rang de l’offre. En cas d’égalité, le critère **qualité technique** (13.1) est déterminant.

---

## 14. Annexes contractuelles  

| Annexe | Description |
|--------|-------------|
| **A – Glossaire** | Définitions des termes techniques et juridiques utilisés dans le présent CCTP. |
| **B – Références normatives** | Liste exhaustive des normes, référentiels et textes législatifs cités (ISO 27001, RGS 2, RGAA 4.1, etc.). |
| **C – Modèle de Déclaration de Conformité** | Formulaire à compléter par le candidat attestant le respect des exigences du CCTP. |
| **D – Modèle de Plan de Gestion des Risques** | Tableau à remplir décrivant les risques identifiés, leur probabilité, impact et les mesures d’atténuation. |
| **E – Modèle de Rapport de Tests** | Structure du rapport attendu (résultats, métriques, anomalies, actions correctives). |
| **F – Modèle de Convention de Garantie** | Document contractuel détaillant les engagements de garantie et de maintenance. |

---  

*Ce CCTP a été rédigé conformément aux exigences du Code de la commande publique et aux référentiels de l’État. Il constitue une partie intégrante du DCE et possède valeur contractuelle.*
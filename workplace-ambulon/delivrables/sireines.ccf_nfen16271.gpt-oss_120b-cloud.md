# 📄 Cahier des Charges Fonctionnel (CCF) – **SIREINES**  
*Version 1.0 – 27 avril 2026*  

Conformément à la norme **NF EN 16271 :2013** (Management par la valeur – Expression fonctionnelle du besoin et cahier des charges fonctionnel), ce document décrit le besoin fonctionnel du système **SIREINES** et les exigences qui en découlent.  

---

## 1. Présentation du projet  

| Élément | Description |
|---|---|
| **Nom du projet** | SIREINES (Système d’Information de Recensement des Experts et Spécialistes) |
| **Contexte** | Application métier du **DG Développement Durable – DRI/AST4** qui recense les demandes de qualification d’experts soumises aux comités de domaine, assure le suivi de leur évolution, génère des statistiques et des courriers, et fournit des exports. |
| **Objectifs** | 1. Centraliser, sécuriser et rendre consultables les dossiers d’expertise.<br>2. Automatiser la génération de courriers et de rapports (BIRT).<br>3. Permettre l’import/export de données (CSV, Excel).<br>4. Garantir la conformité RGPD et la traçabilité des actions.<br>5. Assurer la disponibilité 24 h/24 7 j/7 (production) et la reproductibilité des livraisons (Docker/IaaS). |
| **Périmètre fonctionnel** | • Gestion des agents, dossiers, courriers, extractions, références (structures, comités, mots‑clés…)<br>• Recherche plein‑texte (Elasticsearch intégré)<br>• Génération de rapports BIRT (PDF, HTML)<br>• Import de fichiers (CSV, XML) via l’interface “Import fichier”<br>• Export CSV/Excel des listes de dossiers<br>• Authentification unique (SSO) et gestion des sessions |
| **Exclusions** | • Gestion du portefeuille d’applications tierces.<br>• Développement d’un nouveau moteur de recherche (Elasticsearch déjà fourni).<br>• Migration de la base de données hors PostgreSQL. |

---

## 2. Analyse de la valeur  

### 2.1 Fonctions de service (FS)  

| **Code** | **Fonction de service** | **Type** |
|---|---|---|
| **FS‑01** | Authentifier les usagers (login SSO) | **FP** (Fonction Principale) |
| **FS‑02** | Gérer les dossiers d’expertise (CRUD) | **FP** |
| **FS‑03** | Gérer les référentiels (structures, comités, mots‑clés, qualifications) | **FC** |
| **FS‑04** | Rechercher des dossiers (full‑text) | **FC** |
| **FS‑05** | Générer des rapports BIRT (statistiques, listes, pyramides d’âge) | **FC** |
| **FS‑06** | Importer des fichiers d’alimentation (CSV, XML) | **FC** |
| **FS‑07** | Exporter des listes (CSV, Excel) | **FC** |
| **FS‑08** | Envoyer des courriers électroniques automatisés | **FC** |
| **FS‑09** | Administrer les paramètres de l’application (version, logs, paramètres RGPD) | **FC** |
| **FS‑10** | Assurer la disponibilité et la scalabilité (Docker, IaaS) | **FC** |
| **FS‑11** | Traçabilité et audit (journalisation, conformité RGPD) | **FC** |

*FP = Fonction Principale (justifie l’existence du produit).  
FC = Fonction Contraint (imposée par le contexte réglementaire, technique ou organisationnel).*

### 2.2 Critères de performance (extraits)

| **Fonction** | **Critère** | **Valeur attendue** |
|---|---|---|
| FS‑01 | Temps d’authentification | ≤ 2 s (SSO) |
| FS‑02 | Temps de réponse CRUD | ≤ 1 s pour lecture, ≤ 2 s pour écriture |
| FS‑04 | Temps de recherche plein‑texte | ≤ 3 s pour requêtes complexes |
| FS‑05 | Génération de rapport BIRT | ≤ 10 s (PDF) |
| FS‑06 | Taille maximale import | 200 Mo / fichier |
| FS‑07 | Taille maximale export | 500 Mo / fichier |
| FS‑08 | Délai d’envoi de mail | ≤ 5 s après validation |
| FS‑10 | Disponibilité en prod | ≥ 99,5 % (MTTR ≤ 1 h) |
| FS‑11 | Conservation des logs | 12 mois, format JSON, horodaté |

---

## 3. Expression fonctionnelle du besoin  

### 3.1 Décomposition hiérarchique  

| **Identifiant** | **Niveau** | **Description** |
|---|---|---|
| **B‑01** | Système | Système d’information SIREINES (Web + DB) |
| **B‑01‑01** | Sous‑système | Interface Web (Struts 2 + FreeMarker) |
| **B‑01‑02** | Sous‑système | Base de données PostgreSQL (schéma `sireines`) |
| **B‑01‑03** | Sous‑système | Moteur de reporting BIRT |
| **B‑01‑04** | Sous‑système | Conteneurisation Docker / Orchestration Docker‑Compose |
| **B‑01‑05** | Sous‑système | Service d’envoi de mail (SMTP interne) |
| **B‑01‑06** | Sous‑système | Elasticsearch intégré (search‑dynamo) |
| **B‑01‑07** | Sous‑système | Gestion des imports/exports (CSV, XML) |
| **B‑01‑08** | Sous‑système | Gestion des paramètres et de la version (fichier `version.properties`) |
| **B‑01‑09** | Sous‑système | Audit et traçabilité (log4j + journalisation) |

#### Exemple de besoin élémentaire (B‑01‑01‑01)  

| **Identifiant** | **B‑01‑01‑01** |
|---|---|
| **Description fonctionnelle** | L’utilisateur doit pouvoir se connecter à l’application via le SSO du ministère. |
| **Critère d’appréciation** | Authentification réussie en ≤ 2 s, journalisation de l’événement (login, IP, timestamp). |
| **Niveau d’importance** | **Obligatoire** |
| **Flexibilité** | Fixe (non négociable) |
| **Contraintes** | Respect du protocole SAML 2.0, conformité RGPD (collecte minimale des données). |

*(Tous les besoins élémentaires sont listés dans le tableau 3.2 ci‑dessous.)*

### 3.2 Tableau de caractérisation des besoins  

| **Fonction** | **Critère d’appréciation** | **Importance** | **Flexibilité** | **Contraintes** |
|---|---|---|---|---|
| **FS‑01 – Authentifier les usagers** | Temps d’authentification ≤ 2 s, journalisation | Obligatoire | Fixe | SSO (SAML 2.0), RGPD |
| **FS‑02 – Gestion des dossiers** | CRUD ≤ 1 s (lecture) / ≤ 2 s (écriture) | Obligatoire | Négociable (délais) | Conformité RGPD, persistance PostgreSQL |
| **FS‑03 – Gestion des référentiels** | Mise à jour ≤ 5 s, cohérence référentiels | Obligatoire | Négociable | Intégrité référentielle (FK) |
| **FS‑04 – Recherche plein‑texte** | Réponse ≤ 3 s, pertinence ≥ 90 % | Obligatoire | Négociable (temps) | Elasticsearch 5.6+, indexation quotidienne |
| **FS‑05 – Rapports BIRT** | Génération ≤ 10 s, rendu PDF/HTML | Obligatoire | Négociable (format) | BIRT 4.3, accès aux données via DAO |
| **FS‑06 – Import fichiers** | Taille max 200 Mo, validation schéma | Obligatoire | Négociable (format) | CSV/XML, gestion des doublons |
| **FS‑07 – Export CSV/Excel** | Taille max 500 Mo, encodage UTF‑8 | Obligatoire | Négociable (format) | Respect du standard RFC 4180 |
| **FS‑08 – Envoi de courriers** | Délai ≤ 5 s, accusé de réception | Obligatoire | Fixe | SMTP interne, suivi des statuts |
| **FS‑09 – Administration** | Version affichée, logs accessibles | Obligatoire | Fixe | Fichier `version.properties`, log4j XML |
| **FS‑10 – Disponibilité** | Disponibilité ≥ 99,5 % (MTTR ≤ 1 h) | Obligatoire | Négociable (scénario de basculement) | Docker‑Compose, réplication PostgreSQL |
| **FS‑11 – Traçabilité / RGPD** | Conservation logs 12 mois, anonymisation | Obligatoire | Fixe | Délai de suppression 5 ans (DUA) |

---

## 4. Validation de l’expression du besoin  

| **Étape** | **Méthode** | **Responsables** | **Livrable** |
|---|---|---|---|
| 1️⃣ | Atelier de recueil (MOA + MOE) – revue fonctionnelle | Chef de projet (ZEMOUR) – PO (LETROUIT) – Équipe dev (Klee Group) | Cahier des charges fonctionnel (ce document) |
| 2️⃣ | Prototypage UI (maquettes Struts 2) | UI/UX Designer – PO | Maquettes validées (PDF) |
| 3️⃣ | Revue de conformité RGPD | DPO (CGG / DRI) | Rapport d’impact (DPIA) |
| 4️⃣ | Tests d’acceptation (UAT) – scénario fonctionnel | Équipe recette (MOE) – Utilisateurs métier | Rapport de recette signé |
| 5️⃣ | Validation finale du comité de pilotage | MOA, MOE, DSI | Décision de mise en production |

*Traçabilité* : chaque besoin (B‑xx‑xx‑xx) est relié à un cas d’usage (CU‑xx) et à un critère de test (TC‑xx).  

---

## 5. Scénarios d’usage  

| **Scénario** | **Description** | **Étapes** | **Résultat attendu** |
|---|---|---|---|
| **SC‑N‑01** – **Connexion usager** (nominal) | L’usager se connecte via SSO et accède à la page d’accueil. | 1. Lancer le navigateur → URL `https://sireines.e2.rie.gouv.fr/Accueil.do`<br>2. Redirection SSO → saisie identifiants<br>3. Retour à l’application | Authentification réussie < 2 s, journal d’accès créé. |
| **SC‑E‑01** – **Création d’un dossier** (nominal) | Un agent ajoute un nouveau dossier de qualification. | 1. Menu “Dossiers → Nouveau”<br>2. Saisie des champs obligatoires (agent, structure, qualification)<br>3. Validation | Dossier persistant, audit `INSERT` enregistré, mail de confirmation envoyé (< 5 s). |
| **SC‑E‑02** – **Import d’un fichier CSV** (erreur) | L’opérateur tente d’importer un fichier mal formaté. | 1. Accès “Import fichier”<br>2. Sélection du fichier (ex : `bad_file.csv`)<br>3. Validation | Message d’erreur explicite, aucune donnée insérée, log d’erreur. |
| **SC‑E‑03** – **Recherche plein‑texte** (nominal) | L’utilisateur recherche les dossiers contenant le mot “hydrogène”. | 1. Saisie “hydrogène” dans le champ recherche<br>2. Déclenchement requête Elasticsearch | Résultats affichés en ≤ 3 s, pertinence ≥ 90 %. |
| **SC‑E‑04** – **Génération d’un rapport BIRT** (nominal) | L’administrateur génère le rapport “Pyramide des âges”. | 1. Menu “Rapports → Pyramide âges”<br>2. Sélection de la période<br>3. Clic “Générer” | PDF délivré en ≤ 10 s, contenant les données correctes. |
| **SC‑E‑05** – **Bascule version (Docker)** (nominal) | Déploiement d’une nouvelle version via Docker‑Compose. | 1. `git pull` → nouvelle image war<br>2. `docker-compose up -d --build`<br>3. Vérification de la santé (`docker ps`) | Nouvelle version active, aucun downtime > 30 s, logs d’événement. |
| **SC‑E‑06** – **Suppression d’un dossier** (erreur de contrainte) | Tentative de suppression d’un dossier lié à un courrier déjà envoyé. | 1. Sélection du dossier → “Supprimer”<br>2. Confirmation | Message “Suppression impossible – dossier référencé”, aucune suppression, audit `DELETE` non créé. |

---

## 6. Parties prenantes (Stakeholders)  

| **Partie prenante** | **Rôle** | **Besoins spécifiques** | **Impact sur la valeur** |
|---|---|---|---|
| **MOA – CGDD/DRI/AST4** (ZEMOUR, LETROUIT) | Commanditaire, validation fonctionnelle | Suivi complet des qualifications, reporting fiable, conformité RGPD | Valeur métier principale (FS‑01 à FS‑05) |
| **MOE – Klee Group (ex‑prestataire)** | Développement, intégration, maintenance | Respect des spécifications techniques, livrables Docker, CI/CD (Gitlab) | Garantie de livrable fonctionnel (FS‑10) |
| **DSI – SG/DNUM/PNM/DPNM3** | Exploitation, hébergement IaaS (ECO4) | Disponibilité ≥ 99,5 %, sauvegarde/recouvrement, monitoring | Valeur opérationnelle (FS‑10, FS‑11) |
| **Utilisateurs finaux (agents, experts)** | Saisie et consultation des dossiers | Interface ergonomique, temps de réponse rapide, accès aux rapports | Satisfaction utilisateur (FS‑02, FS‑04, FS‑05) |
| **Responsable sécurité (MOA‑SSI)** | Sécurité, conformité | Journalisation, chiffrement des mails, protection RGPD | Valeur de conformité (FS‑11) |
| **Support / Help‑desk** | Assistance, tickets | Accès aux logs, version applicative, procédure de rollback | Valeur de support (FS‑09) |
| **Auditeurs RGPD / CNIL** | Contrôle conformité | Conservation des logs 12 mois, traçabilité, DUA 5 ans | Valeur légale (FS‑11) |
| **BIRT Community** | Fournisseur du moteur de reporting | Compatibilité BIRT 4.3, licences OpenSource | Valeur de reporting (FS‑05) |

---

## 7. Contraintes et environnement  

| **Catégorie** | **Contraintes** |
|---|---|
| **Réglementaires** | RGPD (collecte minimale, droit à l’oubli, durée de conservation 5 ans), CNIL (déclaration n°1034232), DUA (5 ans). |
| **Techniques** | Java 1.7 (compatibilité avec BIRT 4.3), Struts 2, Maven 3, PostgreSQL 14 (Docker image `postgres:14.1-alpine`), Elasticsearch 5.6+, Docker Compose v2, Tomcat 7.0.108‑JDK8, Spring Framework 2.0, SonarQube analysis (`sonar.projectKey=sireines`). |
| **Infrastructure** | Hébergement IaaS (ECO4) – datacenter Paris La Défense, VM Linux (Ubuntu 20.04), volumes Docker persistants (`sireines_db_sireines_vol`, `sireines_pgadmin_sireines_vol`). |
| **Sécurité** | SSO (SAML 2.0), chiffrement TLS 1.2+, restrictions firewall (ports 443, 22, 5432, 8080), journalisation centralisée (log4j XML). |
| **Organisationnelles** | Processus de mise en production via merge‑request (preprod → prod) sur Gitlab, validation pipeline CI/CD, double‑validation (MOA + DSI). |
| **Performance** | Temps de réponse ≤ 2 s (CRUD), ≤ 3 s (search), ≤ 10 s (rapport BIRT). |
| **Disponibilité** | 99,5 % mensuel, MTTR ≤ 1 h, bascule Docker‑Compose en cas de crash. |
| **Scalabilité** | Possibilité d’ajouter des réplicas PostgreSQL (streaming) et des nœuds Elasticsearch via Docker‑Swarm/K8s (future). |

---

## 8. Critères de sélection et pondération (marché public)

| **Critère** | **Sous‑critère** | **Pondération** | **Modalité de notation** |
|---|---|---|---|
| **C‑01 – Fonctionnalités** | Couverture des FS‑01 à FS‑11 | 40 % | 0–5 (0 = non couvert, 5 = pleinement couvert) |
| **C‑02 – Qualité technique** | Conformité aux standards (Java 1.7, Struts 2, Maven) | 20 % | 0–5 |
| **C‑03 – Sécurité / RGPD** | Journalisation, anonymisation, SSO | 15 % | 0–5 |
| **C‑04 – Performance** | Temps de réponse, charge maximale | 10 % | 0–5 |
| **C‑05 – Exploitabilité** | Documentation, scripts Docker, CI/CD | 10 % | 0–5 |
| **C‑06 – Coût** | Prix total (licences + support) | 5 % | 0–5 (inverse) |

> **Score final** = Σ (pondération × note). Le soumissionnaire doit atteindre un score ≥ 3,5/5.

---

## 9. Glossaire et acronymes  

| **Acronyme** | **Signification** |
|---|---|
| **BIRT** | Business Intelligence and Reporting Tools (Eclipse) |
| **CI** | Continuous Integration |
| **CSS** | Cascading Style Sheets |
| **DD** | Déclaration de Données |
| **DDD** | Domain‑Driven Design |
| **Docker‑Compose** | Outil d’orchestration de conteneurs |
| **FTL** | FreeMarker Template Language |
| **IaaS** | Infrastructure as a Service |
| **JSF** | JavaServer Faces (non utilisé mais présent dans le contexte) |
| **MTTR** | Mean Time To Recovery |
| **RGPD** | Règlement Général sur la Protection des Données |
| **SSO** | Single Sign‑On |
| **UML** | Unified Modeling Language |
| **VM** | Virtual Machine |

---

## 10. Traçabilité des exigences  

| **ID Besoin** | **Description** | **Cas d’usage (CU‑xx)** | **Test (TC‑xx)** |
|---|---|---|---|
| B‑01‑01‑01 | Authentifier via SSO | CU‑01 – Connexion usager | TC‑01 – Temps d’authentification ≤ 2 s |
| B‑01‑02‑01 | Créer un dossier | CU‑02 – Création dossier | TC‑02 – Insertion ≤ 2 s, audit INSERT |
| B‑01‑04‑01 | Recherche plein‑texte | CU‑04 – Recherche dossier | TC‑04 – Réponse ≤ 3 s, pertinence ≥ 90 % |
| B‑01‑05‑01 | Générer rapport BIRT | CU‑05 – Rapport “Pyramide âges” | TC‑05 – PDF rendu ≤ 10 s |
| B‑01‑06‑01 | Import CSV | CU‑06 – Import fichier | TC‑06 – Validation schéma, taille ≤ 200 Mo |
| B‑01‑07‑01 | Export CSV | CU‑07 – Export liste dossiers | TC‑07 – Export ≤ 500 Mo, encodage UTF‑8 |
| B‑01‑09‑01 | Afficher version | CU‑09 – Administration | TC‑09 – Version affichée = `version.properties` |
| B‑01‑10‑01 | Redémarrage conteneur | CU‑10 – Mise à jour Docker | TC‑10 – Downtime ≤ 30 s, logs de redémarrage |
| B‑01‑11‑01 | Journalisation d’accès | CU‑11 – Audit | TC‑11 – Log présent, format JSON, horodatage |

*(Le tableau complet est disponible dans le dépôt sous `docs/CCF/traceability.xlsx`).*  

---

## 11. Annexes  

1. **Diagramme de cas d’usage** – (PDF joint)  
2. **Modèle de données** – (ERD `sireines-db.pdm`)  
3. **Exemple de fichier `docker-compose.yml`** – (extrait du répertoire `sireines-docker/`)  
4. **Checklist de conformité RGPD** – (document interne)  
5. **Plan de test d’acceptation** – (fichier `tests/acceptance_plan.xlsx`)  

---

> **Ce CCF a été élaboré en conformité avec la NF EN 16271 :2013 et constitue la base contractuelle pour les appels d’offres, la conception, le développement, les tests d’acceptation et la mise en production de la solution SIREINES.**  
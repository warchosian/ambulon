# Cahier des Clauses Techniques Particulières (CCTP)  
## Projet : **Afinope** – Application financière des opérateurs de l’État  

*Version 1.0 – 28 avril 2026*  

---  

## 1. Objet du marché  

| N° | Description | Référence CCF |
|---|-------------|----------------|
| 1.1 | Fourniture d’une solution logicielle complète d’ingestion, de transformation et de visualisation des données financières (référentiels, exécutoires et d’exécution) des opérateurs de l’État. | CCF n° AF‑01 |
| 1.2 | Mise à disposition d’une infrastructure d’exécution (Docker, PostgreSQL, Dagster) hébergée en environnement **cloud souverain** ou **on‑premise**, conforme aux exigences de la commande publique. | CCF n° AF‑02 |
| 1.3  | Services de support, de maintenance corrective et évolutive, ainsi que la formation des équipes du maître d’ouvrage. | CCF n° AF‑03 |

**Périmètre** :  

- Extraction de fichiers CSV depuis des répertoires d’entrée définis.  
- Validation et normalisation des données (types, formats, contraintes d’intégrité).  
- Chargement automatisé dans un schéma PostgreSQL pré‑défini (voir annexe A – dictionnaire de données).  
- Orchestration des pipelines via Dagster (graphes de tâches).  
- Mise à disposition de tableaux de bord (Superset) et d’API REST d’accès aux données agrégées.  
- Gestion des logs, de la traçabilité et du suivi d’incidents.  
- Documentation complète (technique, fonctionnelle, exploitation).  

---  

## 2. Description technique détaillée  

### 2.1 Spécifications fonctionnelles minimales (obligations de résultat)  

| Ref. | Fonctionnalité | Critère d’acceptation |
|------|----------------|-----------------------|
| F‑01 | **Ingestion de flux CSV** – Le système doit détecter chaque nouveau fichier `.csv` placé dans le répertoire `entree/` et le traiter dans un délai maximal de **5 minutes**. |
| F‑02 | **Validation** – Chaque fichier doit être validé selon les règles décrites dans le fichier `analyse/flux.txt` (ex. présence de colonnes obligatoires, conformité des types). En cas d’erreur, le fichier est déplacé vers `erreur/` avec un rapport d’erreur au format JSON. |
| F‑03 | **Transformation** – Les champs texte, numériques et date doivent être convertis conformément aux fonctions du module `app/helper.py`. Aucun champ `NULL` ne doit être inséré dans une colonne déclarée `NOT NULL`. |
| F‑04 | **Chargement** – Les données validées sont insérées dans les tables PostgreSQL décrites dans l’annexe A. Le taux de réussite du chargement doit être ≥ 99,9 % par lot. |
| F‑05 | **Orchestration** – Les pipelines Dagster (`circuit_alimentation`) doivent être exécutables via l’API Dagster et planifiables (cron ou déclencheur de fichier). |
| F‑06 | **Reporting** – Les vues matérialisées `tdb_view`, `tdb_abe_view` et `tdb_abp_view` doivent être actualisées quotidiennement et être accessibles via Superset (tableaux de bord prêts à l’emploi). |
| F‑07 | **Export** – Une API REST `/api/v1/export/{table}` doit permettre l’extraction au format CSV ou JSON d’une table donnée, protégée par authentification OAuth 2.0. |
| F‑08 | **Historisation** – Tous les traitements (début, fin, statut, logs) sont enregistrés dans la table `public."audit_log"` (à créer). |
| F‑09 | **Gestion des incidents** – Un ticket d’incident est automatiquement créé dans le système de suivi (ex. JIRA) dès qu’une erreur critique survient. |

### 2.2 Spécifications techniques obligatoires (obligations de moyen)  

| Ref. | Exigence | Niveau |
|------|----------|--------|
| T‑01 | **Langage** – Python 3.11 +  (voir `pyproject.toml`). |
| T‑02 | **Gestion de dépendances** – Poetry ≥ 1.5, verrouillage dans `poetry.lock`. |
| T‑03 | **Base de données** – PostgreSQL 15, version ≥ 15.2, configuration `max_connections ≥ 200`. |
| T‑04 | **Conteneurisation** – Docker ≥ 24.0, image officielle `python:3.11-slim`. |
| T‑05 | **Orchestration** – Dagster ≥ 1.8, utilisation du `DagsterWebserver` exposé sur le port 4400. |
| T‑06 | **Versionnage** – Git + GitLab CI ; le pipeline doit contenir les jobs `lint`, `test`, `build`, `deploy`. |
| T‑07 | **Modularité** – Chaque composant (ingestion, validation, transformation, persistance) doit être implémenté sous forme de classes Python distinctes, conformément à l’architecture actuelle (`app/`). |
| T‑08 | **Internationalisation** – Tous les messages d’erreur doivent être en français et en anglais (catalogue i18n). |
| T‑09 | **Gestion des secrets** – Les variables d’environnement (`.env`) contenant les mots de passe doivent être stockées dans le **Gestionnaire de secrets** de la plateforme d’hébergement (ex. HashiCorp Vault). |

### 2.3 Spécifications techniques souhaitées  

| Ref. | Exigence | Justification |
|------|----------|---------------|
| S‑01 | Utilisation de **SQLAlchemy 2.x** avec le mode “future” pour la génération de schémas. | Facilite la migration vers d’autres SGBD. |
| S‑02 | Tests de charge (JMeter) simulant **100 simultanés** sur l’API d’export. | Garantit la scalabilité. |
| S‑03 | Intégration d’un **catalogue de métadonnées** (Data‑catalog) exposé via CKAN. | Améliore la gouvernance des données. |

### 2.4 Spécifications techniques optionnelles  

| Ref. | Exigence | Conditions de mise en œuvre |
|------|----------|-----------------------------|
| O‑01 | Déploiement en **Kubernetes** (Helm chart fourni). | Sous réserve d’acceptation du maître d’ouvrage et de la disponibilité du cluster. |
| O‑02 | Mise en place d’un **pipeline CI/CD** complet avec promotion d’un environnement “pré‑production”. | Disponible dès la phase 3 du projet. |

---  

## 3. Architecture et conception  

| Élément | Contraintes | Normes / Standards |
|---------|-------------|----------------------|
| **Architecture** | Architecture **micro‑services** : ingestion (service `csv‑ingest`), transformation (`transformer`), persistance (`loader`), API (`gateway`). | ISO/IEC 42010, RGI – Interopérabilité. |
| **API** | RESTful, versionnée (`/api/v1/…`). | RFC 7231, OpenAPI 3.0. |
| **Base de données** | Schéma relationnel strict, contraintes d’intégrité (PK, FK, CHECK). | ISO/IEC 9075 (SQL). |
| **Conteneurs** | Images immuables, tag `<version>-<commit>`. | OCI Image Specification. |
| **Orchestration** | Dagster DAGs décrits en Python, exécution via `dagster-webserver`. | Dagster 1.8+ API. |
| **Dashboard** | Superset 2.x, thème `superset_dashboard_light`. | W3C WCAG 2.1 AA (RGAA). |
| **Frameworks autorisés** | `pandas`, `sqlalchemy`, `dagster`, `fastapi`, `uvicorn`. | Licences compatibles (MIT/BSD). |
| **Interopérabilité** | Export JSON conforme au **RGS – Profil Interopérabilité**. | RGI – Profil Interopérabilité. |

---  

## 4. Exigences de sécurité (RGS, ANSSI)  

| N° | Exigence | Niveau RGS | Mode d’évaluation |
|----|----------|------------|--------------------|
| Sec‑01 | **Authentification** – OAuth 2.0 (client‑credentials) pour l’API. | Renforcé | Test d’intrusion (OWASP ZAP). |
| Sec‑02 | **Contrôle d’accès** – RBAC avec 3 rôles (admin, opérateur, lecteur). | Renforcé | Vérification du mapping rôle‑permission. |
| Sec‑03 | **Chiffrement des données en transit** – TLS 1.3 avec certificats Let’s Encrypt ou équivalent souverain. | Basique | Scan SSL Labs. |
| Sec‑04 | **Chiffrement des données au repos** – `pgcrypto` (AES‑256) pour colonnes sensibles (ex. SIRET). | Renforcé | Revue de schéma et test de récupération. |
| Sec‑05 | **Journalisation** – Tous les accès API, les jobs Dagster et les opérations DB sont consignés dans `audit_log`. | Basique | Requête d’audit sur 30 jours. |
| Sec‑06 | **Gestion des vulnérabilités** – Mise à jour mensuelle des images Docker et des dépendances Python (SCA). | Basique | Rapport SCA (OWASP Dependency‑Check). |
| Sec‑07 | **RGPD** – Anonymisation des champs personnels (ex. SIRET) via pseudonymisation avant stockage. | Renforcé | Analyse d’impact relative à la protection des données (PIA). |
| Sec‑08 | **Sauvegarde** – Backup quotidien incrémental + weekly full, rétention 30 jours, test de restauration mensuel. | Basique | Test de restauration sur environnement de test. |
| Sec‑09 | **Plan de reprise d’activité (PRA)** – Temps de rétablissement < 4 h, perte de données < 15 min. | Renforcé | Simulation de basculement. |

---  

## 5. Interfaces et intégrations  

| Interface | Système partenaire | Protocole / Format | Points de contrôle |
|-----------|-------------------|-------------------|--------------------|
| **I‑01** | Répertoire de dépôt CSV (serveur SFTP) | SFTP, fichiers `.csv` UTF‑8 | Vérification de la signature GPG du lot. |
| **I‑02** | PostgreSQL central (instance `afinope-db`) | PostgreSQL 15, libpq | Test de connexion avec certificat client. |
| **I‑03** | Superset (visualisation) | HTTP / HTTPS, API Superset | Validation du token d’accès. |
| **I‑04** | Service d’authentification interne (Keycloak) | OpenID Connect | Vérification du flux d’obtention du token. |
| **I‑05** | Outil de suivi d’incidents (JIRA) | REST JSON | Envoi d’un ticket via webhook. |

**Modalités de recette** : chaque interface sera testée avec des jeux de données de référence (voir annexe B).  

---  

## 6. Environnements et infrastructure  

| Environnement | Description | Contraintes |
|---------------|-------------|-------------|
| **Dev** | Docker‑Compose local (services `db`, `app`). | Accès libre aux développeurs, données anonymisées. |
| **Int** | Cluster Docker Swarm ou Kubernetes (selon option O‑01). | Isolation réseau, secrets gérés par Vault. |
| **Pré‑prod** | Réplication exacte de la production, données de test (masquées). | Validation des SLA avant mise en prod. |
| **Prod** | Hébergement sur **cloud souverain** (ex. OVHcloud “Public Cloud” ou data‑center Étatique) ou **on‑premise** selon décision du maître d’ouvrage. | Conformité RGS – Souveraineté des données, disponibilité 99,9 % (SLA). |
| **Réseau** | VLAN dédié, firewall périmétrique avec règles “deny‑all‑except”. | inspection TLS, IDS/IPS (ANSSI). |
| **Haute disponibilité** | PostgreSQL en mode **Streaming Replication** (primary + 2 replicas). | RTO ≤ 2 h, RPO ≤ 5 min. |
| **Environnements de test** | Chaque pipeline CI crée un conteneur isolé avec jeu de données fixture. | Nettoyage post‑test automatisé. |

---  

## 7. Qualité et conformité  

| Référentiel | Exigence | Métrique |
|-------------|----------|----------|
| **ISO 9001** | Gestion documentaire – chaque livrable doit être versionné et archivé. | 100 % des livrables archivés dans le référentiel GitLab. |
| **ISO 25010** | *Performance* – Temps moyen de traitement d’un fichier CSV ≤ 30 s. | ≤ 30 s (mesuré sur jeu de 10 000 lignes). |
| **ISO 25010** | *Fiabilité* – Taux d’erreurs de chargement < 0,1 %. | < 0,1 % (rapport journalier). |
| **ISO 25010** | *Sécurité* – Conformité RGS, RGAA. | Validation RGS + RGAA ≥ AA. |
| **ISO 25010** | *Maintainability* – Couverture des tests unitaires ≥ 80 %. | Rapport `coverage.xml`. |
| **RGAA** | Accessibilité des tableaux de bord Superset. | Conformité WCAG 2.1 AA (audit automatisé + manuel). |

---  

## 8. Documentation et formation  

| Document | Format | Responsable | Délai |
|----------|--------|--------------|-------|
| **DOC‑01** : Spécifications fonctionnelles détaillées | PDF + Markdown | Maître d’ouvrage | J‑30 |
| **DOC‑02** : Architecture technique (diagrammes UML) | PDF + Visio | Prestataire | J‑25 |
| **DOC‑03** : Guide d’installation (Docker, Kubernetes) | Markdown | Prestataire | J‑20 |
| **DOC‑04** : Manuel d’utilisation (API, Dashboard) | PDF | Prestataire | J‑15 |
| **DOC‑05** : Guide d’exploitation (sauvegarde, monitoring) | PDF | Prestataire | J‑10 |
| **DOC‑06** : Plan de test (unitaires, intégration, charge) | Excel | Prestataire | J‑15 |
| **DOC‑07** : Rapport de conformité (RGS, RGPD, RGAA) | PDF | Prestataire | J‑5 |
| **FORM‑01** : Formation utilisateurs (2 jours) | Présentiel / Webex | Formateur (prestataire) | J‑3 |
| **FORM‑02** : Formation administrateurs (1 jour) | Présentiel / Webex | Formateur (prestataire) | J‑2 |

---  

## 9. Tests et recette  

| Type de test | Objectif | Méthodologie | Critère d’acceptation |
|--------------|----------|---------------|-----------------------|
| **Unitaire** | Vérifier chaque fonction (ex. `helper.na_to_empty`). | PyTest, couverture ≥ 80 %. | Tous les tests passent, coverage ≥ 80 %. |
| **Intégration** | Valider les flux de bout en bout (CSV → DB → Dashboard). | Jeux de données de référence (annexe B). | Aucun écart fonctionnel, taux de succès ≥ 99 %. |
| **Charge** | Mesurer la capacité de l’API d’export sous 100 concurrents. | JMeter, durée ≤ 5 s par requête. | Temps moyen ≤ 5 s, erreurs ≤ 1 %. |
| **Sécurité** | Vérifier conformité RGS et RGPD. | Scan OWASP ZAP, audit PIA. | Aucun défaut critique, PIA validée. |
| **Recette fonctionnelle** | Validation par le maître d’ouvrage. | Sessions de démonstration, validation des livrables. | Signature du procès‑verbal de recette. |
| **Recette de performance** | Disponibilité ≥ 99,9 % sur 30 jours. | Monitoring via Prometheus + Grafana. | SLA atteint, alertes < 5 % du temps total. |
| **Gestion des anomalies** | Traiter les défauts détectés. | Système de tickets JIRA, délais GTR ≤ 4 h, GTD ≤ 24 h. | Tous les tickets résolus dans les délais. |

---  

## 10. Maintenance et support  

| Niveau | Service | Délai d’intervention (GTR) | Délai de correction (GTD) | SLA |
|--------|---------|------------------------------|---------------------------|-----|
| **N1** – Support fonctionnel | Hotline (email + téléphone) | ≤ 4 h (hors week‑ends) | ≤ 24 h | Disponibilité ≥ 99 % |
| **N2** – Support technique | Intervention sur le serveur (Docker/K8s) | ≤ 2 h | ≤ 12 h | Disponibilité ≥ 99,5 % |
| **N3** – Maintenance évolutive | Ajout de nouveaux flux, mise à jour de schémas | Planifiée (pré‑prod → prod) | ≤ 48 h | 1 release/mois (max). |
| **N4** – Garantie | Correctifs de bugs critiques (sécurité) | ≤ 1 h | ≤ 8 h | 12 mois post‑déploiement. |

**Reporting** : tableau mensuel des indicateurs (MTTR, MTBF, disponibilité) fourni au maître d’ouvrage.  

---  

## 11. Livrables et planning  

| Jalons | Livrable | Format | Date cible |
|--------|----------|--------|------------|
| **J‑30** | CCTP signé | PDF/MD | 30 avril 2026 |
| **J‑25** | Architecture détaillée | PDF + Visio | 25 avril 2026 |
| **J‑20** | Prototype fonctionnel (Docker‑Compose) | Docker images, code source | 20 avril 2026 |
| **J‑15** | Documentation technique complète | PDF/MD | 15 avril 2026 |
| **J‑10** | Validation de la sécurité (rapport RGS) | PDF | 10 avril 2026 |
| **J‑5** | Rapport de conformité RGAA & RGPD | PDF | 5 avril 2026 |
| **J 0** | Livraison en production | Docker images, scripts d’installation | 28 avril 2026 |
| **J +30** | Rapport de mise en service & KPI | PDF | 28 mai 2026 |
| **J +90** | Bilan de la période de garantie | PDF | 28 juillet 2026 |

**Pénalités de retard** : ‑ 0,5 % du montant total par jour ouvré de retard, plafonné à ‑ 10 % du total.  

---  

## 12. Contraintes légales et réglementaires  

| Domaine | Obligation | Référence |
|---------|------------|-----------|
| **Propriété intellectuelle** | Le code source, la documentation et les livrables restent la propriété exclusive de l’État (domaine public). Le prestataire cède tous les droits d’exploitation, de modification et de distribution. | Article L. 111‑1 du Code de la propriété intellectuelle. |
| **Licences tierces** | Toutes les bibliothèques tierces doivent être compatibles avec la licence **GPL‑compatible** ou **MIT/BSD**. Le prestataire doit fournir la liste complète des licences. | Annex C – Table des licences. |
| **Protection des données** | Conformité au RGPD – Pseudonymisation des données à caractère personnel, registre des traitements, notification à la CNIL. | RGPD articles 5‑32. |
| **Archivage** | Les données de référence (ex. fichiers CSV originaux) doivent être archivées pendant **10 ans** au format PDF/A. | Arrêté du 28 janvier 2022 relatif à la conservation des documents numériques. |
| **Sécurité** | Application du RGS – Niveau **Renforcé** pour les données financières. | Référentiel Général de Sécurité (RGS) v 3. |
| **Accessibilité** | Les interfaces publiques (Superset) doivent être conformes au RGAA – Niveau AA. | Référentiel Général d’Amélioration de l’Accessibilité (RGAA). |

---  

## 13. Critères de sélection des offres  

| Critère | Pondération | Barème (0‑20) | Commentaire |
|---------|--------------|--------------|------------|
| **C‑01** – Conformité fonctionnelle (respect du CCF) | 30 % | 0 = non conforme, 20 = totalement conforme | Vérification par le comité de pilotage. |
| **C‑02** – Qualité de l’architecture (modularité, scalabilité) | 20 % | 0 = monolithique, 20 = micro‑services, CI/CD complet | Analyse du livrable d’architecture. |
| **C‑03** – Sécurité (RGS, RGPD) | 20 % | 0 = pas de plan, 20 = plan complet + preuves | Audit de sécurité pré‑sélection. |
| **C‑04** – Méthodologie de test & recette | 10 % | 0 = absence, 20 = plan détaillé + automatisation | Documentation de la stratégie de test. |
| **C‑05** – Coût global (TCO) | 10 % | 0 = coût > budget, 20 = coût le plus bas | Calcul sur base de l’annexe D. |
| **C‑06** – Références et expérience | 10 % | 0 = aucune, 20 = ≥ 3 projets similaires livrés | Attestations de références. |

**Notation** : chaque critère est noté sur 20, le total est ramené sur 100 points. L’offre la mieux notée (≥ 70 points) sera retenue.  

---  

## 14. Annexes contractuelles  

| Annexe | Contenu |
|--------|---------|
| **A** | Dictionnaire de données (schémas SQL). |
| **B** | Jeux de données de référence (exemple `REF_ORGANISME_20240614.csv`). |
| **C** | Tableau des licences tierces utilisées. |
| **D** | Calcul du coût total (licences, hébergement, support). |
| **E** | Modèle de procès‑verbal de recette. |
| **F** | Glossaire des acronymes (RGS, RGPD, RGI, DAG, etc.). |
| **G** | Modèle de déclaration de sous‑traitance (le cas échéant). |

---  

*Fait à Paris, le 28 avril 2026*  

*Le présent CCTP constitue le document contractuel de référence entre le maître d’ouvrage et le futur titulaire du marché.*  
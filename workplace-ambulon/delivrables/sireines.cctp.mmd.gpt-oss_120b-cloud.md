# Cahier des Clauses Techniques Particulières (CCTP)  
**Projet : SIREINES** – Application de gestion des dossiers de qualification des agents  

*Version 1.0 – 27 avril 2024*  

---  

## 1. Objet du marché  

| N° | Description |
|----|-------------|
| 1.1 | Fourniture, installation, configuration, mise en production et support de l’application **SIREINES** (gestion des dossiers de qualification, reporting BIRT, import/export Talend). |
| 1.2 | Fourniture de l’infrastructure d’exécution sous forme de conteneurs Docker (Tomcat 7, PostgreSQL 14.1‑alpine, pgAdmin4). |
| 1.3 | Livraison de la documentation fonctionnelle, technique, d’exploitation et de conformité (RGPD, RGS, CNIL). |
| 1.4 | Accompagnement du maître d’ouvrage (MOA) pendant les phases de recette, pré‑production et production. |

*Le présent CCTP précise les exigences techniques, fonctionnelles et contractuelles que le **Prestataire** devra satisfaire.*  

---  

## 2. Description technique détaillée  

### 2.1 Spécifications fonctionnelles (voir annexe A – “Glossaire fonctionnel”)  

| Fonctionnalité | Référence du module | Description succincte |
|----------------|---------------------|----------------------|
| Gestion des dossiers (création, modification, recherche) | `sireines-web` – contrôleurs `Dossier*` | CRUD complet avec validation métier. |
| Gestion des référentiels (agents, corps, structures, mots‑clefs) | `sireines-web` – contrôleurs `Referentiel*` | Consultation, recherche, mise à jour. |
| Import de fichiers (Talend) | `sireines-talend` – jobs Talend | Import CSV, génération de rapports BIRT. |
| Reporting BIRT | `sireines-web` – service `BirtManager` | Production de rapports PDF/HTML, export. |
| Authentification via Cerbère | `sireines-web` – `sireines-auth-config.xml` | SSO Cerbère (Rôle R_ADMIN, etc.). |
| API Rest (future) | `sireines-web` – couche Vertigo | Exposition de services métiers. |

### 2.2 Spécifications techniques obligatoires  

| Exigence | Référence | Détail |
|----------|-----------|--------|
| **Langage** | Java 8, J2EE | Code source sous `src/main/java`. |
| **Frameworks** | Struts 2, Spring 2.0, Vertigo, BIRT 4.3, Talend 7.x | Versions compatibles déclarées dans les `pom.xml`. |
| **Base de données** | PostgreSQL 14.1‑alpine | Schéma `public`, scripts fournis dans `sireines-database/script`. |
| **Conteneurisation** | Docker 20.10+, Docker‑Compose 1.29+ | `Dockerfile` et `docker‑compose.yml` fournis. |
| **Serveur d’application** | Tomcat 7.0.108‑JDK8 | Déploiement du WAR `sireines-web-*.war`. |
| **Gestion des dépendances** | Maven 3.6+ | Assemblage via `assembly.xml`. |
| **Sécurité transport** | TLS 1.2 minimum, certificats signés par l’ANSSI | Configuration du connecteur HTTPS du Tomcat (voir annexe C). |
| **Authentification** | Cerbère (SAML 2.0) – rôle `R_ADMIN` | Fichier `sireines-auth-config.xml`. |
| **Conformité RGPD** | Anonymisation via `CommonServices.sendMail` & `StringUtils` | Journalisation des traitements de données à caractère personnel. |
| **Journalisation** | Log4j 2, rotation quotidienne, rétention 30 jours. |
| **Sauvegarde DB** | Dump quotidien via `pg_dump` (conteneur `sireines-db_usine_container`). |
| **Monitoring** | Prometheus Node‑Exporter + Grafana (optionnel). |
| **Haute disponibilité** | 2 instances d’applications derrière un load‑balancer (HAProxy) en production. |
| **Performance** | Temps de réponse ≤ 2 s (95 % des requêtes), disponibilité ≥ 99,9 % (SLA). |
| **Internationalisation** | Français uniquement (fichiers de messages `*.properties`). |

### 2.3 Architecture et conception  

```
+-------------------+          +--------------------+          +-------------------+
|   Client Web     |  HTTPS   |  Load‑Balancer    |  HTTP    |  Tomcat (sireines |
| (navigateurs)    | <------> |  (HAProxy)        | <------> |  _app_usine_)    |
+-------------------+          +--------------------+          +-------------------+
                                   |                     |
                                   | JDBC (TLS)         |
                                   v                     v
                            +--------------------+   +-------------------+
                            | PostgreSQL 14.1    |   | pgAdmin4          |
                            | (sireines_db_usine)|   | (admin UI)        |
                            +--------------------+   +-------------------+

Docker‑Compose orchestre les 3 conteneurs :
- `sireines_app_usine_container` (image `sireines_app_usine_image`)  
- `sireines_db_usine_container` (image `postgres:14.1‑alpine`)  
- `sireines_pgadmin_container` (image `dpage/pgadmin4`)  

Volumes persistants :
- `sireines_db_sireines_vol` → données PostgreSQL  
- `sireines_pgadmin_sireines_vol` → configuration pgAdmin4  

```

*Tous les composants sont déclarés dans le fichier `docker‑compose.yml` (voir annexe D).*

---  

## 3. Exigences de sécurité (RGS, ANSSI, RGPD)  

| Référence | Niveau RGS | Description de l’obligation | Modalité de vérification |
|-----------|------------|-----------------------------|--------------------------|
| **3.1** | Basique | Authentification forte via Cerbère (SAML 2.0). | Test d’intégration SAML, revue `sireines-auth-config.xml`. |
| **3.2** | Basique | Chiffrement des flux HTTP (TLS 1.2). | Scan SSL Labs, certificat signé par l’ANSSI. |
| **3.3** | Basique | Chiffrement des données sensibles au repos (AES‑256) – mots‑de‑passe, tokens. | Vérification du `pgcrypto` dans le schéma PostgreSQL. |
| **3.4** | Basique | Traçabilité – journalisation de toutes les actions d’accès aux données à caractère personnel. | Log4j 2 configuré, tableau de bord de logs. |
| **3.5** | Basique | Droit d’accès, de rectification et d’effacement (RGPD Art. 15‑17). | Implémentation de la fonction `CommonServices.sendMail` + API d’anonymisation. |
| **3.6** | Basique | Gestion des vulnérabilités (ANSSI) – mise à jour mensuelle des images Docker. | Rapport de mise à jour des images (`docker pull`). |
| **3.7** | Basique | Ségrégation des environnements (dev / rec / pre‑prod / prod). | Variables d’environnement distinctes (`.env`). |
| **3.8** | Basique | Conservation de la preuve d’audit (intégrité des logs ≥ 180 jours). | Rotation des logs, stockage en S3‑compatible (optionnel). |

---  

## 4. Interfaces et intégrations  

| Interface | Type | Protocole / Format | Points d’intégration | Description |
|-----------|------|-------------------|----------------------|-------------|
| Front‑end | HTTP/HTTPS | HTML + FTL (FreeMarker) | `sireines-web/src/main/resources/template/**` | Génération des pages Struts2. |
| Authentification | SAML 2.0 | XML | `sireines-auth-config.xml` | Authentification unique via Cerbère. |
| Base de données | JDBC | PostgreSQL JDBC driver 42.x | `application-config.xml` → `persistence.xml` | Accès aux tables métiers (dossiers, référentiels). |
| Reporting BIRT | HTTP (Servlet) | BIRT 4.3 (XML, PDF) | `BirtManager` | Production de rapports (ex : `age_pyramid.rptdesign`). |
| Import Talend | Talend Job (Java) | CSV, XML | `sireines-talend` | Import de fichiers de qualification. |
| Monitoring (optionnel) | HTTP | Prometheus metrics | Endpoint `/actuator/metrics` (Spring) | Export des métriques d’utilisation. |
| API Rest (future) | HTTP/HTTPS | JSON‑API | `sireines-web` – couche Vertigo | Exposition des services métiers (non‑déployé en V1). |

---  

## 5. Environnements et infrastructure  

| Environnement | Conteneurs | Volumes | Variables d’environnement (`.env`) | Port exposé |
|---------------|------------|---------|-----------------------------------|------------|
| **Développement** | `sireines_app_usine_container` (image locale) | `sireines_db_sireines_vol` (dev) | `POSTGRES_DB=postgres`, `POSTGRES_USER=postgres`, `POSTGRES_PASSWORD=postgres`, `APP_ENV=dev` | 8080 (Tomcat) |
| **Recette** | idem | idem | `APP_ENV=recette` | 8080 |
| **Pré‑production** | idem | idem | `APP_ENV=preprod` | 8080 |
| **Production** | 2 instances + HAProxy | `sireines_db_sireines_vol` (production) | `APP_ENV=prod` | 443 (HTTPS) |

*Tous les environnements sont créés par la commande `docker‑compose up -d` depuis le répertoire racine `sireines_pgadmin/`.*  

---  

## 6. Qualité et conformité  

| Référentiel | Objectif | Critère de mesure |
|-------------|----------|-------------------|
| ISO 25010 (Qualité logicielle) | Fonctionnalité, fiabilité, performance, sécurité, maintenabilité, portabilité | Tests automatisés + revue de code. |
| ISO 27001 / RGS Basique | Sécurité de l’information | Analyse de risques, journalisation, chiffrement. |
| RGPD | Protection des données à caractère personnel | Registre des traitements (Annexe E), droit d’accès, suppression. |
| ANSSI – Guide “Sécurisation des conteneurs Docker” | Durcissement des images | Scan Trivy / Clair, mise à jour mensuelle. |
| CI/CD (GitLab) | Livraison continue | Pipelines automatisés (`.gitlab-ci.yml`). |
| SonarQube | Qualité du code | Niveau “B” minimum, aucune vulnérabilité critique. |

---  

## 7. Documentation et formation  

| Livrable | Contenu | Format | Responsable |
|----------|---------|--------|------------|
| **Guide d’installation** | Prérequis, Docker‑Compose, variables, procédures de mise à jour. | Markdown + PDF | Prestataire. |
| **Guide d’exploitation** | Démarrage/arrêt, sauvegarde DB, monitoring, récupération d’incident. | PDF | Prestataire. |
| **Guide d’administration Cerbère** | Gestion des rôles, mise à jour du fichier `sireines‑auth‑config.xml`. | PDF | Prestataire. |
| **Manuel utilisateur** | Parcours fonctionnels (accueil, dossiers, référentiels, rapports). | HTML (wiki) + PDF | MOA. |
| **Manuel développeur** | Architecture, modules Maven, schémas K‑maps, scripts SQL. | Markdown + diagrammes PlantUML. |
| **Formation** | 2 sessions de 4 h (déploiement Docker, administration BIRT, exploitation). | Présentiel / Teams. |
| **Registre RGPD** | Tableau des traitements, base légale, durée de conservation. | Excel + PDF. |

---  

## 8. Tests et recette  

| Type de test | Objectif | Méthodologie | Critère d’acceptation |
|--------------|----------|--------------|----------------------|
| **Tests unitaires** | Vérifier chaque méthode Java. | JUnit 5, JaCoCo ≥ 80 % couverture. | Aucun test échoué, couverture ≥ 80 %. |
| **Tests d’intégration** | Interaction entre modules (Web ↔ DB, BIRT). | Spring Boot Test, Docker‑Compose en mode `test`. | Tous les scénarios fonctionnels passent. |
| **Tests fonctionnels** | Parcours métier (création dossier, import, reporting). | Selenium WebDriver + Cucumber. | Scénarios “happy‑path” et “edge‑case” réussis. |
| **Tests de performance** | Temps de réponse, charge. | JMeter – 100 utilisateurs simultanés, 30 min. | 95 % des requêtes ≤ 2 s, aucun dépassement de CPU > 80 %. |
| **Tests de sécurité** | Vulnérabilités applicatives. | OWASP ZAP, Trivy sur images Docker. | Aucun résultat “high” ou “critical”. |
| **Tests de conformité RGPD** | Vérifier droit d’accès, anonymisation. | Requêtes d’extraction, suppression. | Conformité démontrée, logs d’audit. |
| **Recette métier** | Validation par le MOA. | Tableaux de suivi (Annexe F). | Validation signée du MOA. |

---  

## 9. Maintenance et support  

| Niveau | Service | Délai d’intervention (GTR) | Délai de résolution (GTD) | SLA |
|--------|---------|----------------------------|---------------------------|-----|
| **N1 – Support fonctionnel** | Assistance utilisateur (ouverture ticket). | ≤ 4 h ouvrées. | ≤ 8 h ouvrées. | 95 % des tickets résolus dans le GTD. |
| **N2 – Support applicatif** | Correction de bugs, évolutions mineures. | ≤ 2 h ouvrées. | ≤ 24 h ouvrées. | 90 % des corrections dans le GTD. |
| **N3 – Support infrastructure** | Incident Docker/DB, restauration backup. | ≤ 1 h. | ≤ 6 h. | 99 % de disponibilité de l’infrastructure. |
| **Escalade** | MOE → MOA → Direction IT | 2 jours d’escalade maximale. | – | – |

**Garantie** : 12 mois à compter de la mise en production, renouvelable tacite.  

---  

## 10. Livrables et planning  

| Phase | Livrable | Date cible | Responsable |
|-------|----------|------------|--------------|
| **Analyse** | Cahier des charges fonctionnel (CCF) | 30/04/2024 | MOA |
| **Conception** | Architecture détaillée, schémas UML | 15/05/2024 | Architecte |
| **Développement** | Code source complet (`sireines‑*`), WAR, scripts Docker | 30/06/2024 | Équipe de dev |
| **Tests unitaires & int.** | Rapport de couverture, logs JUnit | 15/07/2024 | QA |
| **Tests fonctionnels** | Scripts Selenium, rapport d’exécution | 31/07/2024 | QA |
| **Recette** | Rapport de recette signé (Annexe F) | 15/08/2024 | MOA |
| **Pré‑production** | Déploiement sur environnement `preprod` | 20/08/2024 | Ops |
| **Production** | Mise en service `prod` (HA) | 01/09/2024 | Ops |
| **Documentation** | Guides, registre RGPD, livrables annexes | 01/09/2024 | Documentalist |
| **Support** | Entrée en service (SLA) | 02/09/2024 | Support |

---  

## 11. Contraintes légales et réglementaires  

| Domaine | Exigence | Application |
|---------|----------|-------------|
| **Propriété intellectuelle** | Tous les livrables restent la propriété exclusive du **Maître d’Ouvrage**. Le prestataire cède les droits patrimoniaux et moraux. | Clause de cession de droits (contrat). |
| **Licences tierces** | Bibliothèques Open‑Source (Apache 2.0, LGPL, MIT) – liste dans le fichier `NOTICE.md`. | Vérification de conformité avant livraison. |
| **RGPD** | Registre des traitements, droit d’accès/rectification, notification CNIL. | Annexe E – registre, déclaration CNIL n°1034232 (29/09/2014). |
| **RGS** | Niveau **Basique** – authentification, chiffrement, journalisation. | Conforme aux exigences du tableau §3. |
| **ANSSI** | Durcissement des images Docker, mise à jour de sécurité mensuelle. | Scan Trivy, mise à jour automatisée. |
| **Archivage** | DUA = 5 ans, élimination sécurisée après. | Politique d’archivage (Annexe H). |
| **Accessibilité** | Conformité RGAA 2.1 (niveau AA). | Templates `template/simple_read` pré‑configurés. |

---  

## 12. Critères de sélection des offres  

| Critère | Pondération | Barème (0‑20) | Modalité d’évaluation |
|---------|--------------|---------------|-----------------------|
| **Conformité fonctionnelle** (CCF) | 30 % | 0 = non conforme, 20 = totalement conforme. | Analyse du livrable fonctionnel. |
| **Qualité du code** (SonarQube, couverture tests) | 20 % | 0 = bugs critiques, 20 = aucun défaut, couverture ≥ 80 %. | Rapport Sonar, JaCoCo. |
| **Sécurité** (RGS, RGPD, scans) | 20 % | 0 = vulnérabilités critiques, 20 = conforme RGS + aucune vulnérabilité. | Rapports OWASP ZAP, Trivy. |
| **Performance** (temps de réponse, disponibilité) | 15 % | 0 = SLA non respecté, 20 = SLA largement dépassé. | Résultats JMeter, monitoring. |
| **Méthodologie et planning** | 10 % | 0 = plan incomplet, 20 = plan détaillé, jalons réalistes. | Analyse du planning fourni. |
| **Coût** (TCO) | 5 % | 0 = coût excessif, 20 = coût le plus compétitif. | Comparaison des devis. |

> **Notation** : chaque critère est noté sur 20, la note finale est la somme pondérée (sur 100). Le **candidat retenu** doit obtenir **≥ 70 points** et satisfaire les exigences obligatoires (sécurité, conformité RGPD, disponibilité).  

---  

## 13. Annexes contractuelles  

| Annexe | Contenu |
|--------|---------|
| **A** | Glossaire fonctionnel (dossiers, référentiels, mots‑clefs). |
| **B** | Modèle de tableau de suivi des exigences (traceability matrix). |
| **C** | Spécifications du connecteur HTTPS du serveur Tomcat (certificats, keystore). |
| **D** | `docker‑compose.yml` complet (volumes, réseaux, variables). |
| **E** | Registre RGPD – traitements, bases légales, durée de conservation. |
| **F** | Tableau de recette – scénarios, résultats, signatures MOA. |
| **G** | Modèle de contrat de cession de droits d’auteur. |
| **H** | Politique d’archivage et de destruction des données. |
| **I** | Liste des licences tierces (Apache 2.0, MIT, LGPL) – fichier `NOTICE.md`. |
| **J** | Modèle de reporting d’incident (format JSON). |
| **K** | Procédure de mise à jour des images Docker (pipeline CI/CD). |

---  

### Fait à …, le …  

| Le Maître d’Ouvrage | Le Prestataire |
|---------------------|----------------|
| **Nom / signature** | **Nom / signature** |
| **Fonction** | **Fonction** |
| **Date** | **Date** |

---  

*Ce CCTP constitue le document contractuel de référence pour la mise en œuvre du projet SIREINES. Toute modification devra faire l’objet d’un avenant signé par les deux parties.*
# Cahier des Clauses Techniques Particulières (CCTP)  
**Marché public – Déploiement et maintenance de l’application SIREINES**  

> **Version : 1.0 – 27/04/2026**  

---

## 1. Objet du marché  

| N° | Description | Référence fonctionnelle (CCF) |
|---|-------------|-------------------------------|
| 1 | Fourniture d’une solution applicative Java/J2EE (SIREINES) permettant la gestion du répertoire national d’experts et spécialistes, incluant la collecte, la concentration et la diffusion des données de qualification. | CCF‑SIREINES‑001 |
| 2 | Livraison, mise en production, exploitation et maintenance (corrective / évolutive) de l’application sur l’infrastructure IaaS (ECO4) du ministère de la Transition Écologique. | CCF‑SIREINES‑002 |
| 3 | Documentation technique, fonctionnelle et juridique, ainsi que les livrables de formation. | CCF‑SIREINES‑003 |

**Périmètre fonctionnel** – décrit dans le CCF :  
- Gestion des dossiers de qualification (CRUD)  
- Interface web (Struts 2 + FreeMarker) accessible aux agents, référentiels, comités de domaine, etc.  
- Génération de rapports BIRT (statistiques, pyramide d’âge, extraction totale)  
- Import/export de données (Talend)  
- Authentification/authorisation via Cerbère (Rôle R_ADMIN)  

---

## 2. Description technique détaillée  

### 2.1 Spécifications fonctionnelles minimales (extraits)  

| Fonctionnalité | Description | Source |
|----------------|-------------|--------|
| Gestion des dossiers | Création, lecture, mise à jour, recherche, suppression, export CSV/Excel, génération de rapports BIRT. | `src/main/java/i2/application/sireines/controller/dossiers/*` |
| Gestion des référentiels | CRUD sur corps, grades, comités, mots‑clefs, qualifications, etc. | `src/main/java/i2/application/sireines/controller/referentiel/*` |
| Import de fichiers | Upload de fichiers, suivi de synthèse, traitement via Talend. | `src/main/webapp/jsp/imports/importFichier.jsp` |
| Authentification | Authentification unique via Cerbère, rôle R_ADMIN, permissions OP_READ/OP_WRITE. | `src/main/resources/META-INF/sireines-auth-config.xml` |
| Reporting BIRT | 20+ rapports (ex. « Population qualifiée par corps », « Pyramide des âges », etc.). | `sireines-talend/reports/*.rptdesign` |
| API de recherche | Indexation ElasticSearch (Vertigo Dynamo Search) sur les dossiers. | `SearchManagerInitializer.java` + `src/main/resources/search/config/elasticsearch.yml` |
| Gestion de la base | PostgreSQL 14 (Docker) – schéma décrit dans `sireines-database/modele/*.sql`. | `sireines-database/script/...` |

### 2.2 Spécifications techniques obligatoires  

| N° | Exigence | Mesure / Critère d’acceptation | Source |
|---|----------|-------------------------------|--------|
| T‑01 | L’application doit être packagée au format **WAR** compatible Tomcat 7.0+ (JDK 8). | `Dockerfile` copie `sireines-web.war` → `/tmp/ROOT.war`. | `Dockerfile` |
| T‑02 | Le serveur d’application doit être déployé dans un **container Docker** basé sur `tomcat:7.0.108-jdk8`. | `FROM tomcat:7.0.108-jdk8` dans Dockerfile. | `Dockerfile` |
| T‑03 | La base de données PostgreSQL 14 alpine doit être déployée dans un container dédié, persistant via un **Docker volume** `sireines_db_sireines_vol`. | `docker-compose.yml` définit le volume et le service `sireines-db`. | `docker-compose.yml` |
| T‑04 | Le conteneur `pgadmin` doit être provisionné avec le volume `sireines_pgadmin_sireines_vol`. | `docker-compose.yml` → service `pgadmin`. | `docker-compose.yml` |
| T‑05 | Le code source doit être compilable avec **Maven 3.6+** (Java 1.7). | `pom.xml` → `<maven.compiler.source>1.7</maven.compiler.source</...>` (déduit du repo). | `pom.xml` |
| T‑06 | Les dépendances tierces (Spring 2.x, Struts 2, Vertigo, BIRT 4.3, Talend) doivent être déclarées dans les `pom.xml` de chaque module. | Vérification du `dependencyManagement` dans les `pom.xml`. | `pom.xml` |
| T‑07 | L’application doit être **stateless** au niveau HTTP (session uniquement via `SireinesSessionFilter`). | Implémentation du filtre `SireinesSessionFilter.java`. | `src/main/java/i2/application/sireines/filter/SireinesSessionFilter.java` |
| T‑08 | Toutes les pages web doivent être générées via les templates **FreeMarker** (`.ftl`) fournis. | Aucun `.jsp` contenant du code Java. | `src/main/resources/template/**/*.ftl` |
| T‑09 | L’accès aux URLs doit être limité à **HTTPS** (TLS 1.2 minimum). | Le serveur Tomcat doit être configuré avec un keystore (non fourni, à fournir). | CCTP – exigence |
| T‑10 | Le mot de passe de connexion à la BDD (`POSTGRES_PASSWORD`) doit être **crypté** dans le fichier `.env` (ex. `docker secret`). | Le fichier `.env.sample` masque le mot de passe. | `.env.sample` |
| T‑11 | L’application doit être **compatible RGPD** : consentement, droit d’accès, droit à l’oubli, journalisation des accès. | Implémentation des contrôles dans `CommonServices.sendMail`, `StringUtils.isValidCriteria`, etc. | Code source |
| T‑12 | **RGS Renforcé** (niveau 2) : chiffrement des données en transit, stockage chiffré (AES‑256) des données sensibles (ex. coordonnées). | Utilisation de `javax.crypto` ou du SGBD avec `pgcrypto`. | CCTP – exigence |
| T‑13 | Les logs applicatifs doivent être centralisés (log4j 2) et exporter en **JSON** compatible SIEM. | `log4j.xml` → appender JSON. | `src/main/resources/log4j.xml` |
| T‑14 | Le temps de réponse moyen des pages < 2 s sous charge (100 utilisateurs simultanés). | Test de charge (JMeter) – critère d’acceptation. | CCTP – exigence |
| T‑15 | Disponibilité cible : **99,9 %** sur 12 mois (excluant fenêtres de maintenance planifiées). | Monitoring via Prometheus/Grafana. | CCTP – exigence |

### 2.3 Spécifications techniques souhaitées (optionnelles)  

| N° | Exigence | Bénéfice | Source |
|---|----------|----------|--------|
| S‑01 | Déploiement **Kubernetes** (Helm chart) en plus du Docker‑Compose. | Scalabilité horizontale. | – |
| S‑02 | Authentification **SSO** (FranceConnect) en plus de Cerbère. | Simplification du login. | – |
| S‑03 | Utilisation de **OpenAPI** pour exposer les services métiers (REST). | Interopérabilité RGI. | – |
| S‑04 | Sauvegarde automatisée de la base (snapshot quotidien) stockée hors‑site. | Continuité d’activité. | – |

### 2.4 Spécifications techniques optionnelles (facultatives)  

| N° | Exigence | Bénéfice |
|---|----------|----------|
| O‑01 | Mise à disposition d’un **module de test automatisé** (Selenium + JUnit) pour les écrans UI. | Réduction du temps de recette. |
| O‑02 | Intégration d’un **pipeline CI/CD** complet (GitLab‑CI) incluant SAST/DAST. | Sécurité du code en continu. |

---

## 3. Architecture et conception  

### 3.1 Diagramme d’architecture (description)  

```
+-------------------+       +-------------------+       +-------------------+
|   Utilisateur    | <---> |  Load‑Balancer    | <---> |   Tomcat (Docker) |
|  (HTTPS)         |       |  (TLS termination) |     |  (sireines‑app)   |
+-------------------+       +-------------------+       +-------------------+
                                 |
                                 v
                        +-------------------+
                        |  PostgreSQL (Docker) |
                        |  (sireines‑db)      |
                        +-------------------+
                                 |
                                 v
                        +-------------------+
                        |   pgAdmin (Docker) |
                        +-------------------+

```

- **Conteneurs** (Docker‑Compose) : `sireines-app`, `sireines-db`, `sireines-pgadmin`.  
- **Volumes persistants** : `sireines_db_sireines_vol` (BDD) et `sireines_pgadmin_sireines_vol` (configuration pgAdmin).  
- **Réseau interne** : bridge Docker, aucun port exposé hors du load‑balancer sauf 80/443.  

### 3.2 Normes et standards obligatoires  

| Domaine | Référence | Application |
|----------|------------|-------------|
| Java | **ISO/IEC 30170** (Java SE 7) | Code source |
| Web | **W3C HTML 5**, **WCAG 2.1 AA** (accessibilité) | Templates FTL |
| Sécurité | **RGS Renforcé** (niveau 2) | Chiffrement TLS, stockage chiffré |
| Interopérabilité | **RGI** – API REST, JSON | Future évolutif |
| Qualité | **ISO 25010** (maintenabilité, fiabilité) | Tests unitaires, couverture ≥ 80 % |
| Accessibilité | **RGAA** (niveau 2) | Pages web (templates) |
| Gestion de configuration | **ITIL v4** – CMDB, changement | Git + GitLab‑CI |
| Documentation | **ISO 9001** – Documentation des processus | CCTP, livrables |

### 3.3 Contraintes architecturales imposées  

1. **Séparation des responsabilités** – un conteneur par couche (app, BDD, admin).  
2. **Pas de stockage de données sensibles sur le disque du conteneur** – uniquement dans le volume Docker.  
3. **Utilisation du framework Vertigo Dynamo Search** pour l’indexation ElasticSearch (embedded).  
4. **BIRT 4.3** doit être exécuté en mode **headless** via le `BirtManager` (interface `publish`).  
5. **Authentification unique** via le serveur Cerbère (`authorisation-config.xml`).  

---

## 4. Exigences de sécurité (RGS, ANSSI)  

| N° | Exigence | Niveau RGS | Modalité de vérification |
|---|----------|------------|--------------------------|
| S‑01 | Authentification forte (Cerbère) | **Renforcé** | Test de connexion avec compte R_ADMIN, audit des logs d’accès. |
| S‑02 | Chiffrement TLS 1.2+ sur toutes les communications HTTP/HTTPS | **Renforcé** | Scan SSL Labs, validation du certificat. |
| S‑03 | Chiffrement des données stockées (coordonnées, mails) | **Renforcé** | Vérification du schéma BDD (`pgcrypto`), tests d’accès non‑chiffrés. |
| S‑04 | Journalisation centralisée (log4j → JSON) | **Basique** | Inspection du fichier `log4j.xml`, test de réception par SIEM. |
| S‑05 | Gestion des mots‑de‑passe (hash bcrypt, politique de complexité) | **Renforcé** | Revue du code `UserDetailsService` (non fourni – à implémenter). |
| S‑06 | Contrôle d’accès basé sur les rôles (R_ADMIN, OP_READ, OP_WRITE) | **Renforcé** | Test d’accès aux URLs avec différents rôles, validation du fichier `sireines‑auth‑config.xml`. |
| S‑07 | Protection contre les injections SQL | **Renforcé** | Analyse statique (SonarQube) et tests d’injection (OWASP ZAP). |
| S‑08 | Sécurité des conteneurs (image minimale, mise à jour régulière) | **Renforcé** | Scan Trivy ou Clair sur l’image `tomcat:7.0.108-jdk8`. |
| S‑09 | Conformité RGPD – Droit d’accès, d’effacement, registre des traitements | **Renforcé** | Vérification du registre (`RGPD‑Matrice.xlsx` – à fournir). |
| S‑10 | Gestion des incidents de sécurité (plan de réponse) | **Renforcé** | Existence d’un SOP (à livrer). |

### 4.1 Gestion des données à caractère personnel (DACP)  

- **Catégorie** : coordonnées des experts (nom, prénom, email, téléphone).  
- **Base juridique** : Art. 9‑2‑c du RGPD (exécution d’une mission d’intérêt public).  
- **Mesures** : chiffrement AES‑256, pseudonymisation lors des exports, archivage 5 ans (DUA).  

---

## 5. Interfaces et intégrations  

| Interface | Type | Protocole | Format | Points d’intégration | Référence |
|----------|------|-----------|--------|----------------------|-----------|
| Cerbère | Auth/Z Auth | HTTPS | XML (authorisation‑config) | `sireines‑auth‑config.xml` | `src/main/resources/META-INF/sireines‑auth‑config.xml` |
| PostgreSQL | BDD | TCP 5432 | SQL | `docker‑exec -it sireines‑db psql` | `sireines‑database/script/**/*.sql` |
| BIRT | Reporting | HTTP (REST) | PDF / HTML | `BirtManager.publish()` | `src/main/java/i2/application/sireines/boot/manager/BirtManager.java` |
| ElasticSearch (embedded) | Recherche | HTTP (localhost) | JSON | `SearchManagerInitializer` | `src/main/java/i2/application/sireines/boot/initializer/SearchManagerInitializer.java` |
| Talend | Import/Export | File system (CSV, XML) | CSV / XML | `Talend` → `imports` module | `sireines‑talend/reports/*.rptdesign` |
| PgAdmin | Administration BDD | HTTPS | UI | `docker‑compose.yml` – service `pgadmin` | `docker‑compose.yml` |

**Modalités de recette** : chaque interface doit être validée par un jeu de scénarios (exemple : appel REST BIRT → génération PDF, connexion Cerbère → refus d’accès sans rôle).  

---

## 6. Environnements et infrastructure  

| Environnement | Description | Conteneurs | Volumes | Accès |
|---------------|-------------|------------|---------|-------|
| **Développement** | Machine développeur (Docker Desktop) | `sireines‑app`, `sireines‑db`, `pgadmin` | `sireines_db_dev_vol`, `sireines_pgadmin_dev_vol` | Local (localhost) |
| **Recette** | Serveur `sireinesrec` (Bastion) | Identique au prod | `sireines_db_rec_vol` | VPN + Bastion |
| **Pré‑production** | Serveur `sireinesppr` | Identique au prod | `sireines_db_preprod_vol` | VPN + Bastion |
| **Production** | Serveur `sireinesprod` (ECO4) | Identique au prod | `sireines_db_prod_vol` | Accès restreint (IP whitelisting) |

### 6.1 Configurations réseau  

- **Ports exposés** : 80 → 8080 (Tomcat), 443 → 8443 (TLS), 5432 (PostgreSQL) – uniquement depuis le réseau interne.  
- **Pare‑feu** : règles d’autorisation strictes (IP source autorisée).  

### 6.2 Haute disponibilité (PRA/PCA)  

- **PostgreSQL** : réplication streaming (master‑slave) – à mettre en place en option S‑04.  
- **Tomcat** : deux instances derrière le load‑balancer, bascule automatique.  
- **Backup** : snapshots quotidiens du volume `sireines_db_*` stockés sur stockage objet (S3‑compatible).  

---

## 7. Qualité et conformité  

| Critère | Référence | Méthode de mesure |
|---------|-----------|--------------------|
| **Qualité du code** | ISO 25010 – maintenabilité | SonarQube (`sonar-project.properties`) – couverture ≥ 80 % |
| **Performance** | Temps de réponse < 2 s (100 U) | JMeter script `SIREINES‑Perf‑Load.jmx` |
| **Disponibilité** | 99,9 % sur 12 mois | Monitoring Grafana/Prometheus (SLA) |
| **Sécurité** | RGS Renforcé, OWASP Top 10 | Scan Trivy, ZAP, audit code |
| **Accessibilité** | RGAA 2.1 AA | Test axe‑core, rapport d’audit |
| **Interopérabilité** | RGI – API REST (future) | Validation OpenAPI (Swagger) |
| **Documentation** | ISO 9001 – livrables | Vérification de la présence des annexes (CCTP, guide d’installation, etc.) |

---

## 8. Documentation et formation  

| Livrable | Format | Contenu | Responsable |
|----------|--------|----------|-------------|
| **Guide d’installation** | Markdown + PDF | Procédure Docker‑Compose, pré‑requis, variables d’environnement | Équipe DevOps |
| **Guide d’exploitation** | Markdown | Gestion des logs, sauvegardes, monitoring, récupération d’incident | Équipe Opérations |
| **Guide de maintenance** | PDF | Patch, mise à jour de la base, migration de version | Équipe Support |
| **Manuel utilisateur** | HTML (via l’app) | Fonctionnalités métier, FAQ | MOA |
| **Formation** | Sessions (2 jours) + supports PPT | Administration Cerbère, utilisation BIRT, import Talend | Formateur dédié |
| **Documentation API (optionnelle)** | OpenAPI 3.0 (JSON) | End‑points REST prévus pour RGI | Équipe Architecture |

---

## 9. Tests et recette  

| Type de test | Objectif | Outils | Critères d’acceptation |
|---------------|----------|--------|-----------------------|
| **Tests unitaires** | Vérifier chaque classe Java | JUnit 5, Mockito | 80 % de couverture |
| **Tests d’intégration** | Interaction services (DB, BIRT, Elastic) | Spring Test, TestContainers | Tous les scénarios fonctionnels passent |
| **Tests fonctionnels** | Parcours métier (CRUD dossiers, rapports) | Selenium + Cucumber | Aucun défaut bloquant |
| **Tests de charge** | 100 U simultanés, 30 min | JMeter | Temps moyen ≤ 2 s, pas d’erreur 5xx |
| **Tests de sécurité** | Vulnérabilités OWASP Top 10 | OWASP ZAP, Trivy | Aucun résultat HIGH/CRITICAL |
| **Tests d’acceptation** | Validation du MOA | Check‑list CCF | Toutes les exigences fonctionnelles validées |
| **Tests de reprise** | PRA – bascule sur serveur de secours | Scripts Ansible | Application opérationnelle en < 5 min |

**Gestion des anomalies** : chaque anomalie est enregistrée dans le suivi GitLab Issues, classée (Bloquant, Critique, Mineur) et résolue avant la signature de réception.  

---

## 10. Maintenance et support  

| Niveau | Description | Délai d’intervention | SLA |
|--------|-------------|----------------------|-----|
| **Support de premier niveau** (Helpdesk) | Réponses aux questions utilisateurs, incidents mineurs. | 4 h ouvrées | 95 % de tickets résolus en < 8 h |
| **Support de second niveau** (DevOps) | Analyse des logs, redémarrage de conteneurs, correctifs. | 2 h ouvrées | 90 % des tickets résolus en < 24 h |
| **Support de tier niveau** (Évolution) | Déploiement de correctifs de sécurité, évolutions fonctionnelles. | 1 jour ouvré | 80 % des changements livrés dans le sprint prévu |
| **Disponibilité** | 24 /7 surveillance (Prometheus) | – | Disponibilité 99,9 % |

**Garantie** : 12 mois à compter de la date de mise en production, renouvelable.  

---

## 11. Livrables et planning  

| Jalons | Date cible | Livrable | Responsable |
|--------|-----------|----------|-------------|
| **Kick‑off** | J‑0 | CCTP signé | Maître d’ouvrage |
| **Livraison du code source** | J + 30 | Repositoire GitLab complet (tags v2.5.20) | Équipe Dev |
| **Livraison Docker‑Compose** | J + 35 | `docker‑compose.yml`, `.env.sample` | DevOps |
| **Livraison documentation** | J + 40 | Guide d’installation, d’exploitation, manuel utilisateur | Documentation |
| **Recette fonctionnelle** | J + 45 | Rapport de recette (signé) | MOA |
| **Recette de sécurité** | J + 48 | Rapport d’audit RGS, résultats ZAP/Trivy | SSI |
| **Mise en production** | J + 50 | Application en prod, bascule DNS | Ops |
| **Période de stabilisation** | J + 50 → J + 80 | Support de stabilisation | Support |
| **Fin de garantie** | J + 440 | Rapport de fin de garantie | MAO |

---

## 12. Contraintes légales et réglementaires  

| Domaine | Référence | Exigence |
|---------|-----------|----------|
| **Propriété intellectuelle** | Législation française, code source sous licence interne. | Le titulaire cède les droits d’utilisation, de modification et de maintenance au maître d’ouvrage. |
| **Licences tierces** | Spring 2.x (Apache 2.0), Struts 2 (Apache 2.0), Vertigo (LGPL‑2.1), BIRT (EPL 1.0), Talend (Apache 2.0). | Les licences doivent être respectées, les notices incorporées dans le livrable. |
| **RGPD** | Art. 30 RGPD – Registre des traitements | Le registre doit être fourni (format Excel ou CSV). |
| **RGS** | Décret 2019‑110 (niveau 2) | Conformité aux exigences de chiffrement, journalisation, contrôle d’accès. |
| **RGI** | Référentiel Général d’Interopérabilité – API REST | La future évolution doit être compatible. |
| **RGAA** | Accessibilité – niveau AA | Tous les écrans doivent passer le test axe‑core. |
| **Archivage** | Arrêté 2022‑102 (Données publiques) | Conservation des logs 2 ans, archivage de la BDD 5 ans (DUA). |
| **Sécurité** | ANSSI – Guide d’hygiène informatique | Mise à jour mensuelle des images Docker, analyse de vulnérabilité. |

---

## 13. Critères de sélection des offres  

| Critère | Pondération | Échelle | Points attribués |
|---------|-------------|--------|-----------------|
| **Conformité fonctionnelle (CCF)** | 30 % | 0‑10 pts | – |
| **Qualité du code (SonarQube)** | 20 % | 0‑10 pts | – |
| **Sécurité (RGS, tests d’intrusion)** | 20 % | 0‑10 pts | – |
| **Plan de transition / migration** | 10 % | 0‑10 pts | – |
| **Coût total (TCO 3 ans)** | 10 % | 0‑10 pts | – |
| **Valeur ajoutée (options S‑01 à S‑04)** | 10 % | 0‑10 pts | – |
| **Références similaires (public sector)** | 5 % | 0‑5 pts | – |
| **Délais de mise en œuvre** | 5 % | 0‑5 pts | – |

*Notation* : chaque critère est noté sur 10 pts (ou 5 pts). Le total maximal est 100 pts. Le **candidature** doit atteindre **≥ 70 pts** pour être retenue.

---

## 14. Annexes contractuelles  

| Annexe | Description |
|--------|-------------|
| **A – Glossaire** | Définitions (RGS, RGPD, RGI, Cerbère, etc.) |
| **B – Références normatives** | Liens vers les textes (décrets, RFC, ISO) |
| **C – Modèle de déclaration de conformité RGS** | Formulaire à retourner après recette |
| **D – Modèle de registre RGPD** | Tableur à compléter |
| **E – Tableau de suivi des livrables** | Gantt simplifié (exemple) |
| **F – Modèle de contrat de maintenance** | SLA, pénalités, durée, renouvellement |
| **G – Procédure de gestion des incidents** | SOP, escalade, reporting |
| **H – Modèle de rapport de test** | Structure (unitaires, fonctionnels, charge, sécurité) |
| **I – Checklist de réception** | Items à valider avant signature de réception |


---  

**Fait à Paris, le 27 avril 2026**  

*Le présent CCTP constitue le document contractuel de référence pour le marché public de fourniture, déploiement et maintenance de l’application SIREINES. Toute modification devra faire l’objet d’un avenant signé par les deux parties.*
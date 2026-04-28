# 📘 Dossier d’Architecture Technique (DAT) – **Causalis**  

*[Version du document : 2024‑04‑28 – Auteur : IA‑Architecte]*  

---  

## 📑 Sommaire  
[TOC]

---  

## 1️⃣ Introduction et objectifs  

### 1.1 Vue d’ensemble fonctionnelle  
Causalis est l’application ministérielle de **statistiques nationales sur les accidents du travail et les maladies professionnelles** des agents du ministère du Développement durable. Elle centralise les dossiers d’accidents et de maladies, produit des indicateurs statistiques et les expose aux gestionnaires de services, aux administrateurs nationaux et aux référents santé‑travail.  

### 1.2 Diagramme C4 – Niveau 1 (Contexte)  

```mermaid
graph LR
    subgraph Ext[Environnement externe]
        Users[Utilisateurs<br/>Gestionnaires, Admins] 
        Cerb[Cerbere SSO]
        WS[Web‑services externes<br/>(StubWS, Référentiels RH)]
        PSIN[Supervision PSIN]
        DB[(Base de données Oracle)]
    end
    Caus[Application Causalis<br/>(Struts 1 + Java 8)] 

    Users -->|authentification| Cerb;
    Cerb -->|jeton SSO| Caus;
    Caus -->|requêtes UI| Users;
    Caus -->|accès persistance| DB;
    Caus -->|appel WS| WS;
    Caus -->|exposition métriques| PSIN
```

### 1.3 Objectifs de qualité orientés utilisateur  

| # | Objectif | Raison métier |
|---|----------|---------------|
| **Q‑1** | **Performance** – temps de réponse < 2 s pour la création/consultation d’un dossier | Garantir la fluidité du travail des gestionnaires |
| **Q‑2** | **Sécurité** – authentification SSO, contrôle d’accès RBAC, chiffrement des sauvegardes | Conformité RGPD & exigences D‑I‑C‑T (Disponibilité, Intégrité, Confidentialité, Traçabilité) |
| **Q‑3** | **Maintenabilité** – couverture unitaires ≥ 80 % & documentation générée | Réduire le coût de la dette technique sur le long terme |
| **Q‑4** | **Scalabilité** – capacité à supporter + 200 utilisateurs simultanés | Anticiper l’évolution du nombre d’agents |
| **Q‑5** | **Usabilité** – interface Struts ergonomique, navigation à 3 clics max | Améliorer la productivité des utilisateurs finaux |

---  

## 2️⃣ Parties prenantes  

| Rôle | Responsable | Attente principale |
|------|--------------|---------------------|
| **MOA SSI** | SG/DRH/D/PSPP1 | Garantie de la conformité sécurité (D‑I‑C‑T) |
| **MOE Développeurs** | Équipe Causalis (voir § 6.1) | Livrer des évolutions fonctionnelles dans les délais |
| **Gestionnaires de service** | Managers (ex. Adrien DESSARTRE) | Saisie simple et fiable des dossiers |
| **Administrateurs nationaux** | SG/DNUM/PNM/DPNM3 | Supervision, sauvegarde, continuité de service |
| **Utilisateurs finaux** | Agents du ministère | Accès aux statistiques et aux dossiers |
| **Audit RGPD** | SG/DRH/D | Traçabilité des traitements de données personnelles |
| **Support & exploitation** | PSIN, Portail‑support | Monitoring, alerting, gestion des incidents |

---  

## 3️⃣ Contraintes  

### 3.1 Contraintes techniques  

| Domaine | Contraintes |
|---------|-------------|
| **Langage** | Java 8, compatible JDK 8‑212 |
| **Framework UI** | Struts 1.x (legacy) |
| **Persistance** | Castor JDO + Oracle 12c (JNDI `java:comp/env/jdbc/userDScausalis`) |
| **Gestion de projet** | Maven 3 + assembly plugin (ZIP de scripts, sources, docs) |
| **Conteneur** | Tomcat 6 (déploiement WAR) |
| **Supervision** | Prometheus/Grafana/Loki/Alertmanager + Portainer (containers) |
| **Sauvegarde** | Dump AES‑256 vers B3, Outscale SecNumCloud, Google Cloud |
| **Sécurité** | SSO Cerbere, filtrage RBAC, communication WS en HTTPS |
| **RGPD** | Traçabilité des accès, archivage à haute criticité, plan d’archivage |

### 3.2 Contraintes organisationnelles  

* Utilisation du **tenant `pnm3`** du cloud interne ECO4 (OpenStack).  
* Déploiement en **cluster ESXi** (plateforme ACAI – Java ACAI).  
* Respect du **processus de mise en production** (livraison via artefacts ZIP, validation par CI GitLab).  

### 3.3 Exigences de sécurité D‑I‑C‑T  

| Aspect | Exigence | Implémentation |
|--------|----------|----------------|
| **Disponibilité** | Redondance du serveur d’applications (2 nodes) | Load‑balancer Nginx en front (paires) |
| **Intégrité** | Vérification des checksums des scripts DB | SHA‑256 stocké dans CI |
| **Confidentialité** | Chiffrement des sauvegardes & des flux WS | AES‑256 + TLS 1.2 |
| **Traçabilité** | Journalisation des actions critiques (création/modif dossier) | Log4j + audit table `AUDIT_LOG` |

---  

## 4️⃣ Contexte et périmètre  

### 4.1 Systèmes / acteurs fonctionnels  

| Système | Type d’interaction | Protocole / fréquence |
|--------|-------------------|-----------------------|
| **Cerbere SSO** | Authentification unique | HTTP / HTTPS, appel à chaque session |
| **Référentiels RH (StubWS)** | Consultation de grades, services, etc. | SOAP/REST, appel ponctuel lors de la synchronisation |
| **Base Oracle** | Persistance des dossiers | JDBC via JNDI, requêtes transactionnelles |
| **Supervision PSIN** | Métriques d’usage & health‑check | Export Prometheus (`/metrics`) toutes les 30 s |
| **Portainer** | Gestion des conteneurs Docker (si utilisé) | API Docker, monitoring continu |
| **Système de sauvegarde** | Extraction journalière des dumps | Job cron, chiffrement, push vers 3 stockages |

### 4.2 Interfaces techniques  

| Interface | Direction | Format | Exemple |
|----------|-----------|--------|----------|
| `web.xml` ↔ `Struts‑actions` | Entrée HTTP | `application/x-www-form-urlencoded` |
| DAO ↔ Oracle | JDBC | `SELECT … FROM ACCIDENT WHERE …` |
| Service ↔ WS | SOAP (WSDL) | `GradeService.getAllGrades()` |
| App ↔ Prometheus | HTTP GET | `/metrics` (exposé par `MetricsServlet`) |
| App ↔ Nginx | HTTP/HTTPS (load‑balancing) | `https://causalis.e2.rie.gouv.fr` |

---  

## 5️⃣ Stratégie de solution  

### 5.1 Décisions architecturales majeures  

| Décision | Motif |
|----------|-------|
| **Struts 1.x + Castor JDO** | Héritage historique, contraintes de migration (budget limité). |
| **Maven Assembly** | Packaging standardisé (scripts DB, sources, docs) pour la livraison. |
| **Nginx + Load‑balancer** | Haute disponibilité & répartition du trafic. |
| **Sauvegarde multi‑cloud** | Redondance géographique et conformité SecNumCloud. |
| **SSO Cerbere** | Centralisation de l’identité ministérielle, conformité RGPD. |

### 5.2 Environnement technologique  

| Couche | Technologie | Version / Référence |
|--------|--------------|---------------------|
| **Langage** | Java | 8 (JDK 1.8.0_212) |
| **Web UI** | Struts 1.x + JSP | 1.3.10 |
| **Persistance** | Castor JDO + Oracle | Castor 1.3, Oracle 12c |
| **Serveur d’applications** | Tomcat | 6.0.53 |
| **Reverse‑proxy** | Nginx (2 instances) | 1.18 |
| **Supervision** | Prometheus 2.x, Grafana 8.x, Loki 2.x, Alertmanager 0.23 |
| **CI/CD** | GitLab CI | Pipelines Maven (`mvn clean install`, `assembly:single`) |
| **Gestion de configuration** | XML (`database.xml`, `web.xml`, `pom.xml`) + `.properties` |
| **Conteneurisation (optionnel)** | Docker (Portainer) | 20.10 |

### 5.3 Outils de la forge logicielle  

| Outil | Usage |
|-------|-------|
| **Maven** | Compilation, dépendances, assembly ZIP |
| **GitLab CI** | Build, tests unitaires, génération artefacts |
| **SonarQube** | Analyse qualité (`sonar-project.properties`) |
| **Jenkins** | (historique) pipeline de déploiement automatisé |
| **Portainer** | Supervision des conteneurs Docker (si utilisé) |
| **Prometheus / Grafana** | Métriques d’application & alerting |
| **Log4j** | Journalisation applicative |
| **Cerbere SDK** | Gestion du SSO et du log‑off |

---  

## 6️⃣ Vue en Briques (C4 – Niveau 2)  

```mermaid
containerDiagram;
    title Causalis – Vue en Briques (C4 L2)

    boundary "Cluster ACAI – Paris La Défense" {
        node "Nginx LB (2×)" as Nginx {
            direction TB;

        node "Tomcat (2×)" as Tomcat {
            direction TB;

        component "Web UI (Struts 1.x)" as UI {
            direction TB;

        component "Service Layer (Java)" as Service {
            direction TB;

        component "DAO Layer (Castor JDO)" as DAO {
            direction TB;

        database "Oracle DB\n(userDScausalis)" as Oracle {
            direction TB;

        component "WS Client (StubWS)" as WS {
            direction TB;

        component "Metrics Exporter\n(Prometheus)" as Metrics {
            direction TB;

    Nginx --> Tomcat : HTTP/HTTPS;
    Tomcat --> UI : Servlets / JSP;
    UI --> Service : appels Java;
    Service --> DAO : JDO / Castor;
    DAO --> Oracle : JDBC;
    Service --> WS : SOAP/REST;
    Service --> Metrics : /metrics;
    UI --> Cerbere : SSO (HTTP Header)
```

### 6.1 Description des briques  

| Brique | Responsabilité | Principaux artefacts |
|--------|----------------|----------------------|
| **Nginx LB** | Répartition du trafic, terminaison TLS | `nginx.conf` (non versionné) |
| **Tomcat** | Héberge le WAR `causalis-web` | `causalis-web.war` (généré par Maven) |
| **Web UI** | Pages JSP, Struts Actions, TagLibs | `*.jsp`, `*.action`, `StrutsOptionTag` |
| **Service Layer** | Logique métier, orchestration DAO, appels WS | `*Service.java` (ex : `GradeService`, `SynchronizeService`) |
| **DAO Layer** | Accès aux tables via Castor JDO | `GenericDao<T>`, `GradeDao`, `DossierAccidentDAO` |
| **Oracle DB** | Persistance des entités métier | Tables `ACCIDENT`, `GRADE`, `SERVICE`, … |
| **WS Client** | Synchronisation avec référentiels externes (grades, services) | `WSClientGrade`, `TranscodageGradePredicate` |
| **Metrics Exporter** | Publication des métriques d’usage | `MetricsServlet`, `prometheus.yml` |

---  

## 7️⃣ Vue Exécution (Scénarios critiques)  

### 7.1 Scénario 1 – Création d’un dossier d’accident  

1. **Authentification** – L’utilisateur (Gestionnaire) se connecte via **Cerbere SSO** → jeton SSO stocké en session.  
2. **Accès UI** – L’utilisateur ouvre le formulaire `DossiersAction` → Struts Action charge les listes de référence (`GradeService`, `ServiceService`).  
3. **Saisie** – Le gestionnaire remplit le formulaire `DossiersForm` et soumet.  
4. **Validation** – `DossiersForm.validateEmptyFields()` vérifie la complétude → en cas d’erreur, `ActionWarning` affiché.  
5. **Persistence** – `EffectifService` (ou `DossierAccidentService`) appelle le DAO `GenericDao` → Castor crée l’entité `DossierAccident` et persiste via Oracle.  
6. **Audit** – Log4j enregistre l’événement (`CREATE_DOSSIER_ACCIDENT`) avec l’identifiant utilisateur.  
7. **Réponse** – L’Action renvoie la vue `dossiers.jsp` avec le nouveau dossier affiché.  

#### Points de contrôle  

| Étape | Vérification | Métrique |
|-------|--------------|----------|
| Authentification | Jeton SSO valide (signature, expiration) | ≤ 5 ms |
| Validation UI | Aucun champ obligatoire vide | 0 warnings |
| Persistance | Commit transaction Oracle | ≤ 150 ms |
| Audit | Enregistrement dans `AUDIT_LOG` | ≤ 10 ms |
| Retour UI | Temps total ≤ 2 s | KPI de performance |

---

### 7.2 Scénario 2 – Synchronisation des grades avec le référentiel externe  

1. **Planification** – Un job Quartz (ou Cron) déclenche `SynchronizeService.synchronize()`.  
2. **Récupération** – `GradeService.getAllGrade()` interroge la base locale (filtre `util = 1`).  
3. **Appel WS** – `WSClientGrade` récupère la liste des grades du système externe.  
4. **Filtrage** – `TranscodageGradePredicate` décide quels grades n’existent pas en base.  
5. **Insertion** – `TranscodageGradeService` crée les nouvelles lignes (`INSERT`) via DAO.  
6. **Reporting** – Le nombre de lignes insérées est loggé et exposé via `/metrics` (`grades_synced_total`).  

#### Points de contrôle  

| Étape | Risque | Mitigation |
|-------|--------|------------|
| Appel WS | Timeout / indisponibilité du service externe | Circuit‑breaker, retry avec back‑off |
| Insertion DB | Violation d’unicité | Vérification pré‑existence (`isPresent`) |
| Reporting | Perte de métriques | Export Prometheus avec labels `success/failure` |

---

### 7.3 Scénario 3 – Génération du rapport statistique mensuel  

1. **Planification** – Job mensuel invoque `StatistiquesService`.  
2. **Agrégation** – DAO exécute des requêtes agrégées (`GROUP BY`) sur les tables `ACCIDENT`, `DOSSIER_MALADIE`.  
3. **Export** – `CausalisExportManager` crée un fichier OpenOffice (`.odt`) via `FichierOpenOffice`.  
4. **Archivage** – Le fichier est stocké dans le système de fichiers partagé et référencé dans la base (`ExportDonnees`).  
5. **Notification** – Un email (via `MailService`) est envoyé aux managers avec le lien de téléchargement.  

#### Points de contrôle  

| Étape | Vérification | KPI |
|-------|--------------|-----|
| Agrégation | Résultats cohérents (checksum) | Différence < 0,1 % vs. précédent mois |
| Export | Fichier produit sans erreur | Taille > 0 KB, validité ODT |
| Notification | Email délivré (SMTP 200) | Taux de délivrabilité = 100 % |

---  

## 8️⃣ Vue Déploiement *(section standardisée)*  

### 8.1 Environnements  

| Environnement | Hébergement | Serveurs | Réseau | Particularités |
|---------------|-------------|----------|--------|----------------|
| **Développement** | Cloud interne ECO4 – tenant `pnm3` | 1 VM Tomcat 6 + 1 VM Nginx | VLAN DEV | Base de données sandbox, logs en mode DEBUG |
| **Recette** | Cloud interne ECO4 – tenant `pnm3` | 2 VM Tomcat 6 (cluster) + 2 VM Nginx (HA) | VLAN RECETTE | Sauvegarde quotidienne, jeux de données anonymisés |
| **Production** | Centre‑serveur ministériel **Paris La Défense** (ACAI) | 2 VM Tomcat 6 (clusters ESXi) + 2 VM Nginx (load‑balancer) | VLAN PROD | TLS 1.2, sauvegarde AES‑256, monitoring PSIN, alerting Prometheus |

### 8.2 Infrastructure  

Le produit est hébergé sur le **cloud interne ECO4** basé sur OpenStack, dans le tenant `pnm3` du département.  
Le reverse‑proxy Nginx du schéma ci‑dessus est en fait une **paire de Nginx load‑balancés** en frontal des produits hébergés sur le tenant.

```mermaid
graph TD
    A[Nginx (LB) - Pair] --> B[Tomcat (Cluster) - Causalis Web]
    B --> C[Oracle DB (JNDI datasource)]
    B --> D[StubWS (External Grade Service)]
    B --> E[Prometheus / Grafana / Loki]
```

### 8.3 Supervision  

Le produit est supervisé via le système standard du GTI pour ce faire :  

- **Portainer** – gestion des conteneurs (si Docker est utilisé).  
- **Stack Prometheus / Grafana / Loki / AlertManager** – collecte des métriques, logs, alertes.  
- **Supervision PSIN** – monitoring applicatif dédié aux applications ministérielles.  

### 8.4 Sauvegardes  

Les sauvegardes de la base de données sont assurées par des scripts standards du GTI permettant la création de dumps cryptés en **AES‑256** et déposés sur :  

- le stockage objet **B3** du IaaS ministériel,  
- le stockage objet **Outscale SecNumCloud** (prestation « Nuage Public »),  
- le stockage objet standard de **Google Cloud** (prestation « Nuage Public »).  

---  

## 9️⃣ Sujets transverses  

| Sujet | Implémentation | Référence |
|-------|----------------|------------|
| **Authentification** | SSO Cerbere (jeton JWT) – filtre `CerbereAuthenticationFilter` | `reauth.jsp` |
| **Journalisation** | Log4j 2 configuré via `log4j.xml` – logs séparés INFO/ERROR/WARN | `src/main/resources/log4j.xml` |
| **Monitoring** | Exporter Prometheus (`/metrics`) via `MetricsServlet` | `src/main/java/.../MetricsServlet.java` (non affiché) |
| **Gestion des erreurs** | `ActionWarning` DTO + page `erreur.jsp` | `src/main/webapp/erreur.jsp` |
| **API interne** | `WSConstants` (end‑points) et `WSClient*` | `src/main/java/i2/application/causalis/ws/client/*.java` |
| **Sécurité des données** | Chiffrement des sauvegardes, TLS 1.2, validation côté serveur | `database.xml`, `web.xml` |
| **Internationalisation** | Fichiers `ApplicationResources.properties` (i18n) | `src/main/resources/ApplicationResources.properties` |
| **Gestion de la pagination** | Propriété `pagination.max=30` | `project.properties` |
| **Déploiement continu** | GitLab CI (`.gitlab-ci.yml`) → artefacts Maven → dépôt Nexus | `.gitlab-ci.yml` |

---  

## 🔟 Exigences de qualité  

| Exigence | Critère d’acceptation | Test de validation |
|----------|-----------------------|----------------------|
| **Performance** | Temps de réponse < 2 s pour création/consultation d’un dossier | Tests de charge JMeter (100 utilisateurs simultanés) |
| **Sécurité** | Aucun accès non‑autorisé détecté (OWASP Top 10) | Scan SAST (SonarQube) + DAST (OWASP ZAP) |
| **Disponibilité** | 99,5 % de disponibilité mensuelle | Monitoring via Prometheus, alertes SLA |
| **Intégrité des données** | Aucun `INSERT` dupliqué, contraintes DB respectées | Tests d’intégrité DB (FK, UQ) |
| **Traçabilité** | Chaque action critique auditée dans `AUDIT_LOG` | Vérification des logs + requêtes de contrôle |
| **Maintenabilité** | Couverture unitaires ≥ 80 % et documentation Javadoc générée | SonarQube coverage, Javadoc plugin |
| **Scalabilité** | Le cluster supporte + 200 sessions simultanées sans dégradation | Test de montée en charge + scaling du cluster |

---  

## 1️⃣1️⃣ Risques et dettes techniques  

| Risque / Dette | Impact | Probabilité | Mesure corrective / atténuation |
|----------------|--------|--------------|---------------------------------|
| **Technologies obsolètes** (Struts 1, Castor JDO, Tomcat 6) | Difficulté de maintenance, manque de support, vulnérabilités | Élevée | Plan de migration vers Spring Boot + JPA/Hibernate, mise à jour du serveur d’applications (Tomcat 9) |
| **Absence de tests unitaires sur plusieurs services** | Régression fonctionnelle | Moyenne | Augmenter la couverture tests (JUnit 5, Mockito) et intégrer dans le pipeline CI |
| **DAO incomplets** (`RechercheDossiersMaladiesDAO` vide) | NPE en production | Faible | Implémenter les méthodes ou retirer les références |
| **Dépendance à Cerbere SSO** | Blocage si le service est indisponible | Moyenne | Implémenter un fallback local (cache JWT) et surveiller la disponibilité du SSO |
| **Sauvegarde multi‑cloud** | Complexité de restauration | Moyenne | Documenter le processus de restauration, automatiser les tests de restauration |
| **Gestion des versions de scripts DB** | Incohérence de schéma entre environnements | Faible | Versionner les scripts (Flyway/ Liquibase) et automatiser les migrations |
| **Déploiement manuel du manifeste (`StubWS.jar`)** | Omission en prod → appels WS cassés | Faible | Ajouter `StubWS.jar` comme dépendance Maven et le publier dans Nexus |

---  

## 1️⃣2️⃣ Annexes  

### 12.1 Glossaire  

| Terme | Définition |
|-------|------------|
| **SSO** | Single Sign‑On – authentification unique via Cerbere. |
| **RBAC** | Role‑Based Access Control – contrôle d’accès basé sur les rôles. |
| **D‑I‑C‑T** | Disponibilité, Intégrité, Confidentialité, Traçabilité – modèle de sécurité. |
| **ACAI** | Plateforme d’hébergement ministérielle (Java ACAI, clusters ESXi). |
| **PSIN** | Plateforme de supervision ministérielle. |
| **Nginx LB** | Load‑balancer Nginx en mode reverse‑proxy. |
| **StubWS** | Bibliothèque client (JAR) pour les web‑services externes. |
| **Prometheus Exporter** | Endpoint HTTP exposant les métriques au format Prometheus. |
| **DAO** | Data Access Object – couche d’accès aux données. |
| **DTO** | Data Transfer Object – objet de transport de données. |

### 12.2 Décisions d’Architecture (ADR)  

| ADR # | Décision | Contexte | Conséquence |
|------|----------|----------|-------------|
| **ADR‑001** | Conserver Struts 1.x | Application en production depuis 2004, budget limité pour refonte immédiate. | Maintien du code existant, mais plan de migration à moyen terme. |
| **ADR‑002** | Utiliser Castor JDO | Historique du projet, mapping XML déjà présent. | Simplicité d’intégration, mais risque d’obsolescence. |
| **ADR‑003** | Packager avec Maven Assembly | Besoin d’artefacts ZIP (scripts DB, sources, docs) pour la chaîne CI/CD. | Processus de livraison reproductible. |
| **ADR‑004** | Sécuriser les sauvegardes avec AES‑256 | Exigence de protection des données personnelles (RGPD). | Coût de chiffrement acceptable, conformité assurée. |
| **ADR‑005** | Déployer en cluster ACAI (ESXi) | Niveau de disponibilité requis (99,5 %). | Haute disponibilité, mais dépendance à l’infrastructure ministérielle. |

---  

## 📌 Conclusion  

Le DAT présenté décrit **Causalis** comme une solution d’entreprise fiable, mais reposant sur un socle technologique vieillissant. Les objectifs de performance, de sécurité et de maintenabilité sont clairement définis, tout comme les contraintes réglementaires (RGPD, D‑I‑C‑T).  

Les principaux leviers d’évolution sont :  

1. **Modernisation du stack** (migration Struts 1 → Spring Boot, Castor JDO → JPA).  
2. **Renforcement de la couverture de tests** (unitaires, d’intégration, de charge).  
3. **Automatisation du déploiement** (Infrastructure‑as‑Code, Helm/K8s si migration hors ACAI).  

En suivant ces axes, Causalis pourra garantir la continuité du service tout en réduisant sa dette technique et en améliorant la satisfaction de ses utilisateurs.  

---  

*Fin du Dossier d’Architecture Technique*  
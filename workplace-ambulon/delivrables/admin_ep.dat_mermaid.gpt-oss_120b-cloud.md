[TOC]

# 1. Introduction et objectifs {#introduction}
**Admin EP** est une application web qui centralise les listes des membres des conseils d’administration des établissements publics du ministère de la Transition écologique.  
Elle permet :

* la saisie manuelle des mandats,  
* l’alimentation automatique à partir du Journal Officiel (« JORF »),  
* la consultation, la recherche et la visualisation de statistiques,  
* la génération d’alertes de fin de mandat.

## 1.1 Schéma C4 – Niveau 1 (Contexte) {#c4-l1}
```mermaid
graph LR;
    Utilisateurs[Utilisateurs (SPES, DG de tutelle, Opérateurs)] -->|HTTPS| WebApp[Admin EP (Tomcat + Struts2)]
    WebApp -->|JDBC| DB[(PostgreSQL)]
    WebApp -->|HTTPS| Auth[Service Cerbère (SSO)]
    WebApp -->|HTTPS| JORF[Source JORF (OpenData)]
    WebApp -->|HTTPS| ES[Elasticsearch (full‑text search)]
    Monitoring[Prometheus/Grafana] --> WebApp;
    Monitoring --> DB
```

## 1.2 Objectifs de qualité orientés utilisateur {#objectifs}
| # | Objectif | Raison métier |
|---|----------|---------------|
| 1 | **Disponibilité ≥ 99,5 %** | L’accès aux mandats doit être possible à tout moment pour les services de tutelle. |
| 2 | **Confidentialité des données personnelles** | Conformité au RGPD et à l’évaluation DICT. |
| 3 | **Temps de réponse < 2 s** pour les recherches | Garantir une expérience fluide aux utilisateurs. |
| 4 | **Facilité de maintenance** (code documenté, tests unitaires > 80 %) | Réduire le coût de la montée de version (Tomcat 10 / PostgreSQL 15). |
| 5 | **Traçabilité des modifications** (audit log) | Satisfaire les exigences de traçabilité (D‑I‑C‑T). |

[↩ Retour au sommaire](#toc)

---

# 2. Parties prenantes {#parties-prenantes}
| Rôle | Attente principale |
|------|--------------------|
| **Maîtrise d’ouvrage (MOA) – SG/SPES** | Livraison d’une application fiable, conforme aux exigences légales et fonctionnelles. |
| **Maîtrise d’œuvre (MOE) – SG/SNUM/PNM/DPNM3/BPN** | Gestion du cycle de vie (déploiement, exploitation, évolutions). |
| **Prestataire – CGI** | Respect des délais de développement et de la documentation technique. |
| **Utilisateurs finaux – SPES, DG de tutelle, opérateurs** | Interface ergonomique, recherche rapide, alertes fiables. |
| **Équipe Sécurité (Cerbère)** | Gestion des habilitations, conformité DICT. |
| **Équipe Supervision (PSIN)** | Visibilité en temps réel de la disponibilité et de la santé de l’application. |

[↩ Retour au sommaire](#toc)

---

# 3. Contraintes {#contraintes}
## 3.1 Contraintes techniques
* **Langage** : Java 8 (prévu de migrer vers Java 11).  
* **Serveur d’applications** : Tomcat 9.0.8 (migration vers Tomcat 10 prévue).  
* **Base de données** : PostgreSQL 9.6.11 (migration vers PostgreSQL 15 en projet).  
* **Conteneurisation** : Docker / Kubernetes en cours de mise en place (ECO4).  
* **Recherche plein texte** : Elasticsearch (configuration `elasticsearch.yml`).  
* **Authentification unique** : Cerbère (SSO).  

## 3.2 Contraintes organisationnelles
* **Processus de mise en production** : validation via la chaîne GitLab CI/CD, puis déploiement sur l’infrastructure ECO4 (tenant `pnm3`).  
* **Montée de version Tomcat/PostgreSQL** : doit être réalisée sans interruption de service (fenêtre de maintenance < 2 h).  

## 3.3 Contraintes réglementaires (modèle D‑I‑C‑T)
| Axe | Exigence | Implémentation |
|-----|----------|----------------|
| **Disponibilité** | ≥ 99,5 % (SLA) | Redondance Nginx + Tomcat en mode cluster, backup base. |
| **Intégrité** | Garantie d’atomicité des transactions | Utilisation de transactions JDBC, contraintes de clé étrangère. |
| **Confidentialité** | Chiffrement des données en transit & au repos | TLS 1.2+ sur HTTPS, chiffrement AES‑256 des dumps de sauvegarde. |
| **Traçabilité** | Historisation des actions administratives | Table `audit_log` + log4j2 configuré en mode `JSON`. |

[↩ Retour au sommaire](#toc)

---

# 4. Contexte et périmètre {#contexte}
## 4.1 Périmètre fonctionnel
* **Interface d’écriture** – saisie manuelle des administrateurs et mandats.  
* **Alimentation automatique** – extraction des mentions JORF via le service `ArticleAnalyser`.  
* **Consultation** – recherche multi‑critères (nom, établissement, mandat).  
* **Statistiques** – tableau de bord (nombre de mandats, échéances).  
* **Alertes** – envoi de mail aux référents lorsqu’un mandat arrive à échéance.  

## 4.2 Interfaces techniques
| Interface | Protocole | Format | Fréquence |
|-----------|-----------|--------|-----------|
| Front‑end ↔ Back‑end | HTTPS (REST / Struts2) | JSON / HTML | À la demande |
| Application ↔ PostgreSQL | JDBC | SQL | Transactionnel |
| Application ↔ Elasticsearch | HTTP | JSON | À la demande (indexation) |
| Application ↔ JORF | HTTPS | XML / HTML | Tous les jours (cron) |
| Application ↔ Cerbère | SAML / OAuth2 | Token | À chaque login |
| Supervision ↔ Application | HTTP | Prometheus metrics | Scraping chaque 30 s |

[↩ Retour au sommaire](#toc)

---

# 5. Stratégie de solution {#strategie}
## 5.1 Décisions d’architecture majeures
| Décision | Motif |
|----------|-------|
| **Monolithe Java (Struts2 + JSP)** | Historique du projet, faible besoin de découplage externe. |
| **Déploiement containerisé (Docker)** | Uniformiser les environnements (dev / recette / prod) et faciliter la montée de version. |
| **Reverse‑proxy Nginx** | Gestion du TLS, équilibrage de charge et redirection vers plusieurs instances Tomcat. |
| **Mise en place d’un job Quartz** | Génération quotidienne des alertes de fin de mandat. |
| **Utilisation de Maven Assembly** | Packaging du code SQL et du WAR dans un artefact unique. |

## 5.2 Stack technologique
| Couche | Technologie | Version |
|--------|-------------|---------|
| **Langage** | Java | 8 (prévu 11) |
| **Framework web** | Struts 2, Vertigo, Vertigo‑Vega | – |
| **Serveur d’applications** | Tomcat | 9.0.8 (migration 10) |
| **Base de données** | PostgreSQL | 9.6.11 (migration 15) |
| **Recherche** | Elasticsearch | 7.x (config `elasticsearch.yml`) |
| **CI/CD** | GitLab CI, Maven, Docker | – |
| **Supervision** | Prometheus + Grafana + Loki + AlertManager | – |
| **Logs** | Log4j2 (XML) | – |
| **Authentification** | Cerbère (SSO) | – |
| **Sauvegarde** | Scripts GTI → dumps AES‑256, stockage B3, Outscale SecNumCloud, Google Cloud | – |

## 5.3 Outils de la forge logicielle
* **Gestion de code** – GitLab (repo `admin_ep`).  
* **Build** – Maven (`pom.xml` à la racine et dans chaque module).  
* **Tests** – JUnit, Mockito, Selenium (tests UI).  
* **Déploiement** – Docker images stockées dans le registre interne, déploiement via Helm (ECO4).  
* **Qualité** – SonarQube, Checkstyle.

[↩ Retour au sommaire](#toc)

---

# 6. Vue en briques (C4 – Niveau 2) {#c4-l2}
```mermaid
graph LR;
    subgraph DMZ;
        Nginx[Nginx (Reverse‑proxy)]
    end;
    subgraph APP;
        Tomcat[Tomcat (Webapp WAR)]
        Scheduler[Quartz Scheduler (Alertes)]
        Auth[Filter Cerbère (SSO)]
    end;
    subgraph DB;
        PG[PostgreSQL]
        ES[Elasticsearch]
    end;
    subgraph EXT;
        JORF[Source JORF (HTTPS)]
        PSIN[Supervision PSIN]
    end;
    Nginx --> Tomcat;
    Tomcat --> Auth;
    Tomcat --> PG;
    Tomcat --> ES;
    Scheduler --> PG;
    Scheduler --> Mail[SMTP (mail d’alerte)]
    JORF --> Tomcat : extraction JORF (cron)
    PSIN --> Nginx : health‑check
```

* **Nginx** : load‑balancing, TLS termination.  
* **Tomcat** : conteneur d’exécution du WAR `admin_ep.war`.  
* **PostgreSQL** : persistance des entités (`ADMIN`, `MANDAT`, `CHARGE`, …).  
* **Elasticsearch** : indexation des textes JORF pour la recherche plein texte.  
* **Quartz Scheduler** : job quotidien d’analyse JORF et d’envoi d’alertes.  
* **Cerbère** : filtre d’authentification SSO.  

[↩ Retour au sommaire](#toc)

---

# 7. Vue exécution {#execution}
## 7.1 Scénario 1 – Création d’un mandat administrateur
```mermaid
sequencediagram;
    participant U as Utilisateur;
    participant UI as Front‑end (JSP/Struts)
    participant S as Tomcat;
    participant DB as PostgreSQL;
    participant A as AuditLog;
    U->>UI: Saisie du formulaire “Nouvel administrateur”
    UI->>S: POST /admin/UpsertAdminAction;
    S->>DB: INSERT ADMIN + INSERT MANDAT (transaction)
    DB-->>S: OK;
    S->>A: INSERT audit_log (action=CREATE_ADMIN)
    A-->>S: OK;
    S-->>UI: Redirection vers page de confirmation;
    UI-->>U: Affichage “Mandat créé”
```

* **Critère de validation** : la transaction doit être atomique ; aucun enregistrement partiel ne doit persister.  

## 7.2 Scénario 2 – Notification d’échéance de mandat (job quotidien)
```mermaid
sequencediagram;
    participant S as Scheduler (Quartz)
    participant DB as PostgreSQL;
    participant M as MailServer;
    participant L as Log4j2;
    S->>DB: SELECT mandats WHERE date_fin < now() + 7 days AND not_notified;
    DB-->>S: Liste des mandats à notifier;
    loop pour chaque mandat;
        S->>M: SEND mail (référent)
        S->>DB: UPDATE mandat SET notifié = true;
        S->>L: LOG "Mandat X notifié"
    end
```

* **Critère de validation** : chaque mandat doit générer exactement un e‑mail et être marqué comme notifié.  

[↩ Retour au sommaire](#toc)

---

# 8. Vue Déploiement {#deployment}
## 8.1 Environnements
| Environnement | Hébergement | Serveurs | Réseau | Particularités |
|---------------|-------------|----------|--------|----------------|
| **Développement** | ECO4 – tenant `pnm3-dev` | 1 × Docker / Tomcat (dev) | VLAN 10 | Base de données remplie avec jeux de données fictifs. |
| **Recette** | ECO4 – tenant `pnm3-recette` | 2 × Docker / Tomcat (cluster) | VLAN 20 | Tests d’intégration automatisés, sauvegarde quotidienne. |
| **Production** | ECO4 – tenant `pnm3` (MSP) | 3 × Docker / Tomcat (HA) + Nginx LB | VLAN 30 | TLS 1.2+, sauvegarde chiffrée AES‑256, monitoring Prometheus. |

### 8.2 Infrastructure
```mermaid
graph TD;
    N[Nginx LB] --> T1[Tomcat‑01]
    N --> T2[Tomcat‑02]
    N --> T3[Tomcat‑03]
    T1 --> PG[PostgreSQL (HA)]
    T2 --> PG;
    T3 --> PG;
    T1 --> ES[Elasticsearch]
    T2 --> ES;
    T3 --> ES;
    PG --> B3[Stockage objet B3 (backup)]
    PG --> Outscale[Outscale SecNumCloud]
    PG --> GCS[Google Cloud Storage]
```

* **Reverse‑proxy Nginx** : deux instances en haute disponibilité.  
* **Base de données** : réplication streaming, snapshots quotidiens.  
* **Elasticsearch** : cluster à trois nœuds, index dédié `jorf`.  

### 8.3 Supervision
* **Prometheus** : métriques Tomcat, PostgreSQL, Nginx, Elasticsearch.  
* **Grafana** : tableaux de bord “Disponibilité”, “Temps de réponse”.  
* **Loki + AlertManager** : agrégation des logs, alertes sur les erreurs 5xx.  
* **PSIN** : supervision métier (tableau de bord PSIN).  

### 8.4 Sauvegardes
* Sauvegarde quotidienne des bases (dump chiffré AES‑256).  
* Réplication des dumps sur trois stockages : B3, Outscale SecNumCloud, Google Cloud.  

[↩ Retour au sommaire](#toc)

---

# 9. Sujets transverses {#transverses}
| Sujet | Implémentation |
|-------|----------------|
| **Authentification** | Filtre `SecurityFilter` (package `io.vertigo.vega.impl.servlet.filter`) qui délègue à Cerbère via SAML/OAuth2. |
| **Journalisation** | `log4j2.xml` : appender JSON → Loki, rotation journaux toutes les 10 Mo. |
| **Monitoring** | Métriques exposées via `/actuator/metrics` (Spring‑Boot‑like) et scrappées par Prometheus. |
| **Gestion des erreurs** | `ErrorHandler` (package `fr.gouv.e2.baseadmin.errorhandler`) renvoie les pages `application-error.jsp`. |
| **API REST** | End‑points Struts2 exposés en JSON pour les modules front‑end et l’outil d’alimentation JORF. |
| **Sécurité des données** | Chiffrement des backups, TLS 1.2+ sur toutes les communications externes. |
| **Internationalisation** | `I18nResourcesInitializer` charge les bundles de messages. |
| **Gestion de la configuration** | Fichiers `application-config.xml`, `baseadmin-auth-config.xml`, `elasticsearch.yml`. |
| **Plan de continuité** | Procédure de bascule du cluster Nginx + Tomcat, restauration des dumps. |

[↩ Retour au sommaire](#toc)

---

# 10. Exigences de qualité {#qualite}
| Exigence | Scénario de validation |
|----------|------------------------|
| **Disponibilité ≥ 99,5 %** | Analyse des métriques `up_time` sur Prometheus pendant 30 jours, calcul du pourcentage d’indisponibilité. |
| **Temps de réponse < 2 s** | Test de charge (`k6` ou `JMeter`) sur le endpoint `/admin/recherche` avec 100 concurrents, vérifier que le 95ᵉ percentile ≤ 2 s. |
| **Confidentialité** | Scan de vulnérabilité OWASP ZAP : aucune fuite de données sensibles (ex. : mots de passe, tokens). |
| **Intégrité transactionnelle** | Test d’insertion d’un mandat avec rollback forcé, vérifier qu’aucune ligne n’est créée dans les tables `admin`/`mandat`. |
| **Traçabilité** | Vérifier que chaque action critique (création, modification, suppression) génère un enregistrement dans `audit_log` avec horodatage et identifiant utilisateur. |
| **Couverture de tests > 80 %** | Rapport SonarQube – couverture unitaires + intégration. |
| **Gestion des alertes d’échéance** | Simuler un mandat à J‑5, exécuter le job Quartz, vérifier l’envoi d’un mail et la mise à jour du flag `notifié`. |

[↩ Retour au sommaire](#toc)

---

# 11. Risques et dettes techniques {#risques}
| Risque | Impact | Action d’atténuation |
|--------|--------|----------------------|
| **Montée de version Tomcat → 10** | Rupture de compatibilité avec Struts2 (API Jakarta). | Planifier un sprint de migration, tests d’intégration avant la fenêtre de production. |
| **Migration PostgreSQL → 15** | Incompatibilité de fonctions PL/pgSQL, perte de performances. | Réaliser une migration sur l’environnement de recette, valider les scripts `pg_dump/restore`. |
| **Conteneurisation incomplète** | Déploiements manuels encore nécessaires, dérive de configuration. | Finaliser les Dockerfiles, automatiser le build via GitLab CI, ajouter des tests de conformité Docker. |
| **Dépendance à Cerbère** | Blocage d’accès si le service SSO tombe. | Implémenter un fallback “mode maintenance” avec authentification locale temporaire. |
| **Endettement du code legacy (Struts2, JSP)** | Difficulté à introduire de nouvelles fonctionnalités, faibles couvertures de tests. | Refactoriser progressivement les modules critiques (ex. : service mandat) en Spring Boot. |
| **Sauvegarde hors site** | Risque de perte de données en cas de sinistre du data‑center. | Ajouter une réplication journalière vers un bucket S3/Google Cloud (déjà en place). |
| **Charge JORF** | Extraction massive peut saturer le réseau. | Limiter la fréquence (once per day), mettre en cache les résultats. |

[↩ Retour au sommaire](#toc)

---

# 12. Annexes {#annexes}
## 12.1 Glossaire
| Terme | Définition |
|-------|------------|
| **Cerbère** | Service d’authentification unique (SSO) du ministère. |
| **ECO4** | Cloud interne du ministère (OpenStack) – tenant `pnm3`. |
| **ACAI** | Plateforme d’exécution Java du ministère (clusters ESXi). |
| **PSIN** | Plateforme de supervision métier du ministère. |
| **Mandat** | Période de mandat d’un administrateur (titulaire ou suppléant). |
| **DI​CT** | Délégation à l’Information et à la Communication – évaluation sécurité. |
| **D‑I‑C‑T** | Modèle de sécurité : Disponibilité, Intégrité, Confidentialité, Traçabilité. |

## 12.2 Décisions d’architecture (ADR) – Exemple
**ADR‑001 – Choix du déploiement containerisé**  
*Contexte* : L’application était historiquement déployée sur des serveurs VM classiques.  
*Décision* : Emballer le WAR et la base de données dans des conteneurs Docker et les orchestrer avec Kubernetes (ECO4).  
*Conséquence* : Uniformisation des environnements, simplification des montées de version, besoin de gérer la persistance (volumes, snapshots).  

[↩ Retour au sommaire](#toc)
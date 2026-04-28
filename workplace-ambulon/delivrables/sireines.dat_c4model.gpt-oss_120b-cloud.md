# 📦 Dossier d’Architecture Technique (DAT) – **SIREINES**  
*Version : 2.5.20 (12 / 03 / 2024)*  

[TOC]

---  

## 1️⃣ Introduction et objectifs  

**SIREINES** est une application métier Java/J2EE qui recense, suit et pilote les demandes de qualification d’experts et spécialistes scientifiques et techniques.  
Elle fournit :  

* un espace de saisie et de consultation des dossiers,  
* des extractions statistiques (BIRT),  
* un moteur de recherche (Elasticsearch) pour retrouver les dossiers,  
* des notifications par mail et une interface d’administration (Cerbère).  

### Objectifs de qualité orientés utilisateurs  

| # | Objectif | Pourquoi c’est‑important pour les utilisateurs |
|---|----------|-----------------------------------------------|
| 1 | **Performance** – temps de réponse < 2 s pour les recherches de dossiers | L’utilisateur doit pouvoir consulter rapidement les dossiers. |
| 2 | **Disponibilité** – 99,5 % de disponibilité mensuelle | Les commissions de qualification ne peuvent pas être retardées. |
| 3 | **Sécurité / Confidentialité** – chiffrement des données en transit & repos, conformité CNIL & RGPD | Les dossiers contiennent des données à caractère personnel. |
| 4 | **Maintenabilité** – couverture de tests unitaires ≥ 70 % et documentation à jour | Facilite les évolutions fonctionnelles (nouveaux critères, rapports). |
| 5 | **Traçabilité** – journalisation de toutes les actions critiques (CRUD, génération de rapports) | Permet les audits de conformité et le diagnostic d’incidents. |

---  

## 2️⃣ Niveau 1 – Vue **Contexte** (C4‑L1)

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

System_Boundary(sireines, "SIREINES") {
    System(sireines, "SIREINES", "Application métier de suivi des qualifications")
}

Person(user, "Agent / Utilisateur métier", "Dépose et consulte ses dossiers")
Person(admin, "Administrateur fonctionnel", "Paramètre les référentiels, gère les rapports")
System_Ext(cerb, "Cerbère (IAM)", "Gestion des comptes et authentification")
System_Ext(pg, "PostgreSQL", "Base de données métier")
System_Ext(birt, "BIRT", "Moteur de reporting")
System_Ext(es, "Elasticsearch", "Indexation / recherche plein texte")
System_Ext(mail, "Serveur mail (SMTP)", "Envoi de notifications")
System_Ext(ci, "GitLab CI / Docker registry", "Intégration continue & artefacts")
System_Ext(monitor, "Supervision (Prometheus / Grafana / Portainer)", "Collecte de métriques et alertes")

Rel(user, sireines, "Utilise")
Rel(admin, sireines, "Administre")
Rel(sireines, cerb, "Authentification via")
Rel(sireines, pg, "Lecture/Écriture")
Rel(sireines, es, "Indexation & recherche")
Rel(sireines, birt, "Génération de rapports")
Rel(sireines, mail, "Envoi de notifications")
Rel(sireines, ci, "Déploiement automatisé (Docker)")
Rel(sireines, monitor, "Export de métriques")
@enduml
```

*Explication* : SIREINES interagit avec les acteurs métier (agents, administrateurs) et s’appuie sur plusieurs systèmes externes : Cerbère pour l’authentification, PostgreSQL pour la persistance, Elasticsearch pour la recherche, BIRT pour les rapports, un serveur SMTP, la chaîne CI/CD GitLab/Docker et la supervision.

---  

## 3️⃣ Parties prenantes  

| Rôle | Organisation | Responsabilités |
|------|--------------|-----------------|
| **MOA** | CGDD / DRI / AST4 | Définition du besoin fonctionnel, validation des livrables, suivi de la conformité CNIL. |
| **MOE (prestataire historique)** | Klee Group (jusqu’en nov 2021) | Développement, mise en production initiale, support. |
| **MOE (interne actuelle)** | SG / DNUM / PNM3 | Maintien du code, évolutions fonctionnelles, exploitation. |
| **Utilisateurs finaux** | Agents publics, experts | Saisie, suivi et consultation des dossiers de qualification. |
| **Administrateur fonctionnel** | CGDD / DRI | Gestion des référentiels, paramétrage des rapports, gestion des droits. |
| **Support / Exploitation** | équipe DNUM | Surveillance (Prometheus/Grafana), gestion des incidents, sauvegardes. |
| **Sécurité / conformité** | RSSI CGDD | Garantir la conformité RGPD et la sécurité des flux. |
| **Audit CNIL** | Autorité de contrôle | Vérification de la déclaration CNIL (déclarée le 29/09/2014). |

---  

## 4️⃣ Contraintes  

| Type | Description |
|------|-------------|
| **Réglementaire** | Déclaration CNIL (n° 1034232) – protection des données à caractère personnel (DACP). |
| **Sécurité** | Authentification unique via Cerbère (SAML / OAuth2). Chiffrement TLS 1.2+ pour toutes les communications. |
| **Technique** | Java 8, Tomcat 7 (image Docker officielle), PostgreSQL 14 (Docker), Elasticsearch 7.x, BIRT 4.3, Docker Compose v2, OpenStack ECO4 (tenant *pnm3*). |
| **Opérationnelle** | Sauvegarde quotidienne des bases (AES‑256), réplication des volumes Docker, temps de redémarrage < 30 s. |
| **Performance** | Le moteur de recherche doit répondre < 2 s sur un jeu de 200 k dossiers. |
| **Disponibilité** | HA niveau application via redondance du conteneur *sireines‑app* derrière Nginx (load‑balancer). |
| **Maintenabilité** | Architecture modulaire Vertigo / Struts2, séparation claire *controllers / services / repositories*. |
| **Interopérabilité** | API REST (exposition future) – JSON, compatibilité avec les outils internes (Portainer, Grafana). |

---  

## 5️⃣ Niveau 2 – Vue **Conteneurs** (C4‑L2)

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

System_Boundary(sireines, "SIREINES – Docker Compose") {
    Container(app, "sireines‑app", "Tomcat 7 / Java 8", "Web‑app Struts2 + Vertigo")
    Container(db, "sireines‑db", "PostgreSQL 14", "Base métier")
    Container(pgadmin, "sireines‑pgadmin", "dpage/pgadmin4", "Console d’administration DB")
    Container(nginx, "Nginx LB", "Nginx 1.21", "Load‑balancer frontal")
    Container(prom, "Prometheus / Grafana", "Monitoring", "Collecte métriques & alertes")
}

Rel(nginx, app, "HTTP/HTTPS", "80/443")
Rel(app, db, "JDBC")
Rel(app, es, "REST API (search)")
Rel(app, birt, "HTTP (report generation)")
Rel(app, mail, "SMTP")
Rel(app, cerb, "SAML / OAuth2")
Rel(db, pgadmin, "Gestion via UI")
Rel(app, prom, "Export métriques (Prometheus endpoint)")

@enduml
```

### Description des conteneurs  

| Conteneur | Rôle | Technologie | Points d’interaction clés |
|-----------|------|--------------|---------------------------|
| **sireines‑app** | Application métier (Struts2, Vertigo) | Tomcat 7, Java 8, WAR `sireines-web‑*.war` | - Authentification via Cerbère <br> - Accès DB (JDBC) <br> - Recherche Elasticsearch (REST) <br> - Génération BIRT (HTTP) <br> - Envoi mail (SMTP) |
| **sireines‑db** | Persistance des dossiers, référentiels, logs | PostgreSQL 14 (Docker) | - Exposé sur le réseau interne <br> - Volume `sireines_db_sireines_vol` (persistant) |
| **sireines‑pgadmin** | Console d’administration DB (facultative) | dpage/pgadmin4 | - Se connecte à `sireines‑db` <br> - Volume `sireines_pgadmin_sireines_vol` |
| **Nginx LB** | Point d’entrée unique (HTTPS) | Nginx 1.21 | - Répartition du trafic entre plusieurs instances *app* (future scaling). |
| **Prometheus / Grafana** | Supervision & alerting | Prometheus 2.x + Grafana 8.x | - Scrape `/actuator/prometheus` exposé par l’app. |

### Décisions d’architecture (ADR)  

| # | Décision | Raison |
|---|----------|--------|
| ADR‑001 | **Dockerisation** de l’ensemble de l’application | Simplifie le déploiement multi‑environnements (recette, pré‑prod, prod). |
| ADR‑002 | **Tomcat 7 + Java 8** (hérité) | Contrainte du socle ministériel (ECO4) – maintient la compatibilité avec les librairies Vertigo/Struts2. |
| ADR‑003 | **Elasticsearch embarqué** (container distinct) | Recherche plein texte nécessaire, découplée de la base relationnelle. |
| ADR‑004 | **BIRT intégré** dans l’app (pas de container dédié) | Rapportage déjà intégré, évite la complexité d’un service supplémentaire. |
| ADR‑005 | **Nginx en front** pour le SSL et le load‑balancing | Sépare la terminaison TLS du conteneur d’application, facilite le scaling futur. |

---  

## 6️⃣ Niveau 3 – Vue **Composants** (C4‑L3) – Conteneur *sireines‑app*  

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

Container(app, "sireines‑app (Tomcat)", "Web‑app") {
    Component(searchMgr, "SearchManager", "io.vertigo.dynamo.search", "Gestion de l’index Elasticsearch")
    Component(birtMgr, "BirtManager", "i2.application.sireines.boot.manager", "Génération de rapports BIRT")
    Component(authFilter, "CerbereAuthFilter", "javax.servlet.Filter", "Intégration SSO Cerbère")
    Component(ctrl, "Controllers (Struts2)", "i2.application.sireines.controller", "Gestion des actions web")
    Component(svc, "Services (Vertigo)", "i2.application.sireines.service", "Business logic (Agents, Dossiers, Extractions, …)")
    Component(repo, "Repositories (JPA/Dynamo)", "i2.application.sireines.service", "Accès aux tables PostgreSQL")
    Component(mailSvc, "MailService", "i2.application.sireines.service.common", "Envoi de mails")
    Component(logger, "Logging & Metrics", "SLF4J / Prometheus", "Journalisation & export métriques")
}

Rel(searchMgr, es, "REST (JSON)", "Indexation / Recherche")
Rel(birtMgr, birt, "HTTP", "Récupération de templates & rendu")
Rel(authFilter, cerb, "SAML / OAuth2")
Rel(ctrl, svc, "Appel")
Rel(svc, repo, "JDBC")
Rel(svc, mailSvc, "SMTP")
Rel(logger, prom, "Scrape endpoint")
@enduml
```

### Principaux composants  

| Composant | Responsabilité | Technologie |
|-----------|----------------|--------------|
| **Controllers (Struts2)** | Mapping URL → actions, validation, navigation. | Struts2, JSP/FTL. |
| **Services** | Logique métier (agents, dossiers, extractions, import/export). | Vertigo, CDI. |
| **Repositories** | DAO JPA/Dynamo, requêtes SQL, transactions. | JPA, Spring Transaction. |
| **SearchManager** | Synchronisation des `Dossier` vers Elasticsearch, requêtes full‑text. | Vertigo Search, Elasticsearch client. |
| **BirtManager** | Génération de rapports PDF/Excel via BIRT. | BIRT engine, VFile. |
| **CerbereAuthFilter** | Authentification SSO, récupération du token. | Cerbère (SAML/OAuth2). |
| **MailService** | Envoi de courriels de notification. | JavaMail (SMTP). |
| **Logging & Metrics** | Logback, SLF4J, exposition `/actuator/prometheus`. | Logback, Prometheus client. |

---  

## 7️⃣ Niveau 4 – Vue **Code**  

*Cette section n’est pas détaillée dans ce DAT, mais les artefacts suivants existent :*  

* `src/main/java/i2/application/sireines/...` – contrôleurs, services, managers.  
* `src/main/resources/...` – fichiers de configuration (Struts, Vertigo, BIRT, Elasticsearch).  
* `pom.xml` – gestion des dépendances Maven (Vertigo, Struts2, BIRT, PostgreSQL driver).  

---  

## 8️⃣ Vue **Exécution** (Scénarios critiques)  

### 8.1 Connexion d’un agent et consultation d’un dossier  

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Deployment.puml

Person(agent, "Agent")
System_Boundary(sireines, "SIREINES") {
    Container(app, "sireines‑app")
    Container(db, "sireines‑db")
    Container(nginx, "Nginx LB")
    Container(cerb, "Cerbère (IAM)")
}
Rel(agent, nginx, "HTTPS")
Rel(nginx, app, "HTTP")
Rel(app, cerb, "SAML")
Rel(app, db, "JDBC")
@enduml
```

1. L’agent ouvre son navigateur et accède à `https://sireines.recette…`.  
2. Nginx redirige la requête vers le conteneur `sireines‑app`.  
3. `CerbèreAuthFilter` déclenche le flux SAML → l’utilisateur est authentifié.  
4. Le **Controller** `AccueilAction` charge la page d’accueil.  
5. L’agent sélectionne un dossier → le **Service** `DossiersServices` interroge le **Repository** (PostgreSQL) → le **View** rend les informations.  

### 8.2 Génération d’un rapport BIRT  

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C
# 📘 Dossier d’Architecture Technique (DAT) – **SIREINES**
> **Version : 2.5.20 (12 mars 2024)**  
> **Date : 27 avril 2026**  
> **Auteur : Équipe d’Architecture – DPNM3 / CGDD‑SR‑AST2**  

---

[TOC]

---

## 1️⃣ Introduction & objectifs

### 1.1 Vue d’ensemble fonctionnelle
SIREINES est une application **Web Java/J2EE** qui centralise les demandes de qualification d’experts et spécialistes scientifiques et techniques. Elle permet :

* La **déclaration** d’une demande par un agent.
* Le **suivi** de l’avancement (comité, décision, qualification).
* La **consultation** des dossiers et la **production** de rapports (BIRT).
* La **recherche** avancée (Elasticsearch) et l’**export** de données (CSV).

### 1.2 Objectifs de qualité orientés utilisateur  

| # | Objectif | Raison métier |
|---|----------|---------------|
| 1 | **Disponibilité ≥ 99,5 %** | Garantir l’accès en continu aux services de qualification. |
| 2 | **Temps de réponse ≤ 2 s** pour les écrans de recherche | Optimiser l’expérience utilisateur (agents). |
| 3 | **Conformité RGPD & CNIL** (déclaration : 29/09/2014) | Respecter les obligations légales sur les DACP. |
| 4 | **Traçabilité complète** des actions (audit, logs) | Faciliter les contrôles et les investigations. |
| 5 | **Scalabilité** (Docker, IaaS) | Permettre la montée en charge lors de pics de saisie. |

↩︎ [Retour au sommaire](#toc)

---

## 2️⃣ Parties prenantes

| Rôle | Organisation | Principale attente |
|------|--------------|--------------------|
| **MOA** | CGDD / SR / AST2 – Pascal Zémour (Chef de projet) | Fonctionnalités métier, conformité réglementaire. |
| **MOE** | SG / DNUM / PNM / DPNM3 – Vincent Letrouit (Sponsor) | Livraison fiable, respect des délais, évolutivité. |
| **Utilisateurs finaux** | Agents, commissions, services RH | Saisie simple, suivi transparent, accès aux rapports. |
| **Exploitation** | DSI / ECO4 (IaaS) | Disponibilité, supervision (Prometheus/Grafana), sauvegardes. |
| **Sécurité / DPO** | CNIL, DPO CGDD | Respect du RGPD, traçabilité, protection des DACP. |
| **Prestataire** | Klee Group (historique) | Support technique, maintenance évolutive. |

↩︎ [Retour au sommaire](#toc)

---

## 3️⃣ Contraintes & exigences de sécurité (modèle D‑I‑C‑T)

| Domaine | Contraintes |
|---------|-------------|
| **Technique** | Java 8, Tomcat 7, PostgreSQL 14, Docker Compose, Maven 3, BIRT 4.3, Elasticsearch 7.x. |
| **Organisationnelle** | Déploiements via GitLab CI/CD, procédures de merge‑request (dévelop‑&gt;recette‑&gt;preprod‑&gt;prod). |
| **Réglementaire** | CNIL 2014, RGPD (DACP « coordonnées des experts »). |
| **Sécurité** | <ul><li>Disponibilité (D) : HA Docker, sauvegardes chiffrées AES‑256.</li><li>Intégrité (I) : contrôles de checksum sur les WAR, scripts de migration DB.</li><li>Confidentialité (C) : communications TLS, accès DB limité aux rôles.</li><li>Traçabilité (T) : logs applicatifs (log4j), audit PostgreSQL, supervision Prometheus.</li></ul> |

↩︎ [Retour au sommaire](#toc)

---

## 4️⃣ Contexte & périmètre

### 4.1 Partenaires fonctionnels
* **Cerbère** (gestion des habilitations) – environnements Recette / Pre‑prod / Prod.  
* **BIRT** (reporting) – génération de rapports PDF/Excel.  
* **Elasticsearch** – moteur de recherche plein texte.  
* **Portail‑support DIN** – suivi des tickets (SIREINES).  

### 4.2 Interfaces techniques

| Interface | Protocole | Fréquence | Type de données |
|-----------|-----------|----------|-----------------|
| Front‑end (agents) | HTTP/HTTPS | On‑demand | JSON/HTML |
| API interne (services) | HTTP/REST | On‑demand | JSON |
| DB SIREINES | JDBC (PostgreSQL) | Persistante | Tables relationnelles |
| BIRT server | HTTP | On‑demand | PDF/Excel |
| Elasticsearch | HTTP/REST | On‑demand | Index JSON |
| Cerbère (auth) | LDAP/TLS | Authentification | Identifiants |
| Monitoring (Prometheus) | Scrape HTTP | 15 s | Métriques |

↩︎ [Retour au sommaire](#toc)

---

## 5️⃣ Stratégie de solution

| Décision | Justification |
|----------|--------------|
| **Architecture monolithique (Struts2 + Spring)** | Réutilisation du code existant, faible complexité de mise en place. |
| **Dockerisation** | Portabilité, isolement des dépendances, alignement avec les pratiques CI/CD. |
| **PostgreSQL** | Base relationnelle robuste, support de scripts de migration versionnés. |
| **Elasticsearch embarqué** | Recherche rapide sur les mots‑clés, filtres complexes. |
| **BIRT** | Reporting déjà intégré, génération dynamique de documents. |
| **Reverse‑proxy Nginx (pair)** | Haute disponibilité, équilibrage du trafic HTTP/HTTPS. |
| **Supervision Prometheus + Grafana** | Visibilité des indicateurs (latence, erreurs, utilisation CPU/RAM). |
| **Sauvegarde AES‑256** (GTI) | Conformité RGPD, protection des DACP. |
| **Maven + GitLab CI** | Build reproductible, artefacts versionnés (WAR). |

↩︎ [Retour au sommaire](#toc)

---

## 6️⃣ Vue en briques (C4 ‑ L2)

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor': '#2F80ED', 'edgeLabelBackground':'#f9f9f9'}}%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%}%%
graph TD
    subgraph "Docker‑Compose"
    A[Tomcat 7 (sireines‑app)] -->|JDBC| B[PostgreSQL 14 (sireines‑db)]
    A -->|HTTP| C[Elasticsearch]
    A -->|HTTP| D[BIRT Server]
    A -->|HTTP| E[Nginx LB (2 instances)]
    B -->|Backup| F[GTI Storage (AES‑256)]
    G[PgAdmin] --> B;
    end
    style A fill:#E3F2FD,stroke:#2F80ED,stroke-width_2px;
    style B fill:#FFF3E0,stroke:#FF9800,stroke-width_2px;
    style C fill:#E8F5E9,stroke:#4CAF50,stroke-width_2px;
    style D fill:#F3E5F5,stroke:#9C27B0,stroke-width_2px;
    style E fill:#E0F7FA,stroke:#00BCD4,stroke-width_2px;
    style F fill:#F5F5F5,stroke:#9E9E9E,stroke-dasharray: 5 5
```

* **sireines‑app** : conteneur Tomcat 7 contenant le WAR `sireines-web‑*.war`.  
* **sireines‑db** : conteneur PostgreSQL 14 + schéma `sireines`.  
* **Elasticsearch** : moteur de recherche dédié aux mots‑clés.  
* **BIRT** : génération de rapports (PDF/Excel).  
* **Nginx** : reverse‑proxy en mode « pair » (load‑balancing, TLS termination).  
* **PgAdmin** : console d’administration DB (usage interne).  
* **GTI Storage** : sauvegarde chiffrée des volumes DB.

↩︎ [Retour au sommaire](#toc)

---

## 7️⃣ Vue d’exécution (Scénarios critiques)

### 7.1 Connexion d’un agent & recherche de dossiers
```mermaid
sequencediagram;
    participant Agent as Agent (Web)
    participant Nginx as Nginx LB;
    participant Tomcat as Tomcat (SIREINES‑app)
    participant ES as Elasticsearch;
    participant DB as PostgreSQL;
    Agent->>Nginx: GET /Recherche.do (session cookie)
    Nginx->>Tomcat: Forward request;
    Tomcat->>ES: Search query (mots‑clés)
    ES-->>Tomcat: Résultats JSON;
    Tomcat->>DB: Lecture dossiers (SELECT)
    DB-->>Tomcat: Données dossiers;
    Tomcat-->>Agent: HTML + Résultats
```

*Temps attendu* : < 2 s du premier rendu.

### 7.2 Génération d’un rapport BIRT
```mermaid
sequencediagram;
    participant Agent;
    participant Nginx;
    participant Tomcat;
    participant BIRT;
    Agent->>Nginx: POST /Rapport.do;
    Nginx->>Tomcat: Forward;
    Tomcat->>BIRT: Request report (XML + data)
    BIRT-->>Tomcat: PDF (stream)
    Tomcat-->>Agent: Download PDF
```

### 7.3 Sauvegarde planifiée
```mermaid
sequencediagram;
    participant GTI as GTI Scheduler;
    participant Docker as Docker Engine;
    participant DB as PostgreSQL;
    participant Storage as AES‑256 Storage;
    GTI->>Docker: docker exec sireines‑db pg_dump -Fc;
    Docker->>DB: Dump;
    DB-->>Docker: Dump file;
    Docker->>Storage: Upload (encrypted)
```

↩︎ [Retour au sommaire](#toc)

---

## 8️⃣ Vue Déploiement *(section standardisée)*

### Environnements

| Environnement | Hébergement | Serveurs | Réseau | Particularités |
|---------------|-------------|----------|--------|-----------------|
| **Développement** | Poste développeur (Docker Desktop) | 1 × Tomcat, 1 × Postgres, 1 × Elasticsearch | LAN local | Docker Compose, volume persistant `sireines_db_dev_vol`. |
| **Recette** | ECO4 / PNM3 (Bastion) | 2 × Tomcat (LB), 1 × Postgres, 1 × Elasticsearch | VLAN Recette, TLS mutualisé | Sauvegarde nightly, accès via `sireinesrec`. |
| **Pré‑prod** | ECO4 / PNM3 (Bastion) | Identique Recette | VLAN Pre‑prod | Validation avant mise en prod, tests de charge. |
| **Production** | ECO4 / PNM3 (Data‑Center Paris La Défense) | 2 × Tomcat (LB), 1 × Postgres, 1 × Elasticsearch | VLAN Prod, TLS + HSTS | Sauvegarde chiffrée AES‑256, monitoring 24/7, haute disponibilité. |

### 8.1 Infrastructure (standard)

```mermaid
flowchart LR
    subgraph IaaS_ECO4["ECO4 IaaS – Paris La Défense"]
    N[Reverse‑proxy Nginx (2 instances)]
    T1[Tomcat – sireines‑app (1)]
    T2[Tomcat – sireines‑app (2)]
    P[PostgreSQL – sireines‑db]
    E[Elasticsearch]
    B[BIRT Server]
    end
    N --> T1 & T2;
    T1 --> P & E & B;
    T2 --> P & E & B
```

*Le *reverse‑proxy* assure l’équilibrage et la terminaison TLS.  
Les conteneurs sont orchestrés via **docker‑compose** (fichier versionnée dans le repo).  

↩︎ [Retour au sommaire](#toc)

---

## 9️⃣ Sujets transverses

| Domaine | Décisions / pratiques |
|--------|----------------------|
| **Authentification** | Centralisée via **Cerbère** (LDAP/TLS). Jeton de session géré par Struts2. |
| **Journalisation** | `log4j.xml` → logs JSON → agrégés par **Filebeat → Loki**. |
| **Monitoring** | Prometheus scrape `/metrics` (Tomcat, PostgreSQL, Elasticsearch). Alertes via Alertmanager (disponibilité, latence > 2 s). |
| **Gestion des erreurs** | `ErrorHandler.java` → page d’erreur générique, logs d’exception. |
| **API** | REST interne (Spring MVC) pour BIRT & recherche, versionnée (`/api/v1/…`). |
| **Sécurité** | TLS 1.2+, en‑tête `X‑Content‑Security‑Policy`, chiffrement des sauvegardes, secrets dans `.env` (non versionnés). |
| **CI/CD** | GitLab CI → `docker build`, `docker push`, `docker-compose up -d` sur chaque environnement. |
| **Gestion de configuration** | `application-config.xml` + `sireines‑auth‑config.xml` (déploiement via variables d’environnement). |

↩︎ [Retour au sommaire](#toc)

---

## 🔟 Exigences de qualité & scénarios de validation

| Exigence | Critère d’acceptation | Scénario de test |
|----------|----------------------|-----------------|
| **Performance** | 95 % des requêtes < 2 s | Simuler 200 utilisateurs simultanés (JMeter) → mesurer temps de réponse. |
| **Disponibilité** | ≥ 99,5 % sur 30 jours | Vérifier les métriques `up{job="tomcat"}` dans Grafana, comparer aux SLA. |
| **Sécurité – DACP** | Aucun accès non‑autorisé aux données personnelles | Pentest OWASP Top 10, validation du chiffrement des sauvegardes. |
| **Intégrité des données** | Aucun `checksum` de dump corrompu | Après chaque sauvegarde, comparer `sha256` avec valeur stockée. |
| **Traçabilité** | Log de chaque action (CRUD) avec userID | Parcourir les logs `audit.log` → vérifier présence de `userId`, `timestamp`. |
| **Scalabilité** | Déploiement d’un deuxième conteneur Tomcat sans downtime | `docker-compose scale app=2` → vérifier le basculement du LB. |
| **Reporting BIRT** | PDF généré sans perte de données | Générer le rapport « Statistiques qualification » → comparer avec export CSV. |

↩︎ [Retour au sommaire](#toc)

---

## 1️⃣1️⃣ Risques & dettes techniques

| Risque / Dette | Impact | Probabilité | Mitigation |
|----------------|--------|-------------|------------|
| **Dépendance à Tomcat 7 / Java 8** (fin de support) | Sécurité, incompatibilité future | ★★☆☆☆ | Plan de migration vers Tomcat 9 / Java 11 (road‑map 2027). |
| **Images Docker non‑pinned** (latest) | Rupture de build | ★★☆☆☆ |
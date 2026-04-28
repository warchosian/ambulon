# Cahier des Spécifications Techniques (CST) – **SIREINES**  
*Version 1.0 – 27 / 04 / 2026*  

> **Document** : CST – SIREINES  
> **Projet** : SIREINES (Gestion des dossiers d’expertise et de qualification)  
> **Références** : ISO/IEC 25010:2023, ISO/IEC 25023 (mesurabilité), ISO/IEC 25024 (traceabilité), ISO/IEC 27001 (sécurité), ISO 9001 (qualité).  

---  

## 1. Introduction et contexte qualité  

| Élément | Description |
|--------|-------------|
| **Objectifs qualité du projet** | • Garantir la disponibilité ≥ 99,9 % en production.<br>• Assurer l’intégrité des données (aucune perte ou corruption).<br>• Offrir une expérience utilisateur fluide (temps de réponse ≤ 2 s, SUS ≥ 68).<br>• Respecter les exigences RGPD (confidentialité, traçabilité). |
| **Contexte métier** | SIREINES recense les demandes de qualification des agents par les comités de domaine, assure le suivi des dossiers, la génération de rapports BIRT et l’envoi de notifications. Le système est utilisé par la DRI/AST4 (CGDD) et doit être disponible en pré‑prod, recette et production. |
| **Contexte technique** | • Application Java /J2EE (Spring + Struts 2).<br>• Base de données PostgreSQL 14 (Docker).<br>• Conteneurisation Docker + docker‑compose (3 containers : app, db, pgadmin).<br>• Rapport BIRT 4.3, serveur d’application Tomcat 7 (JDK 8).<br>• CI/CD GitLab CI, SonarQube, Sonar‑Project‑Properties. |
| **Méthodologie d’évaluation** | 1️⃣ Analyse statique (SonarQube, Checkstyle, PMD).<br>2️⃣ Tests automatisés (JUnit 5, Selenium, JBehave).<br>3️⃣ Tests de performance (JMeter, Gatling).<br>4️⃣ Audits sécurité (OWASP ZAP, SAST).<br>5️⃣ Mesure d’usage (Google Analytics + logs applicatifs). |
| **Portée du CST** | Tous les modules du code source `sireines-web`, scripts SQL, Docker, scripts d’installation, fichiers de configuration (Struts, Spring, BIRT, Docker‑compose). |

---  

## 2. Modèle de qualité ISO / IEC 25010  

```
                     QUALITÉ DU PRODUIT LOGICIEL
┌─────────────────────┬─────────────────────┬─────────────────────┬─────────────────────┐
│ 1. Aptitude        │ 2. Performance      │ 3. Compatibilité    │ 4. Utilisabilité    │
│    fonctionnelle   │    efficacité       │    (Interopérabilité│    (Satisfaction)  │
│                    │                     │     & Cohérence)   │                     │
├─────────────────────┼─────────────────────┼─────────────────────┼─────────────────────┤
│ 5. Fiabilité       │ 6. Sécurité         │ 7. Maintenabilité   │ 8. Portabilité      │
│    (Disponibilité,│    (Confidentialité│    (Modularité,     │    (Installation,  │
│     Tolérance)    │     Intégrité, …) │     Testabilité)   │     Migration)      │
└─────────────────────┴─────────────────────┴─────────────────────┴─────────────────────┘
```

---  

## 3. Spécification détaillée par caractéristique  

> **Notation** : Chaque sous‑caractéristique possède :  
> • **Métrique** (mesurable, source de donnée).  
> • **Objectif** (seuil à atteindre).  
> • **Méthode de vérification** (outil / procédure).  

### 3.1 Aptitude fonctionnelle (Functional Suitability)

| Sous‑caractéristique | Métrique | Objectif | Source / Outil | Vérification |
|----------------------|----------|----------|----------------|--------------|
| **Complétude fonctionnelle** | % de exigences fonctionnelles implémentées (issues / CCF) | ≥ 95 % | Jira / GitLab (issues) | Revue de traçabilité CCF→CST (tableau 3) |
| **Exactitude fonctionnelle** | Taux d’erreurs fonctionnelles détectées en test (bugs / tests) | ≤ 0,5 % | SonarQube / JUnit | Rapport de test unitaire + Sonar “bugs” |
| **Adéquation fonctionnelle** | Score d’évaluation utilisateur (échelle 1‑5) | ≥ 4 / 5 | Enquête interne (Google Forms) | Analyse post‑déploiement (Satisfaction ≥ 80 %) |

### 3.2 Performance et efficacité (Performance Efficiency)

| Sous‑caractéristique | Métrique | Objectif | Source / Outil | Vérification |
|----------------------|----------|----------|----------------|--------------|
| **Comportement temporel** | 95ᵉ percentile du temps de réponse (ms) | ≤ 2000 ms (pages ≤ 2 s) | JMeter / Gatling | Rapport de charge (≤ 2 s) |
| **Utilisation des ressources** | CPU % moyen, RAM % moyen (sur conteneur) | CPU ≤ 70 % ; RAM ≤ 75 % | Docker stats, Prometheus | Dashboard Grafana (alertes > 80 %) |
| **Capacité** | Nombre d’utilisateurs simultanés supportés (sessions) | ≥ 150 utilisateurs | JMeter (scenario 150) | Test de charge validé |

### 3.3 Compatibilité (Compatibility)

| Sous‑caractéristique | Métrique | Objectif | Source / Outil | Vérification |
|----------------------|----------|----------|----------------|--------------|
| **Cohérence** | % de conformité aux standards (HTML5, CSS3, OWASP) | 100 % | W3C validator, OWASP‑ZAP | Rapport de conformité |
| **Interopérabilité** | Nombre de formats d’échange supportés (CSV, XLSX, BIRT PDF) | ≥ 3 | Documentation d’API | Tests d’import/export automatisés |

### 3.4 Utilisabilité (Usability)

| Sous‑caractéristique | Métrique | Objectif | Source / Outil | Vérification |
|----------------------|----------|----------|----------------|--------------|
| **Appréhensibilité** | Temps de formation (h) pour un utilisateur « nouveau » | ≤ 2 h | Sessions de formation | Feuilles de présence |
| **Apprenabilité** | Taux de réussite du scénario de test « première utilisation » | ≥ 90 % | Test utilisateur (Selenium) | Rapport de test UX |
| **Opérabilité** | Nombre moyen de clics pour une tâche courante (ex : création dossier) | ≤ 5 clics | Analyse de parcours (Hotjar) | Dashboard UX |
| **Esthétique** | Score SUS (System Usability Scale) | ≥ 68/100 | Enquête post‑déploiement | Rapport SUS |
| **Accessibilité** | Conformité WCAG 2.1 Niveau AA | 100 % | axe‑core, Lighthouse | Rapport d’audit |

### 3.5 Fiabilité (Reliability)

| Sous‑caractéristique | Métrique | Objectif | Source / Outil | Vérification |
|----------------------|----------|----------|----------------|--------------|
| **Maturité** | Densité de défauts (bugs / KLOC) | ≤ 0,5 bugs/KLOC | SonarQube “bugs” | Rapport mensuel |
| **Disponibilité** | % de temps de service (Uptime) | ≥ 99,9 % (MTBF ≥ 876 h) | Pingdom / Grafana | SLA‑report |
| **Tolérance aux fautes** | RTO (Recovery Time Objective) | ≤ 10 min | Procédure de bascule, tests de chaos | Test de bascule |
| **Récupérabilité** | RPO (Recovery Point Objective) | ≤ 5 min de perte de données | Snapshots PostgreSQL | Test de restauration |

### 3.6 Sécurité (Security)

| Sous‑caractéristique | Métrique | Objectif | Source / Outil | Vérification |
|----------------------|----------|----------|----------------|--------------|
| **Confidentialité** | Score d’audit OWASP‑ASVS (niveau 2) | ≥ 80 % | OWASP‑ZAP, SAST | Rapport d’audit |
| **Intégrité** | Nombre de violations d’intégrité détectées (checksum) | 0 | PostgreSQL pgcrypto, triggers | Logs d’intégrité |
| **Non‑répudiation** | % de transactions journalisées (audit‑log) | 100 % | Logback + ELK | Requête Kibana |
| **Responsabilité** | Couverture de traçabilité (audit‑log / actions) | 100 % | Spring Security + Audit | Rapport d’audit |
| **Authenticité** | Méthodes d’authentification utilisées (OIDC, LDAP) | OIDC + LDAP | Spring Security | Vérif. configuration |

### 3.7 Maintenabilité (Maintainability)

| Sous‑caractéristique | Métrique | Objectif | Source / Outil | Vérification |
|----------------------|----------|----------|----------------|--------------|
| **Modularité** | Couplage (Ce) & Cohésion (Coh) (average) | Ce ≤ 0,4 ; Coh ≥ 0,7 | SonarQube “coupling” | Rapport de métriques |
| **Réutilisabilité** | % de composants réutilisables (modules) | ≥ 30 % | Analyse de code (Maven modules) | Inventaire MOA |
| **Analysabilité** | Complexité cyclomatique moyenne | ≤ 10 | SonarQube “cognitive complexity” | Rapport mensuel |
| **Modifiabilité** | Temps moyen de modification (h) – ticket | ≤ 4 h | JIRA / GitLab | Historique tickets |
| **Testabilité** | Couverture de tests unitaires (%) | ≥ 80 % (branches) | JaCoCo, Sonar | Dashboard de couverture |

### 3.8 Portabilité (Portability)

| Sous‑caractéristique | Métrique | Objectif | Source / Outil | Vérification |
|----------------------|----------|----------|----------------|--------------|
| **Adaptabilité** | Nombre d’environnements supportés (Docker, VM, IaaS) | 3 (Docker‑local, IaaS‑ECO4, VM‑test) | Documentation d’installation | Tests d’installation |
| **Installabilité** | Temps d’installation (min) sur poste de travail | ≤ 15 min | Script `docker‑compose up -d` | Chronométrage |
| **Remplaçabilité** | % de conformité aux standards d’image (OCI) | 100 % | Dockerfile lint (hadolint) | Rapport lint |

---  

## 4. Architecture technique  

### 4.1 Diagramme de composants (texte)  

```
+-------------------+          +-------------------+          +-------------------+
|  SIREINES‑WEB    |  HTTP    |   Tomcat 7 (JDK8) |  JDBC    |  PostgreSQL 14   |
| (Struts2 + Spring| <------> | (Docker container) | <------> | (Docker container)|
+-------------------+          +-------------------+          +-------------------+
        |                               |                               |
        |  BIRT 4.3 (report engine)    |  ElasticSearch (embedded)    |
        +-------------------+-----------+-------------------+-----------+
                            |                               |
                            v                               v
                     +--------------+                +--------------+
                     |  pgAdmin4    |  UI/DB Admin   |  Docker‑Compose |
                     +--------------+                +--------------+
```

### 4.2 Justification des choix  

| Élément | Raison du choix | Impact qualité |
|--------|----------------|----------------|
| **Spring + Struts 2** | Framework mature, supporte l’injection, la sécurité, le MVC. | **Fiabilité**, **Sécurité**, **Maintenabilité** |
| **Docker + docker‑compose** | Isolation, reproducibilité, scalabilité. | **Portabilité**, **Installabilité**, **Performance** |
| **PostgreSQL 14 (Alpine)** | Licence libre, performances, support JSON & full‑text search. | **Fiabilité**, **Sécurité**, **Performance** |
| **BIRT 4.3** | Génération de rapports PDF/HTML, intégré à l’application. | **Compatibilité**, **Utilisabilité** |
| **SonarQube** | Analyse continue de la qualité du code. | **Maturité**, **Testabilité**, **Maintenabilité** |
| **OWASP‑ZAP & SAST** | Détection précoce des vulnérabilités. | **Confidentialité**, **Intégrité** |

### 4.3 Patterns architecturaux  

| Pattern | Description | Qualité impactée |
|---------|-------------|-------------------|
| **MVC (Model‑View‑Controller)** | Séparation claire des responsabilités. | **Modularité**, **Testabilité** |
| **DAO (Data Access Object)** | Accès aux données via interfaces. | **Réutilisabilité**, **Sécurité** |
| **Factory & Builder** (BirtManager) | Création dynamique des rapports. | **Adaptabilité**, **Extensibilité** |
| **Circuit Breaker** (SearchManager) | Résilience lors de pannes ElasticSearch. | **Tolérance aux fautes**, **Disponibilité** |
| **Dependency Injection (Spring)** | Découplage des composants. | **Modifiabilité**, **Testabilité** |

---  

## 5. Stack technologique qualifié  

| Niveau | Technologie | Version | Raison du choix | Métriques qualité (exemple) |
|--------|--------------|---------|-----------------|------------------------------|
| **Langage** | Java | 1.8 (JDK 8) | Compatibilité avec Tomcat 7, mature. | Sonar bugs ≤ 0,5 /KLOC |
| **Framework** | Spring Core + Spring Security | 5.2.x | DI, sécurité, gestion transactions. | % de fonctions couvertes ≥ 80 % |
| **Web MVC** | Struts 2 | 2.5.x | UI legacy, intégration BIRT. | Temps de réponse ≤ 2 s |
| **Serveur d’app** | Tomcat 7 | 7.0.108 | LTS, support JDK 8. | Uptime ≥ 99,9 % |
| **Base de données** | PostgreSQL | 14.1‑alpine | ACID, JSON, full‑text search. | RPO ≤ 5 min |
| **Conteneurisation** | Docker | 24.0.x | Portabilité, CI/CD. | Installabilité ≤ 15 min |
| **Orchestration** | Docker‑compose | 2.22.x | Déploiement multi‑service simple. | Temps de démarrage ≤ 30 s |
| **Reporting** | BIRT | 4.3.0 | Rapports PDF/HTML, open‑source. | Export ≤ 5 s |
| **Gestion des dépendances** | Maven | 3.9.x | Build reproductible. | Build success ≥ 99 % |
| **Analyse qualité** | SonarQube | 9.9 LTS | Détection de bugs & couverture. | Couverture ≥ 80 % |
| **Tests unitaires** | JUnit 5 | 5.9.x | Framework moderne. | Temps de test ≤ 2 min |
| **Tests fonctionnels** | Selenium WebDriver | 4.11.x | Tests UI. | Pass rate ≥ 95 % |
| **Tests charge** | JMeter | 5.6.x | Performance. | 95ᵉ percentile ≤ 2 s |
| **Sécurité** | OWASP‑ZAP | 2.12.x | Scan dynamique. | Vulnérabilités ≥ A‑level = 0 |
| **Observabilité** | Prometheus + Grafana | 2.48 / 9.5 | Métriques runtime
# 📄 Cahier des Spécifications Techniques (CST) – **causalismp**  
**Version : 1.0** – 2024‑04‑28  
**Projet** : *causalismp* – Gestion des accidents du travail et des maladies professionnelles  

---

## 1️⃣ Introduction & Contexte Qualité  

| Élément | Description |
|---------|-------------|
| **Objectif du projet** | Fournir une application web d’administration des référentiels : accidents, maladies, grades, services, tâches prescrites, etc. – soutenir les équipes RH et la conformité aux obligations légales. |
| **Environnement technique** | - **Java 8‑11** (source : `src/main/java/...`) <br> - **Struts 1.x** (MVC) <br> - **JSP** (fragments, redirections) <br> - **Castor JDO** + **Oracle 12c** (datasource JNDI `jdbc/userDScausalis`) <br> - **Maven multi‑module** (`causalismp-database`, `causalismp-deployment`, `causalismp-doc`, `causalismp‑web`) <br> - **Tomcat 9** (déploiement WAR) <br> - **GitLab CI** + **SonarQube** (`sonar-project.properties`) |
| **Références fonctionnelles (CCF)** | 1. Gestion des dossiers d’accident <br> 2. Gestion des dossiers de maladie professionnelle <br> 3. Export OpenOffice/CSV des dossiers <br> 4. Synchronisation des référentiels (grades ↔ Rehucit) <br> 5. Consultation / recherche avancée <br> 6. Gestion des paramètres de pagination <br> 7. Authentification via Cerbere (SSO) |
| **Méthodologie d’évaluation** | - **Mesure automatisée** (SonarQube, JUnit, JMeter) <br> - **Audits manuels** (revue de code, tests de sécurité) <br> - **Tableaux de bord** (Grafana / Prometheus) <br> - **Critères d’acceptation** définis dans le tableau de traçabilité CCF ↔ Qualité (section 3). |

---

## 2️⃣ Modèle de Qualité – ISO/IEC 25010 : 2023  

```
                     QUALITÉ DU PRODUIT LOGICIEL
┌─────────────────────┬─────────────────────┬─────────────────────┬─────────────────────┬─────────────────────┬─────────────────────┬─────────────────────┬─────────────────────┐
│ Fonctionnalité      │ Performance          │ Compatibilité        │ Utilisabilité        │ Fiabilité            │ Sécurité            │ Maintenabilité      │ Portabilité          │
│ (Functional Suit.) │ (Performance)       │ (Compatibility)      │ (Usability)          │ (Reliability)       │ (Security)          │ (Maintainability)   │ (Portability)       │
└─────────────────────┴─────────────────────┴─────────────────────┴─────────────────────┴─────────────────────┴─────────────────────┴─────────────────────┴─────────────────────┘
```

Chaque caractéristique est détaillée ci‑dessous avec sous‑caractéristiques, métriques, objectifs chiffrés et méthodes de vérification.

---

## 3️⃣ Spécifications détaillées par caractéristique  

> **Remarque** : Toutes les métriques sont **mesurables** et **traçables** à l’aide de SonarQube, JUnit, JMeter, OWASP‑ZAP, Prometheus, etc.

### 3.1 Fonctionnalité (Functional Suitability)

| Sous‑caractéristique | Métrique | Objectif | Méthode de mesure |
|----------------------|----------|----------|--------------------|
| **Complétude fonctionnelle** | % d’exigences CCF implémentées | **≥ 95 %** (toutes les exigences listées en § 1 sont couvertes) | Mapping CCF ↔ Classes/Endpoints (ex. `DossierAccidentService`, `ExportDonnees`, `SynchronizeService`). |
| **Exactitude fonctionnelle** | Taux d’erreurs de traitement (défauts fonctionnels) | **≤ 0,5 %** des transactions | Tests d’intégration automatisés + suivi des tickets JIRA. |
| **Adéquation fonctionnelle** | Score d’évaluation utilisateur (échelle 1‑5) | **≥ 4,2/5** (questionnaire auprès des équipes RH) | Enquête post‑déploiement, agrégation dans SonarQube “custom metrics”. |

### 3.2 Performance & Efficacité (Performance Efficiency)

| Sous‑caractéristique | Métrique | Objectif | Méthode de mesure |
|----------------------|----------|----------|--------------------|
| **Comportement temporel** | Temps de réponse 95ᵉ percentile (ms) | **≤ 2000 ms** pour les pages de recherche (`/dossiers.do`, `/statistiques.do`) | JMeter scripts sous charge 50 utilisateurs simultanés. |
| **Utilisation des ressources** | CPU % / RAM % sous charge nominale (50 U) | **CPU ≤ 70 %**, **RAM ≤ 75 %** du conteneur Tomcat | Prometheus node‑exporter + Grafana dashboards. |
| **Capacité** | Nombre d’utilisateurs concurrents supportés sans dégradation > 20 % | **≥ 200 U** (test de montée en charge) | JMeter “stress test” + analyse des GC logs. |

### 3.3 Compatibilité (Compatibility)

| Sous‑caractéristique | Métrique | Objectif | Méthode de mesure |
|----------------------|----------|----------|--------------------|
| **Cohérence** | Nombre de violations de standards (JEE, Struts 1, Castor) détectées par Sonar | **0** violations critiques | SonarQube “ruleset” : `java:S1192`, `struts:missing-config` … |
| **Interopérabilité** | Formats d’échange supportés (CSV, OpenOffice ODS, Web‑Service SOAP) | **≥ 3** formats (déjà implémentés) | Vérification des classes `CausalisExportManager`, `WSClient*`, tests d’intégration. |

### 3.4 Utilisabilité (Usability)

| Sous‑caractéristique | Métrique | Objectif | Méthode de mesure |
|----------------------|----------|----------|--------------------|
| **Appréhensibilité** | Temps moyen de formation d’un nouvel utilisateur (hrs) | **≤ 2 h** (formation RH) | Sessions de formation + suivi temps via ticket. |
| **Apprenabilité** | % de tâches réalisées sans aide (test utilisateur) | **≥ 85 %** | Scénario d’usage (création dossier, export) avec observation. |
| **Opérabilité** | Nombre de clics pour créer un dossier accident | **≤ 6 clics** | Analyse UX (heat‑map) sur les JSP. |
| **Esthétique** | Score SUS (System Usability Scale) | **≥ 68/100** | Questionnaire SUS auprès des utilisateurs. |
| **Accessibilité** | Conformité WCAG 2.1 (niveau A/AA) | **Niveau AA** minimum | Outil d’audit axe‑core, rapport automatisé. |

### 3.5 Fiabilité (Reliability)

| Sous‑caractéristique | Métrique | Objectif | Méthode de mesure |
|----------------------|----------|----------|--------------------|
| **Maturité** | Densité de défauts (défauts/KLOC) | **≤ 0,5 / KLOC** | Historique Sonar “bugs” + JIRA. |
| **Disponibilité** | % de disponibilité du service (Uptime) | **≥ 99,9 %** (3 h / mois) | Monitoring via Pingdom / Grafana alerts. |
| **Tolérance aux fautes** | Temps moyen de récupération (MTTR) après incident | **≤ 10 min** | Historique d’incidents + alertes. |
| **Récupérabilité** | Point de récupération (RPO) | **≤ 15 min** (replication DB) | Tests de restauration de la base (scripts `20190403‑…`). |

### 3.6 Sécurité (Security)

| Sous‑caractéristique | Métrique | Objectif | Méthode de mesure |
|----------------------|----------|----------|--------------------|
| **Confidentialité** | Score d’audit OWASP ASVS (niveau 3) | **≥ 80 %** des exigences | OWASP‑ZAP + revue manuelle du code (ex. `WSException`, `CommonException`). |
| **Intégrité** | % de contrôles d’intégrité implémentés (hash, signatures) | **100 %** sur les flux critiques (export, WS) | Analyse du code (`TranscodageGradePredicate`, `WSConstants`). |
| **Non‑répudiation** | Présence de journaux d’audit (audit‑log) | **Oui** (log4j config) | Vérification du fichier `log4j.xml`. |
| **Responsabilité** | Couverture du traçage d’audit (log lines) | **≥ 95 %** des actions critiques | Sonar “log‑usage” rule + tests. |
| **Authenticité** | Méthodes d’authentification (SSO Cerbere) | **Oui** (classe `Cerbere` dans `reauth.jsp`) | Tests fonctionnels d’authentification. |

### 3.7 Maintenabilité (Maintainability)

| Sous‑caractéristique | Métrique | Objectif | Méthode de mesure |
|----------------------|----------|----------|--------------------|
| **Modularité** | Couplage / Cohésion (CK, HC) mesurés par Sonar | **Couplage ≤ 15 %**, **Cohésion ≥ 0,75** | Sonar “cognitive complexity”, “package cohesion”. |
| **Réutilisabilité** | % de composants réutilisables (services, DAO) | **≥ 80 %** | Analyse du nombre de services génériques (`ReferenceService<T>`). |
| **Analysabilité** | Complexité cyclomatique moyenne | **≤ 10** | Sonar “cyclomatic_complexity”. |
| **Modifiabilité** | Temps moyen de modification (jours‑homme) | **≤ 0,5 j/h** pour une petite fonction (ex. ajout de champ) | Historique de commits + ticket de changement. |
| **Testabilité** | Couverture de tests unitaires | **≥ 80 %** (ligne) & **≥ 70 %** (branches) | Sonar “coverage” + JaCoCo. |

### 3.8 Portabilité (Portability)

| Sous‑caractéristique | Métrique | Objectif | Méthode de mesure |
|----------------------|----------|----------|--------------------|
| **Adaptabilité** | Nombre d’environnements supportés (OS/Serveur) | **3** (Linux Debian, RedHat, Windows) | Scripts d’installation (`assembly‑sources.xml`). |
| **Installabilité** | Temps d’installation standard (min) | **≤ 15 min** (déploiement WAR) | Playbook Ansible + mesure temps réel. |
| **Remplaçabilité** | Compatibilité avec formats standards (CSV, ODS) | **Oui** (déjà implémenté) | Tests d’import/export automatisés. |

---

## 4️⃣ Architecture Technique  

### 4.1 Diagramme de composants (texte)

```
+-------------------+       +-------------------+       +-------------------+
|  causialsmp-web  | <---> |  Castor JDO DAO   | <---> |   Oracle DB      |
| (Struts1, JSP)    |       | (GenericDao, ... )|       | (causalis schema)|
+-------------------+       +-------------------+       +-------------------+
          |                         ^
          |                         |
          v                         |
+-------------------+       +-------------------+
|  Service Layer   | <---> |  ReferenceService |
| (GradeService,    |       | (Domain, Statut) |
|  DomaineAffect... )|       +-------------------+
+-------------------+
          |
          v
+-------------------+
|  Synchronisation  |
| (SynchronizeSrv, |
|  TranscodageGrade)|
+-------------------+
          |
          v
+-------------------+
|  Export Layer    |
| (CausalisExportM.)|
+-------------------+
```

### 4.2 Justification des choix  

| Élément | Pourquoi ce choix ? |
|---------|---------------------|
| **Struts 1** | Hérité d’un contexte legacy, faible courbe d’apprentissage pour les équipes, intégration simple avec JSP et Castor. |
| **Castor JDO** | Mapping XML léger, compatible avec les bases Oracle déjà en place, aucune dépendance JPA. |
| **Oracle** | Base de données de référence de l’entreprise, scripts de migration déjà fournis. |
| **Maven multi‑module** | Séparation claire des préoccupations : DB scripts, packaging, documentation, application web. |
| **Tomcat** | Serveur d’applications Java EE standard, support JNDI datasource. |
| **Log4j 1.x** | Configuration simple via `log4j.xml`; déjà utilisé dans le projet. |
| **JUnit 4/5 + SonarQube** | Couverture de tests automatisés et métriques de qualité intégrées dans la chaîne CI. |
| **OWASP‑ZAP / ASVS** | Cadre reconnu pour les tests de sécurité d’applications web. |

---

## 5️⃣ Stack Technologique Qualifié  

| Catégorie | Technologie | Version (exemple) | Licence | Cycle de vie |
|-----------|-------------|-------------------|---------|---------------|
| **JDK** | OpenJDK 11 | LTS (support jusqu’en 2026) | GPL 2 + Classpath Exception | Actif |
| **Web Framework** | Apache Struts 1.3.10 | 1.3.x | Apache 2.0 | Maintenance (critical only) |
| **Persistance** | Castor JDO 1.4.1 | 1.4.x | Apache 2.0 | Actif |
| **DB** | Oracle 12c Release 2 | 12.2 | Commercial | Actif (support jusqu’en 2027) |
| **Build** | Apache Maven 3.8.5 | 3.x | Apache 2.0 | Actif |
| **Serveur d’app** | Apache Tomcat 9.0.58 | 9.x | Apache 2.0 | Actif |
| **Logging** | Log4j 1.2.17 | 1.x | Apache 2.0 | Maintenance (security patches) |
| **Tests Unitaires** | JUnit 4.13.2 / JUnit 5.8 | 4/5 | Eclipse Public License | Actif |
| **Analyse Qualité** | SonarQube 9.7 LTS | 9.x | LGPL 3.0 | Actif |
| **CI/CD** | GitLab‑CI 13.x | 13.x | MIT | Actif |
| **Sécurité** | OWASP‑ZAP 2.11.1 | 2.x | Apache 2.0 | Actif |
| **Monitoring** | Prometheus 2.34 + Grafana 9.2 | 2.x / 9.x | Apache 2.0 | Actif |

---

## 6️⃣ Stratégie de Test & Validation  

| Niveau | Outils | Scénarios | Critères d’acceptation |
|--------|--------|-----------|------------------------|
| **Unitaires** | JUnit 4/5, JaCoCo | Tous les `*Service`, `*Dao`, `*Predicate`, `*Helper` | Couverture ≥ 80 % ligne, ≥ 70 % branche |
| **Intégration** | Maven‑failsafe, DB‑Unit, H2 (mode Oracle) | DAO ↔ DB, Service ↔ DAO, Export ↔ Fichier, WS ↔ Stub | Tous les tests passent, aucune exception non‑gérée |
| **Fonctionnels** | Selenium WebDriver, StrutsTestCase | Création/édition/suppression dossiers, recherche, export, synchronisation | Temps de réponse ≤ 2 s, aucun défaut fonctionnel détecté |
| **Performance** | JMeter, Gatling | Chargement 50 U, pic 200 U, tests de stress | 95ᵉ percentile ≤ 2000 ms, CPU ≤ 70 % |
| **Sécurité** | OWASP‑ZAP, Sonar “security‑rules” | Scan d’injection SQL, XSS, CSRF, mauvaise configuration | Aucun problème de niveau high/critical, score ASVS ≥ 80 % |
| **Accessibilité** | axe‑core, WAVE | Vérification WCAG 2.1 sur toutes les JSP | Niveau AA validé sur 100 % des pages |
| **Acceptation** | GitLab‑CI pipelines + manuel | Déploiement sur environnement de pré‑production, validation métier | Tous les KPI (disponibilité, performance, sécurité) respectés → **Go‑Live** |

---

## 7️⃣ Supervision & Métriques en Production  

| Métrique | Source | Seuil d’alerte | Tableau de bord |
|----------|--------|----------------|-----------------|
| **Uptime** | Pingdom / Grafana (Prometheus `up` metric) | < 99,9 % → **Alerte critique** | Grafana “Availability”. |
| **Temps de réponse moyen** | Prometheus `http_request_duration_seconds` | > 2 s (95ᵗh) → **Alerte warning** | Grafana “Response Times”. |
| **CPU / RAM** | node‑exporter | CPU > 80 % ou RAM > 85 % → **Alerte warning** | Grafana “Resource Utilisation”. |
| **Erreurs HTTP 5xx** | Nginx/Tomcat access logs | > 5 % des requêtes → **Alerte critique** | Grafana “Error Rate”. |
| **Log4j ERROR/WARN** | Log4j appender → ElasticSearch | > 10 ERROR/min → **Alerte** | Kibana “Log Overview”. |
| **Défauts de sécurité** | SonarQube security hotspot, OWASP‑ZAP scan | Tout nouveau **critical** → **Alerte immédiate** | SonarQube “Security”. |
| **Transactions de synchronisation** | Application metrics (`synchronize.count`, `synchronize.errors`) | Échec > 0 → **Alerte** | Grafana “Sync Jobs”. |

---

## 8️⃣ Documentation Technique  

| Document | Format | Responsable | Norme |
|----------|--------|--------------|-------|
| **Code** | Javadoc (auto‑généré) | Développeurs | Javadoc 3.0 |
| **API WS** | WSDL + XSD (dans `ws/`) | Équipe intégration | WS‑I 1.1 |
| **Guide d’installation** | Markdown (`README.md` + `deployment/assembly‑sources.xml`) | Ops | GitLab‑CI Docs |
| **Manuel utilisateur** | Confluence (pages “Gestion dossiers”, “Export”, “Synchronisation”) | Business Analyst | ISO 9001 |
| **Run‑books** | YAML (Ansible playbooks) | Ops | ITIL v3 |
| **Matrice de traçabilité** | Excel/Google‑Sheets (CCF ↔ Qualité) | QA | IEEE 830 |

---

## 9️⃣ Gestion des Dettes Techniques  

| Zone de dette | Impact | Priorité | Plan de remboursement |
|---------------|--------|----------|-----------------------|
| **Struts 1 & Log4j 1** | Obsolescence, manque de correctifs de sécurité | **Moyenne** | Migration progressive vers Spring Boot + Logback (sprint Q4‑2024). |
| **DAO générique sans pagination** | Risque de **OOME** sur gros volumes | **Élevée** | Implémenter pagination (`LIMIT/OFFSET`) dans `ReferenceService` (sprint Q2‑2024). |
| **Classes utilitaires non‑génériques** (`ListeTableauEffectifs`, `ListeEntete…`) | Complexité accrue, faible réutilisabilité | **Faible** | Refactoriser en collections génériques (Java 8 Streams). |
| **Services vides** (`UtilisateurService`, `RechercheDossiersMaladiesDAO`) | Fonctionnalité manquante, confusion | **Moyenne** | Définir cahier des charges fonctionnel, implémenter (sprint Q3‑2024). |
| **Absence de REST** | Difficulté d’intégration avec nouveaux front‑ends | **Moyenne** | Ajouter façade REST (Spring MVC) autour des services existants (road‑map 2025). |
| **Gestion de la configuration** (hard‑coded JNDI, `Constantes.NOMDATASOURCE`) | Risque d’erreur en environnement multi‑env | **Élevée** | Centraliser dans `application.yml` (Spring Boot) ou `properties` externalisés. |
| **Manque de tests de charge** | Incertitude sur la capacité réelle | **Faible** | Ajouter JMeter scripts (sprint Q2‑2024). |

---

## 🔟 Annexes  

### 10.1 Matrice de traçabilité CCF ↔ Qualité  

| CCF (Exigence) | Fonctionnalité | Performance | Compatibilité | Utilisabilité | Fiabilité | Sécurité | Maintenabilité | Portabilité |
|----------------|----------------|--------------|--------------|----------------|-----------|----------|----------------|-------------|
| **Gestion dossiers accident** | ✔︎ | ✔︎ (temps de réponse) | ✔︎ (CSV/ODS) | ✔︎ (SUS) | ✔︎ (MTTR) | ✔︎ (auth SSO) | ✔︎ (modularité DAO) | ✔︎ (Linux/Windows) |
| **Gestion dossiers maladie** | ✔︎ | ✔︎ | ✔︎ | ✔︎ | ✔︎ | ✔︎ | ✔︎ | ✔︎ |
| **Export OpenOffice/CSV** | ✔︎ | ✔︎ (taille fichier) | ✔︎ (format ODS) | ✔︎ (interface simple) | ✔︎ (pas d’interruption) | ✔︎ (contrôle accès) | ✔︎ (service Export) | ✔︎ (portable) |
| **Synchronisation grades ↔ Rehucit** | ✔︎ | ✔︎ (batch) | ✔︎ (WS SOAP) | — | ✔︎ (retry) | ✔︎ (WS‑Sec) | ✔︎ (Predicate) | ✔︎ (déploiement) |
| **Recherche avancée** | ✔︎ | ✔︎ (index) | ✔︎ (paramètres) | ✔︎ (formulaires) | ✔︎ (pas de perte) | ✔︎ (validation) | ✔︎ (DAO) | ✔︎ (multi‑env) |
| **Pagination** | ✔︎ | ✔︎ (limite) | — | ✔︎ (UX) | — | — | ✔︎ (config) | — |
| **SSO Cerbere** | ✔︎ | — | — | — | ✔︎ (session mgmt) | ✔︎ (token) | — | — |

> **✔︎** = exigence satisfaite par la sous‑caractéristique correspondante.  

### 10.2 Exemple de scénario de test de performance (JMeter)

```jmx
Test Plan
 └─ Thread Group (50 users, ramp‑up 30s, loop 10)
     ├─ HTTP Request – GET /causalismp-web/dossiers.do?type=accident
     ├─ HTTP Request – POST /causalismp-web/dossiers.do (create)
     └─ Response Assertion – Temps de réponse < 2000 ms
```

### 10.3 Exemple de règle SonarQube personnalisée  

```yaml
# quality-profile.yml
rules:
  - key: java:S1192
    severity: BLOCKER
    status: ACTIVE
    params: {}
  - key: java:S00112
    severity: MAJOR
    status: ACTIVE
```

---

## 📌 Conclusion  

Le **Cahier des Spécifications Techniques** ci‑dessus traduit le **modèle de qualité ISO/IEC 25010** en exigences mesurables et en actions concrètes pour le projet **causalismp**.  

- **Tous les objectifs** (fonctionnalité, performance, sécurité, etc.) sont définis avec des **valeurs chiffrées** et des **méthodes de vérification** intégrées à la chaîne CI/CD.  
- L’**architecture** est clairement délimitée, les **choix technologiques** sont justifiés et les **risques** identifiés.  
- Un **plan de tests complet** couvre les niveaux unitaires → sécurité → performance.  
- La **surveillance en production** repose sur des métriques fiables et des alertes automatisées.  
- La **gestion de la dette technique** propose un roadmap réaliste pour moderniser le stack (Struts 1 → Spring Boot, Log4j 1 → Logback, ajout de REST, pagination, etc.).  

En suivant ce CST, l’équipe pourra :

1. **Garantir** la conformité aux exigences de qualité définies par la norme ISO/IEC 25010.  
2. **Mesurer** objectivement la performance, la fiabilité et la sécurité du produit.  
3. **Piloter** les évolutions futures tout en maîtrisant la dette technique.  

---  

*Document élaboré à partir de l’analyse du code source (`causalismp‑code.filtered.md`), du résumé (`causalismp‑code.summarized.md`) et du wiki d’équipe (`causalismp.wiki.md`).*  
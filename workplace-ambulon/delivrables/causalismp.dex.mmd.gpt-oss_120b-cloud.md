# 📚 Dossier d’Exploitation (DEX) – **causalismp**  
*Document de référence garantissant la continuité, la maintenabilité et la sécurisation de l’exploitation d’une application en production*  

> **Établi sur les principes de la transition `Build → Run` et des bonnes pratiques ITIL / DevOps pour l’exploitation applicative**  

---

[TOC]

---  

## 1️⃣ Introduction et objectifs 🎯  

| 🎯 Objectif | ✅ Description |
|-------------|----------------|
| **Continuité de service** | Assurer le bon fonctionnement de l’application de gestion des accidents du travail et des maladies professionnelles 24 h/24 7 j/7. |
| **Documentation opérationnelle** | Centraliser les procédures quotidiennes, les scripts de maintenance et les contacts clés. |
| **Support & résolution d’incidents** | Fournir aux équipes de support les informations nécessaires pour diagnostiquer et corriger rapidement les dysfonctionnements. |
| **Responsabilités clairement définies** | Délimiter les rôles entre **Développement**, **Exploitation**, **Sécurité** et **Support**. |
| **Conformité & maîtrise des risques** | Garantir le respect des exigences réglementaires (RGPD, archivage légal) et des politiques internes (SLA, backup, sécurité). |
| **Accompagnement de la phase `Build → Run`** | Formaliser la passation du livrable de l’équipe de développement vers l’équipe d’exploitation. |

---  

## 2️⃣ Contexte d’usage et périmètre 🌐  

| 📦 Livrable | ✅ Valeur |
|-------------|----------|
| **Type** | Standard ✅ |
| **Nature** | Document de référence 📘 |
| **Activité** | Transition **Build → Run** / Exploitation |
| **Quand l’utiliser** | <ul><li>Avant chaque mise en production (Go‑Live)</li><li>Comme support de formation des nouvelles équipes d’exploitation</li><li>Pour les audits de conformité, PRA/PCA, revues de sécurité</li></ul> |
| **Cycle de vie** | Document vivant – mise à jour à chaque évolution fonctionnelle, technique ou d’infrastructure. |

---  

## 3️⃣ Pré‑requis et jalons ✅  

- [ ] **Architecture technique validée** (schémas, mapping Castor, diagrammes d’infrastructure).  
- [ ] **Environnement de production stabilisé** (accès JNDI `java:comp/env/jdbc/userDScausalis`, DNS, certificats).  
- [ ] **Politiques définies** (sauvegarde, supervision, sécurité, SLA).  
- [ ] **Contacts clés identifiés** (métier, technique, support, sécurité).  
- [ ] **Outillage en place** (monitoring, logging, ordonnanceur, gestion des secrets).  

> ⏱ **Jalon critique** – Le DEX doit être **validé et signé** avant tout déploiement en production. Aucun lancement ne doit intervenir sans un DEX approuvé.  

---  

## 4️⃣ Gouvernance et rôles 👥  

| Rôle | Profil type | Responsabilité |
|------|-------------|----------------|
| **Rédacteur principal** | Tech Lead / DevOps / Référent Prod | Rédaction, structuration, intégration des spécifications techniques. |
| **Validateur Exploitation** | Chef d’exploitation / Responsable support | Vérification de l’opérabilité et de la complétude. |
| **Validateur Sécurité / Conformité** | RSSI / DPO / Auditeur interne | Validation des procédures de sécurité, backup, conformité RGPD. |
| **Mainteneur** | Équipe projet / PO technique | Mise à jour continue à chaque release ou changement d’infra. |

---  

## 5️⃣ Structure détaillée du DEX (16 sections standards) 📑  

| N° | Section | Contenu attendu (extraits spécifiques à **causalismp**) |
|---:|----------|--------------------------------------------------------|
| 1 | **Généralités** | • **Objet** : Exploitation de l’application *causalismp* (gestion des accidents du travail & maladies professionnelles). <br>• **Audience** : équipes d’exploitation, support, sécurité, management. <br>• **Version** : `v${project.causalis.version}` (défini dans `version.properties`). |
| 2 | **Documents applicables et de référence** | • `pom.xml` (Maven multi‑module). <br>• `assembly.xml`, `assembly-sources.xml` (packaging). <br>• `database.xml` (Castor JDO). <br>• `web.xml`, `struts-config.xml` (Struts 1). <br>• `README.md` (contexte projet). |
| 3 | **Terminologie** | • **DEX** – Dossier d’Exploitation. <br>• **SLA** – Service Level Agreement. <br>• **PRA/PCA** – Plan de Reprise d’Activité / Plan de Continuité d’Activité. <br>• **JNDI** – Java Naming and Directory Interface. |
| 4 | **Spécificités** | • **SLA** : Disponibilité 99,5 % (heure ouvrée 08 h–18 h). <br>• **Contacts** :<br> - **Production** : `prod-support@company.com` / +33 1 23 45 67 89. <br> - **Développement** : `dev-team@company.com`. <br>• **Matrice d’escalade** : Niveau 1 → Niveau 2 → Niveau 3 (RSSI). |
| 5 | **Architecture** | **Vue logique** : <br>• **Web‑app** (`causalismp‑web`) – Struts 1, JSP, WAR. <br>• **Persist‑layer** – Castor JDO + Oracle DB (`causalismp‑database`). <br>• **Services externes** – Web‑services *StubWS.jar* (synchronisation grades). <br>**Vue physique** : serveur d’application (Tomcat 9) → datasource JNDI `jdbc/userDScausalis` → Oracle 12c. |
| 6 | **Serveurs** | • **App‑server** : `app01.causalismp.prod.company.com` (Linux RHEL 8, Tomcat 9, Java 1.8). <br>• **DB‑server** : `db01.causalismp.prod.company.com` (Oracle 12c). <br>• **IP/DNS** : à compléter (`[IP]`). |
| 7 | **Application** | • **Artefact** : `causalismp-web.war`. <br>• **Version** : `${project.causalis.version}`. <br>• **Paramètres** : `<context-param>` dans `web.xml` (ex. `pagination.max=30`). <br>• **Procédure de déploiement** : `mvn clean package && cp target/causalismp-web.war /opt/tomcat/webapps/`. |
| 8 | **Supervision et métrologie** | • **Outils** : Grafana + Prometheus (exposition métriques via JMX Exporter). <br>• **Seuils d’alerte** : CPU > 80 % 5 min, mémoire > 85 %, temps de réponse HTTP > 3 s. <br>• **Dashboards** : “Causalismp – Health”, “DB – Sessions”. |
| 9 | **Sauvegarde** | • **Fréquence** : Quotidienne (full) + incrémentale toutes les 6 h. <br>• **Rétention** : 30 jours (full), 7 jours (incrémentale). <br>• **Localisation** : NAS `nas01.backup.company.com` (NFS). <br>• **Procédure de restauration** : `RMAN` + scripts `restore_*.sql`. |
| 10 | **Stockage** | • **Volumes** : `/opt/tomcat/logs` (logrotate 7 jours), `/opt/tomcat/webapps` (WAR). <br>• **Quotas** : 10 Go (logs), 5 Go (temp). |
| 11 | **Inventaire des bases** | • **Base** : `CAUSALIS` (Oracle). <br>• **Schéma** : `CAUSALIS_USER`. <br>• **Tables principales** : `ACCIDENT`, `GRAD`, `SERVICE`, `STATUT`, `TRANSCODAGE_GRADE`. <br>• **Utilisateurs** : `causalis_app` (lecture/écriture), `causalis_report` (lecture seule). |
| 12 | **Flux inter‑applicatifs** | • **Web‑service** : `StubWS.jar` expose `GradeService` → `TranscodageGrade`. <br>• **Protocoles** : HTTP / HTTPS (TLS 1.2). <br>• **Authentification** : Basic Auth (API‑key). |
| 13 | **Plan de production** | • **Ordonnancement** : <br> - **CRON** `0 2 * * *` – exécution du batch de synchronisation (`SynchronizeService`). <br> - **Fenêtre de maintenance** : chaque dimanche 02 h–04 h (déploiement, DB scripts). |
| 14 | **Sécurisation des images** | • **Scan vulnérabilités** : Trivy sur l’image Docker (`causalismp-web:latest`). <br>• **Hardening** : désactivation du compte `root` dans le conteneur, utilisation d’un utilisateur non‑privileged (`causalis`). |
| 15 | **Opérations courantes** | • **Check‑list jour** : <br> 1. Vérifier les alertes JMX/Prometheus. <br> 2. Contrôler l’espace disque (`df -h`). <br> 3. S’assurer du bon déroulement du batch de synchronisation. <br>• **Gestion des logs** : rotation via `logrotate` (7 jours). <br>• **Erreurs connues** : `TechnicalException` lié à `DBTools` – vérifier les connexions Castor. |
| 16 | **Opérations récurrentes** | • **Gestion des comptes** : revue trimestrielle des utilisateurs JNDI et des API‑keys. <br>• **Rotation des certificats** : tous les 12 mois (TLS). <br>• **Nettoyage** : purge des dossiers `tmp/` > 30 jours. <br>• **Audit** : audit de conformité RGPD semestriel. |

> **⚠️ Note** : Les champs marqués `[À COMPLÉTER]` devront être remplis avec les valeurs exactes de votre environnement (adresses IP, contacts, etc.) lors de la finalisation du DEX.  

---  

## 6️⃣ Diagramme Mermaid du cycle de vie du DEX  

```mermaid
graph TB
    %% Styles;
    classDef dev fill:#E3F2FD,stroke:#1976D2,stroke-width_2px;
    classDef ops fill:#E3F2FD,stroke:#1976D2,stroke-width_2px;
    classDef sec fill:#E3F2FD,stroke:#1976D2,stroke-width_2px;
    classDef maint fill:#E3F2FD,stroke:#1976D2,stroke-width_2px;
    classDef phase1 fill:#add8e6,stroke:#1976D2,stroke-width_2px;
    classDef phase2 fill:#90ee90,stroke:#1976D2,stroke-width_2px;
    classDef phase3 fill:#ffff99,stroke:#1976D2,stroke-width_2px;
    classDef phase4 fill:#e6e6fa,stroke:#1976D2,stroke-width_2px;

    %% Actors;
    actor dev as "Équipe Dev / Tech Lead"
    actor ops as "Équipe Ops / Support"
    actor sec as "Équipe Sécurité"
    actor maint as "Équipe Maintien"

    %% Phases;
    subgraph p1["Phase 1 – Rédaction"]
    direction TB;
    step1(("Collecte des specs & architecture"))
    step2(("Rédaction des 16 sections DEX"))
    end
    subgraph p2["Phase 2 – Validation croisée"]
    direction TB;
    step3(("Revue technique (DevOps/Infra)"))
    step4(("Validation ops & support"))
    step5(("Validation sécurité & conformité"))
    end
    subgraph p3["Phase 3 – Go‑Live & Run"]
    direction TB;
    step6(("Signature & archivage versionné"))
    step7(("Intégration run‑book & supervision"))
    end
    subgraph p4["Phase 4 – Maintenance continue"]
    direction TB;
    step8(("Mise à jour à chaque release"))
    step9(("Revue trimestrielle ou post‑incident"))
    end
    %% Links;
    dev -->|Alimente| step1;
    dev -->|Rédige| step2;
    ops -->|Vérifie| step3;
    ops -->|Valide opérabilité| step4;
    sec -->|Valide conformité| step5;
    step5 -->|Accord go‑live| step6;
    step6 -->|Déploiement| step7;
    maint -->|Met à jour| step8;
    step9 -.->|Boucle d’amélioration| step2;
    %% Notes;
    note1["<b>Points de contrôle</b>\n- Complétude des accès\n- Procédures de rollback\n- Matrice d’escalade testée"]:::phase2;
    note2["<b>Règle d’or</b>\nPas de mise en production\nsans DEX à jour"]:::phase4;
    p2 -->|Points de contrôle| note1;
    p4 -->|Règle d’or| note2;
    class dev,ops,sec,maint dev,ops,sec,maint;
    class step1,step2,step3,step4,step5,step6,step7,step8,step9 phase1,phase2,phase3,phase4;
```

---  

## 7️⃣ Conseils de rédaction et maintenance 🛠  

| Bonne pratique | À éviter |
|----------------|----------|
| Utiliser un **dépot versionné** (Git) avec historique complet du DEX. | Stocker le DEX en pièce jointe email ou sur un partage non versionné. |
| Rédiger en **langage clair, orienté action** (ex. : “Vérifier le disque : `df -h`”). | Utiliser des descriptions vagues ou purement théoriques. |
| Inclure **captures d’écran**, chemins exacts et commandes. | Laisser des placeholders `[À COMPLÉTER]` en production. |
| Prévoir une **revue systématique** à chaque release majeure. | Considérer le DEX comme un document “jetable” post‑lancement. |
| **Lier** le DEX aux run‑books, tickets d’incident et procédures PRA. | Isoler le DEX des outils de supervision et de ticketing. |

---  

## 8️⃣ Adaptations contextuelles 📦  

| Contexte | Adaptation recommandée |
|----------|------------------------|
| **Applications Cloud / Serverless** | Remplacer la section **Serveurs** par **Services managés**, IAM, limites de quotas, configuration as Code. |
| **Secteur réglementé (Santé, Finance, Public)** | Renforcer les sections **Sécurité**, **Traçabilité**, **Archivage légal**, conformité **RGAA/ANSSI**. |
| **Legacy / Monolithe** | Insister sur la dépendance OS, les patches, la compatibilité, les procédures de reprise manuelle. |
| **Microservices / Kubernetes** | Remplacer **Inventaire serveurs / bases** par **Clusters, Namespaces, Helm/Manifests, Observabilité** (Prometheus/Grafana/Loki). |

---  

## 9️⃣ Livrables et intégration 🚀  

| Livrable | Format | Usage |
|----------|--------|-------|
| **DEX versionné** | `DEX_causalismp_vX.Y.Z.md` (Markdown) ou `PDF` exporté | Référence principale pour l’exploitation. |
| **Checklist de validation** | Tableur ou Markdown | Signatures des parties prenantes (Dev, Ops, Sec). |
| **Matrice de traçabilité** | Tableur | Lien DEX ↔ Architecture ↔ Runbooks ↔ Tickets support. |
| **Intégration CI/CD** | Pipeline GitLab CI (`.gitlab-ci.yml`) | Validation automatisée (lint du Markdown, vérif. liens internes). |
| **Liens DEX** | Ajout dans les pages d’accueil de supervision (Grafana, Datadog) | Accès rapide depuis les dashboards. |
| **Génération automatique** | Scripts `generate-dex.sh` (ex. : `sed` sur les placeholders) | Automatisation de la mise à jour des sections version, contacts, etc. |

---  

## 🔎 Mini‑glossaire  

| Acronyme | Signification |
|----------|---------------|
| **DEX** | Dossier d’Exploitation |
| **SLA** | Service Level Agreement |
| **PRA** | Plan de Reprise d’Activité |
| **PCA** | Plan de Continuité d’Activité |
| **JNDI** | Java Naming and Directory Interface |
| **IAM** | Identity and Access Management |
| **RGPD** | Règlement Général sur la Protection des Données |
| **TLS** | Transport Layer Security |
| **CRON** | Planificateur de tâches Unix |
| **JMX** | Java Management Extensions |

---  

## 📌 Mentions légales  

*Document établi sur les principes de la transition **Build → Run** et des bonnes pratiques **ITIL/DevOps** pour l’exploitation applicative.*  

---  

### 📂 Navigation interne  

- Retour à l'**[Introduction et objectifs](#1️⃣-introduction-et-objectifs-🎯)**  
- Retour à la **[Structure détaillée du DEX](#5️⃣-structure-détaillée-du-dex-📑)**  
- Retour au **[Diagramme Mermaid](#6️⃣-diagramme-mermaid-du-cycle-de-vie-du-dex)**  
- Retour aux **[Conseils de rédaction](#7️⃣-conseils-de-rédaction-et-maintenance-🛠)**  

---  

*Ce DEX est prêt à être intégré dans votre dépôt Git (VS Code, Obsidian, Confluence) ou exporté en PDF pour diffusion.*
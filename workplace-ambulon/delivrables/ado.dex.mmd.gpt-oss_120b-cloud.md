# 📘 DEX – Dossier d’Exploitation (DEX)  
**Projet :** ADO – Consultation des dossiers RH archivés (ReHucit)  
**Version du DEX** : 1.0 – 2024‑06‑27  

---

[TOC]

---

## 1️⃣ Introduction et objectifs

> **Document de référence garantissant la continuité, la maintenabilité et la sécurisation de l’exploitation d’une application en production.**

### 🎯 Objectifs opérationnels

| ✅ | Objectif |
|----|-----------|
| ✅ | Assurer la continuité de service (SLA/DICT) |
| ✅ | Documenter les procédures de gestion courante (requêtes, rapports, sauvegarde, purge) |
| ✅ | Faciliter le support et la résolution d’incidents |
| ✅ | Encadrer les responsabilités (Dev / Ops / Support) |
| ✅ | Assurer la conformité (RGPD, DICT, sécurité) |
| ✅ | Accompagner la phase de transition **Build → Run** |

---

## 2️⃣ Contexte d’usage et périmètre

| Élément | Valeur |
|---------|--------|
| **Type de livrable** | Standard ✅ |
| **Nature** | Document de référence 📘 |
| **Activité** | Transition **Build → Run / Exploitation** |
| **Quand l’utiliser** | - Avant chaque mise en production (go‑live) <br> - Pour la formation des équipes d’exploitation <br> - Lors d’audits conformité, PRA/PCA, revue sécurité |
| **Cycle de vie** | Document vivant – mise à jour à chaque évolution fonctionnelle, technique ou d’infrastructure (ex. version Spring Boot, schéma DB, changements de SLA) |

---

## 3️⃣ Pré‑requis et jalons

- [ ] Architecture technique validée (schéma DB, scripts d’index, fonction `array_uniq_stable`)  
- [ ] Environnement de production stabilisé (accès réseau, DNS, certificats HTTPS)  
- [ ] Politiques définies : sauvegarde, supervision, sécurité, SLA/DICT, RGPD  
- [ ] Contacts clés identifiés (MOA, MOE, RSSI, support) – voir section **6**  
- [ ] Outillage prêt : monitoring (ex. Prometheus / Grafana), logging, ordonnanceur, gestion des secrets (Vault)  

> **⏱ Jalon critique** – Le DEX doit être **validé et signé** *avant* toute mise en production. Aucun déploiement ne doit intervenir sans un DEX à jour.

---

## 4️⃣ Gouvernance et rôles

| Rôle | Profil type | Responsabilité |
|------|-------------|----------------|
| **Rédacteur principal** | Tech Lead / DevOps / Référent Prod | Rédaction, structuration, intégration des spécifications techniques |
| **Validateur Exploitation** | Chef d’exploitation / Responsable support | Vérification de l’opérabilité, exhaustivité du DEX |
| **Validateur Sécurité/Conformité** | RSSI / DPO / Auditeur interne | Validation des procédures de sécurité, sauvegarde, conformité RGPD & DICT |
| **Mainteneur** | Équipe projet / Product Owner technique | Mise à jour continue à chaque release ou changement d’infra |
| **Support fonctionnel** | Service d’administration centrale | Gestion des demandes utilisateurs, escalade métier |
| **MOA / MOE** | SG/DRH / SG/DNUM/PNM/DPNM3 | Validation fonctionnelle et technique, pilotage projet |

---

## 5️⃣ Structure détaillée du DEX (16 sections)

| N° | Section principale | Contenu attendu (exemples) |
|---:|-------------------|----------------------------|
| 1 | **Généralités** | Objet, domaine d’application, audience (exploitation, support, MOA), version du document |
| 2 | **Documents applicables et de référence** | Normes internes (RGPD, DICT, ISO 27001), chartes, documents d’architecture, politiques sécurité, procédures backup |
| 3 | **Terminologie** | Glossaire (ex. RGP, RRH, “agent”, “rapport”, “mini‑CV”, “PIP”, “quota”) |
| 4 | **Spécificités** | Fonctionnalités critiques (consultation historique, génération de rapports Jasper, purge du journal), SLA/DICT (ex. Disponibilité = 1, Intégrité = 3, Traçabilité = 2, Confidentialité = 3) |
| 5 | **Architecture** | Schéma logique (Spring Boot → PostgreSQL), flux de données (requêtes → repository → service → controller → UI), infrastructure prod (IaaS Paris La Défense, HA, réplication) |
| 6 | **Serveurs** | Accès (SSH, HTTPS), OS (Linux CentOS 7), ressources (CPU 4 vCPU, RAM 8 Go, stockage 200 Go), DNS/URL (`ado.e2.rie.gouv.fr`) |
| 7 | **Application** | Modules (`ado‑web`, `ado‑database`), versions (Spring Boot 2.6.x, Java 11), paramètres (`application.properties`), procédure de déploiement (CI → Docker → K8s) |
| 8 | **Supervision et métrologie** | Outils (Prometheus + Grafana, ELK), seuils d’alerte (latence API > 2 s, DB > 90 % CPU), dashboards (requêtes, journaux, santé JVM) |
| 9 | **Sauvegarde** | Fréquence (quotidienne incrémentale + weekly full), rétention (30 jours), localisation (Vault → Data‑Center Paris), procédure de restauration (scripts `restore.sh`) |
|10| **Stockage** | Volumes PostgreSQL (PGDATA), chemins (`/var/lib/pgsql/data`), quotas, rotation des logs |
|11| **Inventaire des bases** | DB `ado_recette` / `ado_prod`, version PostgreSQL 13, utilisateurs (`ado_read`, `ado_write`), maintenance (VACUUM auto) |
|12| **Flux inter‑applicatifs** | Aucun échange externe (application autonome) – exposition uniquement via HTTPS |
|13| **Plan de production** | Ordonnancement (cron → `purge.sh` chaque dimanche 00 h), fenêtres de maintenance (samedi 02 h‑04 h) |
|14| **Sécurisation des images** | Scans de vulnérabilités Docker (`trivy`), hardening (user `appuser`), gestion des secrets (HashiCorp Vault) |
|15| **Opérations courantes** | Check‑list quotidienne (vérif logs, état health‑endpoints), gestion des erreurs connues (ex. `JReportExportException`), diagnostic (curl, pgAdmin) |
|16| **Opérations récurrentes** | Rotation des certificats (90 jours), mise à jour des dépendances (Maven → versions propre), audit de conformité semestriel, revue de la matrice d’escalade |

---

## 6️⃣ Diagramme Mermaid du cycle de vie DEX

```mermaid
graph TB;
    %% Styles;
    style dev fill:#E3F2FD,stroke:#1976D2,stroke-width_2px;
    style ops fill:#E3F2FD,stroke:#1976D2,stroke-width_2px;
    style sec fill:#E3F2FD,stroke:#1976D2,stroke-width_2px;
    style maint fill:#E3F2FD,stroke:#1976D2,stroke-width_2px;
    style p1 fill:#add8e6,stroke:#1976D2,stroke-width_2px;
    style p2 fill:#90ee90,stroke:#1976D2,stroke-width_2px;
    style p3 fill:#ffff99,stroke:#1976D2,stroke-width_2px;
    style p4 fill:#e6e6fa,stroke:#1976D2,stroke-width_2px;
    %% Acteurs;
    actor dev as "Équipe Dev / Tech Lead"
    actor ops as "Équipe Ops / Support"
    actor sec as "RSSI / DPO"
    actor maint as "Mainteneur DEX"

    %% Phases;
    subgraph p1["Phase 1 – Rédaction"]
        step1(("Collecte des specs & architecture"))
        step2(("Rédaction des 16 sections DEX"))
    end;
    subgraph p2["Phase 2 – Validation croisée"]
        step3(("Revue technique (DevOps/Infra)"))
        step4(("Validation exploitation & support"))
        step5(("Validation sécurité & conformité"))
    end;
    subgraph p3["Phase 3 – Go‑Live & Run"]
        step6(("Signature & archivage versionné"))
        step7(("Intégration run‑book & supervision"))
    end;
    subgraph p4["Phase 4 – Maintenance continue"]
        step8(("Mise à jour à chaque release"))
        step9(("Revue trimestrielle / post‑incident"))
    end;
    %% Flux;
    dev -->|Alimente| step1;
    dev -->|Rédige| step2;
    ops -->|Vérifie| step3;
    ops -->|Valide opérabilité| step4;
    sec -->|Valide conformité| step5;
    step5 -->|Accord go‑live| step6;
    step6 -->|Déploiement| step7;
    maint -->|Met à jour| step8;
    step9 -.->|Boucle d'amélioration| step2;
    %% Notes;
    note1["<b>Points de contrôle</b>\n- Complétude des accès\n- Procédures de rollback\n- Matrice d’escalade testée"]
    note2["<b>Règle d’or</b>\nPas de mise en production sans DEX à jour"]
    p2 -->|Points de contrôle| note1;
    p4 -->|Règle d’or| note2;
    %% Clickable (facultatif)
    click p1 "javascript_void(0)" "Phase 1 – Rédaction"
    click p2 "javascript_void(0)" "Phase 2 – Validation"
    click p3 "javascript_void(0)" "Phase 3 – Go‑Live"
    click p4 "javascript_void(0)" "Phase 4 – Maintenance"
```

---

## 7️⃣ Conseils de rédaction et maintenance

| ✅ Bonne pratique | ❌ À éviter |
|-------------------|--------------|
| Utiliser un dépôt **Git** versionné (branch `dex/main`) avec historique clair | Stocker le DEX en pièce jointe email ou sur un partage non versionné |
| Rédiger en langage clair, orienté **action** (ex. « Vérifier le health‑endpoint /health toutes les 5 min ») | Rédiger des descriptions vagues ou purement théoriques |
| Inclure des chemins exacts, captures d’écran et commandes (ex. `kubectl get pod -n ado`) | Laisser des placeholders `[À COMPLÉTER]` en production |
| Planifier une revue à chaque **release majeure** (ex. upgrade Spring Boot, changement de schéma) | Considérer le DEX comme un document « jetable » post‑déploiement |
| Lier le DEX aux **runbooks**, tickets d’incident et procédures PRA/PCA | Isoler le DEX des outils de supervision et de ticketing |

---

## 8️⃣ Adaptations contextuelles

| Contexte | Adaptation recommandée |
|----------|-----------------------|
| **Applications Cloud / Serverless** | Remplacer la section **Serveurs** par **Services managés**, IAM, quotas, etc. |
| **Secteur réglementé (RH, données personnelles)** | Renforcer les sections **Sécurité**, **RGPD**, **DICT**, ajouter la matrice de traçabilité des accès. |
| **Legacy / Monolithe** | Insister sur la dépendance OS, les patches OS, les scripts de reprise manuelle du serveur. |
| **Microservices / Kubernetes** | Remplacer **Serveurs** par **Clusters, Namespaces, Helm charts**, ajouter la supervision Prometheus/Grafana, les probes liveness/readiness. |

*ADO* est un **monolithe Spring Boot** déployé sur des **VM Linux** en IaaS Paris La Défense ; la version présentée ci‑dessus correspond donc à la configuration **On‑Prem / VM**.

---

## 9️⃣ Livrables et intégration

| Livrable immédiat | Description |
|-------------------|-------------|
| **DEX versionné** (`DEX_ADO_v1.0.md`) | Fichier Markdown versionné dans le dépôt Git (`dex/main`) |
| **Checklist de validation** | Tableau de signatures (Dev, Ops, Sécurité) à signer avant le go‑live |
| **Matrice de traçabilité** | Liens DEX ↔ Architecture ↔ Runbooks ↔ Tickets support (ex. JIRA `ADO-123`) |

### Intégration continue (CI/CD)

- **Pipeline** : `mvn clean verify` → `docker build` → `helm upgrade` → **step** `validate-dex` (script qui vérifie la présence du fichier `DEX_*.md` et sa version).  
- **Dashboard** : Ajout d’un lien vers le DEX dans le Grafana dashboard “ADO – Overview”.  
- **Documentation as Code** : Le DEX est généré en PDF automatiquement via `pandoc` dans le job `publish-docs`.

---

## 🔐 Sécurité & Conformité (extraits)

| Aspect | Détails |
|--------|---------|
| **DICT** | Disponibilité = 1, Intégrité = 3, Traçabilité = 2, Confidentialité = 3 |
| **RGPD** | Traitement de données à caractère personnel (NIR, données RH) – registre DPD : **Oui** |
| **Sauvegarde** | Volume PostgreSQL sauvegardé quotidiennement, rétention 30 jours, chiffrement AES‑256 |
| **Accès** | Authentification unique via filtre `FiltreCerbere` (SSO / SAML) – droits “lecture‑seule” pour les utilisateurs métier |
| **PRA/PCA** | Serveur principal en zone A, réplica en zone B, bascule automatisée (failover) sous 5 min |
| **Gestion des secrets** | Secrets (DB password, JWT secret) stockés dans **HashiCorp Vault**, accès limité aux comptes de service |

---

## 📅 Historique du DEX

| Version | Date | Auteur | Modifications |
|---------|------|--------|---------------|
| 1.0 | 2024‑06‑27 | IA (Assistant) | Création du DEX à partir des sources `ado.*` et des documents métier |
| — | — | — | — |

---

## 📎 Annexes (liens internes)

- ↩ Retour à l’[sommaire](#toc)  
- ↩ Retour à la [section 5 – Architecture](#5---architecture)  
- ↩ Retour à la [section 9 — Livrables](#9livrables-et-intégration)  

---

*Document établi sur les principes de la transition **Build → Run** et des bonnes pratiques **ITIL/DevOps** pour l’exploitation applicative.*
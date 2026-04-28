# 📘 Dossier d’Exploitation (DEX) – **agile‑back**  

> **Document établi sur les principes de la transition Build → Run et des bonnes pratiques ITIL/DevOps pour l’exploitation applicative**  

---  

## 📑 Table des matières  
[TOC]

---  

## 🎯 1. Introduction et objectifs  

> Document de référence garantissant la continuité, la maintenabilité et la sécurisation de l’exploitation d’une application en production.  

| ✅ Objectif | Description |
|---|---|
| **Assurer la continuité de service** | Procédures de démarrage, surveillance et reprise après incident. |
| **Documenter les procédures de gestion courante** | Check‑lists quotidiennes, hebdomadaires et mensuelles. |
| **Faciliter le support et la résolution d’incidents** | Matrice d’escalade, contacts clés et scripts de diagnostic. |
| **Encadrer les responsabilités (Dev / Ops / Sécurité)** | Rôles clairement définis et validés. |
| **Assurer la conformité et la maîtrise des risques** | Politique de sauvegarde, de mise à jour et de suivi des vulnérabilités. |
| **Accompagner la phase de transition Build → Run** | Points de contrôle à chaque jalon de mise en production. |

---  

## 📦 2. Contexte d’usage et périmètre  

| Élément | Valeur |
|---|---|
| **Type de livrable** | Standard ✅ |
| **Nature** | Document de référence 📘 |
| **Activité** | Transition Build → Run / Exploitation |
| **Quand l’utiliser** | • Avant chaque mise en production  <br>• Pour la formation des équipes d’exploitation <br>• Lors d’audits de conformité, PRA/PCA, revues de sécurité |
| **Cycle de vie** | Document vivant – mise à jour à chaque évolution fonctionnelle, technique ou d’infrastructure. |

---  

## 📋 3. Pré‑requis et jalons  

- [ ] Architecture technique validée et schémas à jour  
- [ ] Environnement de production stabilisé (accès réseau, DNS, certificats)  
- [ ] Politiques définies : sauvegarde, supervision, sécurité, SLA  
- [ ] Contacts clés identifiés (métiers, technique, support, sécurité)  
- [ ] Outillage prêt : monitoring (Monolog + Grafana), logging, ordonnanceur (cron), gestion des secrets  

> ⏱ **Jalon critique** – Le DEX doit être **validé et signé** avant toute mise en service. Aucun déploiement ne doit intervenir sans un DEX approuvé.  

---  

## 👥 4. Gouvernance et rôles  

| Rôle | Profil type | Responsabilité |
|------|-------------|----------------|
| **Rédacteur principal** | Tech Lead / DevOps / Référent Prod | Rédaction, structuration, intégration des spécifications techniques |
| **Validateur Exploitation** | Chef d’exploitation / Responsable support | Vérification de l’opérabilité et de la complétude |
| **Validateur Sécurité / Conformité** | RSSI / DPO / Auditeur interne | Validation des procédures de sécurité, backup, conformité |
| **Mainteneur** | Équipe projet / PO technique | Mise à jour continue à chaque release ou changement d’infra |

---  

## 📂 5. Structure détaillée du DEX (16 sections standards)  

| N° | Section principale | Contenu attendu (exemples) |
|---:|-------------------|----------------------------|
| 1 | **Généralités** | Objet, domaine d’application, audience cible, version du document |
| 2 | **Documents applicables et de référence** | Charte projet, normes internes, `README.md`, `phpunit.xml.dist`, documentation Symfony |
| 3 | **Terminologie** | Glossaire des acronymes (SLA, SLO, PRA, CI/CD, API Platform, CAS) |
| 4 | **Spécificités** | Fonctionnalités critiques (gestion des études, API Platform), SLA : 99,5 % Uptime, contacts clés (développeur : `John Doe <john.doe@example.com>`), matrice d’escalade |
| 5 | **Architecture** | Diagramme logique (Symfony 5 + PHP 8, PostgreSQL 13, serveur web Apache/Nginx, CAS v1.35), flux de données, infrastructure prod, PRA/PCA |
| 6 | **Serveurs** | Accès SSH, OS : Ubuntu 22.04, CPU 2 vCPU, RAM 4 GiB, stockage 30 GiB, noms DNS (`app.agile-back.local`) |
| 7 | **Application** | Packages : `api_platform`, `swiftmailer`, `nelmio_cors`, `security`; paramètres (`.env`), procédure de déploiement (GitLab CI → Docker ou rsync) |
| 8 | **Supervision et métrologie** | Outils : Monolog, Symfony Profiler, Grafana + Prometheus, alertes sur CPU > 80 %, latence API > 500 ms, erreurs 5xx |
| 9 | **Sauvegarde** | PostgreSQL dump quotidien (retention 30 jours), sauvegarde des répertoires `public/`, procédure de restauration testée mensuellement |
| 10 | **Stockage** | Répertoire `public/` (images, JS, CSS), quotas : 5 GiB, rotation des logs (`logrotate`) |
| 11 | **Inventaire des bases** | PostgreSQL 13 – DB `agile_back`, schéma `public`, utilisateurs `app_user` (rôles READ/WRITE) |
| 12 | **Flux inter‑applicatifs** | API Platform (`/api/**`) exposé en HTTPS, authentification CAS, communication avec services internes via `http://service.internal` |
| 13 | **Plan de production** | Cron : `SiteUpdateAbonnementsRunner` (00:00), `SiteUpdateAlertesRunner` (02:00), fenêtres de maintenance (dimanche 02:00‑03:00) |
| 14 | **Sécurisation des images** | Scans de vulnérabilités Docker (`trivy`), hardening PHP (`disable_functions`), gestion des secrets via `.env` et GitLab CI variables |
| 15 | **Opérations courantes** | ✅ Check‑list démarrage, ✅ Vérification des logs, ✅ Diagnostic d’erreurs communes (ex. `500 Internal Server Error`), procédures de purge du cache |
| 16 | **Opérations récurrentes** | Gestion des comptes utilisateurs, rotation des certificats CAS (90 jours), nettoyages des fichiers temporaires, audits de sécurité trimestriels |

> **Note d’adaptation** – Certaines sections (ex. « Serveurs ») peuvent être fusionnées ou détaillées selon que l’application tourne sur VM, conteneurs ou serveur dédié.  

---  

## 🗺️ 6. Diagramme Mermaid du cycle de vie du DEX  

```mermaid
graph TB
    %% Styles;
    classDef dev fill:#E3F2FD,stroke:#1976D2,stroke-width_2px;
    classDef ops fill:#E3F2FD,stroke:#1976D2,stroke-width_2px;
    classDef sec fill:#E3F2FD,stroke:#1976D2,stroke-width_2px;
    classDef maint fill:#E3F2FD,stroke:#1976D2,stroke-width_2px;
    classDef phase1 fill:#ADD8E6,stroke:#1976D2,stroke-width_2px;
    classDef phase2 fill:#90EE90,stroke:#1976D2,stroke-width_2px;
    classDef phase3 fill:#FFFF99,stroke:#1976D2,stroke-width_2px;
    classDef phase4 fill:#E6E6FA,stroke:#1976D2,stroke-width_2px;

    %% Actors;
    actor dev as "Équipe Dev / Tech Lead"
    actor ops as "Équipe Ops"
    actor sec as "Équipe Sécurité"
    actor maint as "Mainteneur"

    %% Phases;
    subgraph p1["Phase 1 – Rédaction"]
        direction TB;
        step1(("Collecte specs & architecture"))
        step2(("Rédaction des 16 sections DEX"))
    end
    subgraph p2["Phase 2 – Validation croisée"]
        direction TB;
        step3(("Revue technique (DevOps/Infra)"))
        step4(("Validation opérabilité (Ops)"))
        step5(("Validation conformité (Sécurité)"))
    end
    subgraph p3["Phase 3 – Go‑Live & Run"]
        direction TB;
        step6(("Signature & archivage versionné"))
        step7(("Intégration run‑book & supervision"))
    end
    subgraph p4["Phase 4 – Maintenance continue"]
        direction TB;
        step8(("Mise à jour à chaque release"))
        step9(("Revue trimestrielle / post‑incident"))
    end
    %% Links;
    dev -->|Alimente| step1;
    dev -->|Rédige| step2;
    ops -->|Vérifie| step3;
    ops -->|Valide| step4;
    sec -->|Valide| step5;
    step5 -->|Accord go‑live| step6;
    step6 -->|Déploiement| step7;
    maint -->|Met à jour| step8;
    step9 -.->|Boucle d’amélioration| step2;
    %% Notes;
    note right of step2;
        <b>Points de contrôle</b>\n- Accès SSH\n- Procédures rollback\n- Matrice d’escalade testée;
    end note;
    note right of step9;
        <b>Règle d’or</b>\nPas de mise en prod sans DEX à jour;
    end note;
    class dev,ops,sec,maint dev,ops,sec,maint;
    class step1,step2,step3,step4,step5,step6,step7,step8,step9 phase1,phase2,phase3,phase4;
```

---  

## 🛠️ 7. Conseils de rédaction et maintenance  

| Bonne pratique | À éviter |
|---|---|
| **Versionner** le DEX dans un dépôt Git (tags `v1.0‑dex`) | Stocker le DEX en pièce jointe email ou sur un partage non versionné |
| Rédiger en **langage clair**, orienté action (ex. « Vérifier le log `/var/log/app.log` ») | Utiliser des descriptions vagues ou purement théoriques |
| Inclure **captures d’écran**, chemins exacts et commandes (`docker exec …`) | Laisser des placeholders `[À COMPLÉTER]` en production |
| Prévoir une **revue systématique** à chaque release majeure | Considérer le DEX comme document « jetable » post‑lancement |
| **Lier** le DEX aux run‑books, tickets d’incident et procédures PRA | Isoler le DEX des outils de supervision et de ticketing |

---  

## ⚙️ 8. Adaptations contextuelles  

| Contexte | Adaptation recommandée |
|----------|------------------------|
| **Applications Cloud / Serverless** | Remplacer la section « Serveurs » par « Services managés, IAM, Config as Code, Limits/Quotas » |
| **Secteur réglementé (Santé, Finance, Public)** | Renforcer les sections Sécurité, Traçabilité, Archivage légal, Conformité RGAA/ANSSI |
| **Legacy / Monolithe** | Insister sur la dépendance OS, les patches, la compatibilité, les procédures de reprise manuelle |
| **Micro‑services / Kubernetes** | Remplacer « Inventaire BDD/Serveurs » par « Clusters, Namespaces, Helm/Manifests, Observabilité (Prometheus/Grafana/Loki) » |

---  

## 📦 9. Livrables et intégration  

| Livrable | Description |
|---|---|
| **DEX versionné** | Fichier `DEX_agile-back_vX.Y.md` (Markdown) – export possible en PDF |
| **Checklist de validation** | Tableau de signatures (Dev, Ops, Sécurité) – annexé au DEX |
| **Matrice de traçabilité** | DEX ↔ Architecture ↔ Runbooks ↔ Tickets support (ex. Jira) |
| **Intégration CI/CD** | Étape `dex:validate` – lint du Markdown, vérification des sections critiques (SLA, sauvegarde) |
| **Liens DEX dans les dashboards** | URL du DEX affichée dans Grafana/Datadog (onglet *Documentation*) |
| **Génération automatisée** | Scripts `scripts/generate-dex.sh` (extraction des paramètres depuis `config/*.yaml` et `src/Entity/*`) |

---  

## 📚 10. Mini‑glossaire  

| Acronyme | Signification |
|---|---|
| **SLA** | Service Level Agreement – engagement de disponibilité (ex. 99,5 % Uptime) |
| **SLO** | Service Level Objective – seuils mesurables (latence, taux d’erreur) |
| **PRA** | Plan de Reprise d’Activité – restauration après sinistre |
| **CI/CD** | Continuous Integration / Continuous Delivery – pipelines GitLab |
| **API Platform** | Framework Symfony pour exposer des API REST/GraphQL |
| **CAS** | Central Authentication Service – authentification unique |
| **Monolog** | Bibliothèque de logging utilisée par Symfony |
| **Docker** | Containerisation – optionnel pour le déploiement |

---  

## 📞 11. Contacts clés  

| Rôle | Nom | Email | Téléphone |
|---|---|---|---|
| **Chef de projet** | Alice Martin | alice.martin@example.com | +33 1 23 45 67 89 |
| **Tech Lead / Dev** | John Doe | john.doe@example.com | +33 6 12 34 56 78 |
| **Responsable Ops** | Marie Dupont | marie.dupont@example.com | +33 1 98 76 54 32 |
| **RSSI** | Paul Leroy | paul.leroy@example.com | +33 1 11 22 33 44 |
| **Support Niveau 2** | Sophie Benoit | sophie.benoit@example.com | +33 6 55 44 33 22 |

---  

## 📅 12. Historique des versions  

| Version | Date | Auteur | Modifications |
|---|---|---|---|
| **v1.0** | 2024‑04‑28 | Alice Martin | Version initiale – structure DEX, sections 1‑8 |
| **v1.1** | 2024‑05‑15 | John Doe | Ajout sections 9‑12, mise à jour diagramme |
| **v1.2** | 2024‑06‑10 | Marie Dupont | Intégration checklist de validation, contacts clés |
| **v1.3** | 2024‑07‑02 | Paul Leroy | Renforcement sécurité (scan Docker, rotation certs) |
| **vX.Y** | … | … | … |

---  

## 📎 Annexes  

- **Annexe A – Schéma logique de l’application** (extrait de `config/packages/api_platform.yaml` et `src/Entity/*`)  
- **Annexe B – Matrice d’escalade** (niveau 1 : support front‑office, niveau 2 : dev/ops, niveau 3 : RSSI)  
- **Annexe C – Procédure de restauration PostgreSQL** (voir `config/packages/doctrine.yaml`)  

---  

## 🔚 Conclusion  

Le présent DEX constitue la **boussole opérationnelle** de l’application **agile‑back**. En suivant rigoureusement les procédures décrites, les équipes de **développement**, **exploitation** et **sécurité** garantissent la continuité de service, la conformité aux exigences (SLA, sauvegarde, sécurité) et la capacité d’évolution du système dans le temps.  

> **« Pas de mise en production sans DEX à jour »** – règle d’or à respecter à chaque itération.  

---  

*Document généré le 2026‑04‑28 – prêt à être versionné dans le dépôt Git du projet.*